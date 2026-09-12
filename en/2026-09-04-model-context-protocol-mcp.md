---
date: 2026-09-04
author: Oleg Patsay
slug: model-context-protocol-mcp
excerpt: "MCP does not make models smarter. It standardizes how AI applications connect to files, databases, APIs, and other external systems."
---

# What Is MCP (Model Context Protocol) and How Does It Work?

I came to MCP for a very practical reason: I got tired of manually copying notes from Obsidian into an LLM, so I decided to write a small server between them. While building it, I started to understand why there is so much discussion around Model Context Protocol. MCP itself does not make models smarter or give them fundamentally new abilities. Its job is much more boring: standardize the way AI applications connect to files, databases, APIs, and other external systems.

And that boring part turns out to be important.

Without a common protocol, every AI client has to build its own integration with every external system. Cursor needs one GitHub integration, Claude another, ChatGPT a third. The same story repeats for PostgreSQL, Obsidian, Jira, internal APIs, and everything else.

Eventually you get an integration zoo.

MCP tries to create a common boundary.

## Why MCP was needed in the first place

Without a shared protocol, integrations tend to look like this:

```text
Cursor → GitHub
Cursor → PostgreSQL
Cursor → Obsidian

Claude → GitHub
Claude → PostgreSQL
Claude → Obsidian
```

Every client knows how to talk to every system.

MCP inserts a standardized layer between them:

```text
Cursor  ─┐
Claude  ─┼── MCP ── GitHub
ChatGPT ─┘         ├─ PostgreSQL
                   └─ Obsidian
```

Now each AI application needs to understand one protocol, and each external system can expose its capabilities through an MCP server.

The usual analogy is USB-C. USB-C does not make a monitor better, a laptop faster, or a hard drive more reliable. It gives different devices a common way to connect.

MCP is similar.

It does not solve authentication for you.

It does not repair a bad API.

It does not design your business logic.

It standardizes the connection boundary.

## How MCP is structured

At the conceptual level, there are three main roles: Host, Client, and Server.

The **Host** is the AI application the user works with: Cursor, Claude Code, VS Code, a custom agent application, and so on. The model itself is not the Host.

Inside the Host, there are one or more **MCP Clients**. A client maintains the connection to a particular MCP Server.

The **MCP Server** exposes external capabilities.

The structure looks roughly like this:

```text
                    ┌→ MCP Client → GitHub MCP
AI application ─────┼→ MCP Client → PostgreSQL MCP
                    └→ MCP Client → Obsidian MCP
```

The server can be local or remote.

For example, my Obsidian server works with a Markdown vault on disk. It exposes operations for searching notes, reading files, inspecting the directory tree, and, if allowed, writing notes.

The Host decides which servers are available, which data can be passed to the model, and which operations are permitted.

An MCP server does not automatically receive the entire conversation or unrestricted access to the model's context.

It exposes a defined interface.

## Tools, Resources, and Prompts

MCP defines several kinds of capabilities. The three most visible are Tools, Resources, and Prompts.

### Tools

Tools are actions the model can invoke.

Examples:

```text
create_issue
run_query
vault_search
vault_read
```

A tool usually has a name, description, and input schema.

For example:

```text
search_notes(query: string)
```

Then a user can ask:

> Find everything I wrote about MCP.

The model can decide that `search_notes` is the right operation and call it with `MCP` as the query.

### Resources

Resources are data the server exposes for reading, usually addressable through URIs.

Conceptually, Tools answer “what can I do?” while Resources answer “what can I read?”

A server might expose a document, configuration file, database schema, or another piece of structured data as a Resource.

### Prompts

Prompts are reusable interaction templates exposed by the server. They are closer to prepared workflows that a user can invoke explicitly.

For example, a server could expose a code-review prompt that knows which project context should be loaded.

The rough distinction is:

| Capability | Purpose | Example |
| --- | --- | --- |
| Tool | Perform an action | Create an issue |
| Resource | Provide data | Read a document |
| Prompt | Provide a prepared workflow | Code review |

In practice, I mostly work with Tools because they map naturally to agent actions.

## What happens after a user request

Suppose the user asks:

> Find my notes about MCP and prepare a short summary.

The AI application already knows that the connected server exposes `vault_search` and `vault_read`.

The model can first call:

```text
vault_search("MCP")
```

The server returns something like:

```text
Projects/mcp.md
Ideas/ai-tools.md
Daily/2026-08-15.md
```

The interesting part comes next. The model can look at the result and decide that a list of files is not enough. It then calls `vault_read` for one or more documents, receives their contents, and only then answers the user.

The flow is roughly:

```text
User
 ↓
AI application
 ↓
LLM
 ↓
selects a tool
 ↓
MCP Client
 ↓
MCP Server
 ↓
external system
 ↓
result
 ↓
LLM
 ↓
User
```

The model does not receive some magical “Obsidian access.” It receives a limited set of operations that someone designed and allowed in advance.

This is where tool design becomes much more important than it first appears. Give the model ten clearly separated operations and it can usually compose them into a reasonably predictable sequence. Give it forty nearly identical methods with vague descriptions and it has to guess which one the developer intended every time.

When I built my MCP server, this became one of the most useful observations. The instinct is to create a separate tool for every scenario, but a small set of good primitives often works better.

It is a familiar API-design problem. The consumer of the API just happens to be an LLM now.

## How does the client know what the server can do?

An MCP client can ask the server for the tools it exposes.

Each tool is described with metadata such as its name, description, and JSON Schema for input.

Conceptually, the server might expose:

```json
{
  "name": "search_notes",
  "description": "Search notes by text",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string"
      }
    },
    "required": ["query"]
  }
}
```

The model sees this description through the Host and can choose the tool when it appears relevant.

Descriptions matter. A vague tool name and vague description create ambiguity for the model just as a bad API creates ambiguity for a developer.

Under the hood, MCP uses JSON-RPC 2.0 messages. A tool call can conceptually look like this:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_notes",
    "arguments": {
      "query": "MCP"
    }
  }
}
```

In normal application code, an SDK handles most of that plumbing.

One detail is worth mentioning because MCP has changed quickly. In the `2026-07-28` specification, the old mandatory `initialize` / `initialized` handshake and protocol-level sessions were removed from the core protocol. Requests are designed to be self-contained, and optional discovery mechanisms such as `server/discover` cover some scenarios that previously relied on session negotiation.

So if you read an older MCP tutorial centered around `Mcp-Session-Id`, a mandatory initialization exchange, or the old HTTP+SSE transport, it may describe an earlier version of the protocol rather than the current architecture.

## Local and remote MCP servers

MCP works both locally and over the network.

For local tools, `stdio` is often the simplest transport.

The Host launches the MCP server as a local process and communicates through stdin and stdout:

```text
Cursor
 ↓
stdio
 ↓
MCP Server
 ↓
Obsidian Vault
```

This has a useful property: there is no public port, domain, HTTPS certificate, or separate network authentication layer to configure.

That makes `stdio` a natural choice for local files, IDE integrations, shell tools, and personal knowledge bases.

Remote MCP is a different infrastructure problem.

A remote server usually sits behind HTTP and now needs the things any network service needs: HTTPS, authentication, authorization, rate limiting, monitoring, and operational controls.

The current MCP protocol core is intentionally more stateless than older versions, which also makes ordinary web infrastructure and load balancing easier to reason about. The earlier HTTP+SSE approach is considered legacy for new deployments.

A rough comparison:

|  | Local MCP | Remote MCP |
| --- | --- | --- |
| Runs | On the user's machine | On a server / cloud infrastructure |
| Typical transport | stdio | HTTP |
| Authentication | Often unnecessary at the protocol boundary | Usually required |
| Typical data | Files, IDE state, local tools | CRM, APIs, databases, company systems |
| Main concern | Local permissions | Network security and multi-user access |

Remote MCP becomes interesting when it acts as a reusable AI infrastructure layer for several users or clients.

## MCP, Function Calling, APIs, and RAG solve different problems

These concepts are often mixed together because they all appear in the same AI systems.

They are not interchangeable.

### MCP and Function Calling

Function Calling is usually a mechanism through which an application tells an LLM which functions it may request.

Conceptually:

```text
LLM
 ↓
functions provided by the application
```

MCP standardizes where those external capabilities can come from and how an AI application talks to their provider.

```text
AI application
 ↓
MCP
 ↓
external systems
```

The two work together perfectly well. A Host may discover tools through MCP and then present them to a model through the model provider's tool-calling or function-calling interface.

MCP is not a replacement for Function Calling. They live at different boundaries.

### MCP and ordinary APIs

The API story is similar. MCP does not replace REST, GraphQL, gRPC, or an internal company RPC protocol.

An MCP server is often simply an adapter over an existing API.

A CRM can continue exposing REST while the MCP server turns it into a handful of operations that are convenient for an AI client, such as:

```text
find_customer
create_lead
get_deals
```

The architecture becomes:

```text
LLM
 ↓
MCP
 ↓
MCP Server
 ↓
REST API
 ↓
CRM
```

The CRM does not need to know anything about LLMs.

MCP merely creates another interface on the other side.

### MCP and RAG

RAG solves a different problem again.

In a classic retrieval pipeline, the system receives a query, finds relevant documents, and adds them to the context before generation:

```text
query → retrieval → documents → context → LLM
```

With MCP, the model may decide to call a search tool, inspect the result, read one specific document, and then call another tool if necessary.

The MCP server itself can still use embeddings, a vector database, and conventional RAG internally.

For example, a tool called `semantic_search` may query Qdrant and return relevant fragments.

So “MCP or RAG?” is usually the wrong question.

MCP can be the interface through which an agent reaches a retrieval system.

## MCP and AI agents

MCP is also not an agent framework.

An agent decides what to do, in what order, whether another step is needed, and when the task is complete.

MCP standardizes the interface through which it can reach external capabilities.

A simple way to remember the distinction is:

> The agent decides what to do. MCP standardizes the interface through which it can do it.

This is why MCP is particularly useful for agents. An agent may need to work with an issue tracker, repository, documentation, CI, database, CRM, and internal services in one workflow. A shared protocol reduces the number of custom integration layers around that orchestration.

But MCP itself does not plan, reason, or create an agent loop.

## Where MCP actually makes sense

For developers, the use cases are fairly obvious:

- repositories;
- project documentation;
- issues and pull requests;
- CI results;
- logs;
- local development tools.

For a personal knowledge base, MCP can expose Obsidian or another document store to several different AI clients.

Inside a company, it can sit in front of:

- PostgreSQL or BigQuery;
- CRM and ERP;
- internal documentation;
- task trackers;
- analytics systems;
- internal APIs.

The key benefit appears when there is a reusable boundary between AI applications and external capabilities.

If you have one fixed backend endpoint that always calls one model to perform one function, such as:

```text
generate_description(product)
```

you may not need MCP at all.

A direct integration is often simpler.

MCP becomes more useful when several AI clients need access to several systems, or when you want the external capability contract to be reusable independently of a specific model provider.

## Security did not disappear

MCP tools may perform real actions.

There is a huge difference between:

```text
search_docs
```

and:

```text
delete_customer
transfer_money
vault_write
```

The protocol does not decide which operations are safe.

That remains an architecture problem.

The usual controls still apply:

- least privilege;
- authentication;
- authorization;
- audit logging;
- explicit user confirmation for dangerous operations;
- narrow tool contracts;
- restricted data scope.

If an agent only needs to search notes, it does not need permission to overwrite or delete them.

For my Obsidian integration, write access is something I treat separately from read access. A useful design may include a read-only mode, permitted directories, Git versioning, diffs, or confirmation before replacing a file.

The MCP specification itself emphasizes understandable tool calls and user control around sensitive actions. Remote authentication has also evolved; in the `2026-07-28` generation of the specification, the direction moved away from earlier Dynamic Client Registration patterns toward mechanisms such as Client ID Metadata Documents.

A server should be treated as a trust boundary.

Its tool descriptions and returned data can influence what the model does next. A standardized interface is not automatically a safe interface.

## MCP does not design the architecture for us

After spending time with MCP, I increasingly see it as a fairly boring infrastructure protocol.

I mean that positively.

It does not fix a bad API.

It does not decide how granular a tool should be.

It does not implement your business rules.

It does not stop a model from hallucinating.

It does not guarantee that the model will choose the right action.

What it does is standardize a useful boundary between AI applications and external capabilities.

That lets us reuse integrations across clients and reason about them as infrastructure instead of rebuilding every connection inside every AI product.

The interesting engineering questions remain ours:

What capabilities should be exposed?

How large should each tool be?

Which actions require confirmation?

Which data may leave the system?

Where does deterministic automation end and human responsibility begin?

MCP does not remove those questions.

It gives them a cleaner interface.

## Frequently asked questions

### What is MCP in simple terms?

MCP is an open protocol that standardizes how AI applications access external data and tools. Through it, an AI client can search documents, read files, call APIs, or invoke explicitly allowed actions exposed by an MCP server.

### What is an MCP server?

An MCP server is a program or service that exposes capabilities to an MCP client. Those capabilities can include Tools, Resources, and Prompts.

### How is MCP different from an API?

An API is the interface of a particular system. MCP is a standardized boundary designed for AI applications to discover and use external capabilities. In many architectures, an MCP server simply wraps an existing REST, GraphQL, or RPC API.

### How is MCP different from Function Calling?

Function Calling is usually the model-provider mechanism through which an application exposes functions to an LLM. MCP standardizes how the application obtains external tools and data. They are commonly used together.

### How is MCP different from RAG?

RAG is a retrieval pattern for finding relevant information and adding it to model context. MCP is a protocol for accessing external systems. A retrieval system can be exposed through an MCP tool.

### Is MCP an agent framework?

No. MCP does not implement planning, reasoning loops, or task completion logic. It provides an interface to external capabilities that an agent may use.

### Is MCP only for local tools?

No. Local `stdio` servers are common, but MCP also supports remote network services.

### Do I always need MCP for an AI integration?

No. A simple application with one model and one fixed backend workflow may be easier to implement directly. MCP becomes valuable when the capability needs to be reused across multiple AI clients or when the number of connected systems grows.

## What to read next

- [MCP for Obsidian: How to Connect Your Notes to ChatGPT, Claude, and Cursor](/obsidian-mcp)
- [Context Engineering: What It Is and How to Manage LLM Context](/context-engineering)
- [Vector Search and Embeddings: How Semantic Search Works](/vector-search-embeddings)

Official specification and documentation: [Model Context Protocol](https://modelcontextprotocol.io/).

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
