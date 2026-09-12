---
date: 2026-09-03
author: Oleg Patsay
slug: obsidian-mcp
excerpt: "How to expose an Obsidian vault to LLM clients through MCP, choose between filesystem, REST API, plugin, and CLI approaches, and design safe read/write access to a personal knowledge base."
---

# MCP for Obsidian: Connect Notes to ChatGPT, Claude, and Cursor

I keep a lot of useful context in Obsidian: work notes, article ideas, drafts, technical decisions, documentation fragments, project plans, and a personal knowledge base.

The problem is that when I work in Cursor, ChatGPT, or Claude, all of that context effectively disappears. The model can reason about almost anything in general, but it cannot see the decisions I wrote down three months ago unless I manually bring them into the conversation.

For a while, I acted as the integration layer myself.

Open Obsidian.

Find the note.

Copy the relevant fragment.

Switch back to the LLM client.

Paste it.

Ask the question.

Then sometimes copy the result back into Obsidian.

After doing this several times a day, I built a small MCP server called **Obsidian Agent** : [github.com/tenqz/obsidian-agent](https://github.com/tenqz/obsidian-agent).

It gives an LLM controlled access to an Obsidian vault. The model can search notes, read them, inspect the directory structure, and, if explicitly allowed, create or modify files.

The project itself is fairly small. The more interesting question turned out to be architectural: how should we give an LLM access to a personal knowledge base, and how much access should it receive?

That is where I want to start.

## What is MCP for Obsidian?

MCP, or Model Context Protocol, is an open protocol through which an AI application can work with external tools and data.

Without MCP, the workflow can look like this:

```text
Obsidian
   ↓
human copies text
   ↓
ChatGPT / Claude / Cursor
   ↓
LLM
```

With MCP, a server appears between the client and the data:

```text
Obsidian Vault
      ↓
  MCP Server
      ↓
ChatGPT / Claude / Cursor
      ↓
     LLM
```

The MCP server describes the tools available to the model. For example:

```text
read_note
search_notes
list_files
create_note
update_note
```

When the user asks:

> Find my PostgreSQL notes and remind me why I abandoned the previous architecture.

the model does not need the entire Obsidian vault in its context in advance.

It can search first, receive a few likely files, read the relevant notes, and only then produce an answer.

This is the main difference from manually pasting text into a chat: the LLM gets a way to retrieve the context it needs on its own.

## What can you do with Obsidian through MCP?

The most obvious use case is note search.

For example:

> Find everything I wrote about MCP.

Or:

> Show me notes that mention Redis.

But Obsidian already has search, so search alone is not a particularly strong reason to build an MCP integration.

It gets more interesting when the retrieved information can immediately become part of a larger task.

For example:

> Find all my notes about MCP and collect the unresolved technical questions.

Or:

> Read the project notes and draft a README.

Or:

> Find every mention of the project in my daily notes from the last month and summarize what happened.

Or:

> Read my old architecture notes and compare them with the current solution.

Now the model performs a short sequence of actions:

```text
task
 ↓
search
 ↓
select relevant files
 ↓
read
 ↓
analyze
 ↓
answer
```

If write access is enabled, the sequence can continue:

```text
analysis
 ↓
create or update a note
```

At this point, Obsidian gradually stops being only an archive of Markdown files.

It becomes external memory that an agent can work with.

## What are the main ways to connect MCP to Obsidian?

This is where terminology becomes confusing because several different architectures are currently described as “Obsidian MCP.”

They can roughly be divided into four approaches.

| Approach | How it works | Advantages | Limitations |
| --- | --- | --- | --- |
| Direct filesystem access | MCP reads Markdown files in the vault directly | Simple, fast, Obsidian does not need to be running | No access to Obsidian's internal application state |
| Local REST API | MCP talks to a REST API plugin inside Obsidian | Works through an application API | Requires a plugin and a running Obsidian instance |
| MCP as an Obsidian plugin | The MCP server runs inside Obsidian | Can access active note, backlinks, tags, frontmatter, attachments, and app state | Depends directly on Obsidian and its plugin environment |
| Obsidian CLI | MCP calls the official CLI | Official automation surface | Obsidian must be running |

Each approach is reasonable for a different problem.

### Direct access to Markdown files

An Obsidian vault is ultimately a directory containing Markdown files and related assets.

That means the simplest architecture can avoid the application entirely:

```text
Vault
 ↓
filesystem
 ↓
MCP Server
 ↓
LLM client
```

You can mount the vault into a Docker container, or let a local process access the directory directly.

The main advantage is that Obsidian itself can be closed.

The server does not care which editor you use to open the Markdown files.

The downside is that the MCP server does not know the internal state of the Obsidian application. It cannot tell which tab is open, which plugins are installed, or which file is currently active.

For my use case, that was a perfectly acceptable trade-off.

### Local REST API

Another popular option is to install a Local REST API plugin in Obsidian and make the MCP server an adapter between that API and the LLM.

The architecture becomes:

```text
LLM
 ↓
MCP Server
 ↓
Local REST API
 ↓
Obsidian
 ↓
Vault
```

This is how some widely used `mcp-obsidian` integrations work.

The advantage is that the integration goes through Obsidian itself.

The cost is another layer, an API key, a separate plugin, and a requirement that Obsidian be running.

### MCP as an Obsidian plugin

A tighter option is to run the MCP server inside Obsidian as a community plugin.

Now the integration can access application-specific concepts: the active note, backlinks, tags, frontmatter, attachments, and other Obsidian entities.

This is a good choice when AI needs to understand not only vault contents but also the current state of the application.

### Obsidian CLI

In 2026, another interesting option appeared: the official Obsidian CLI.

It can be used to search, read, and modify notes programmatically:

```bash
obsidian search query="MCP"
obsidian read
obsidian daily
```

For new integrations, this is particularly interesting because the layer between the MCP server and Obsidian can now be an official interface rather than a third-party REST plugin.

There is one important limitation: the CLI operates through a running Obsidian instance.

I started my own project from a simpler assumption: if the Markdown already exists on disk, I can read it directly.

## Why I chose direct filesystem access

My original task was intentionally narrow.

I did not need “AI inside Obsidian.”

I wanted access to my notes wherever I already happened to be working.

For example, I might be in Cursor writing code and suddenly need to remember a decision I recorded several months earlier.

I do not want to:

1. switch to Obsidian;
2. remember the note name;
3. search for it;
4. copy the text;
5. return to Cursor;
6. paste the context.

It feels much more natural to write:

> Look through my notes for this project and find what I wrote about this problem.

In this architecture, Obsidian remains the editor and the human interface to the knowledge base.

The vault remains storage.

MCP becomes the access layer.

The LLM client remains the interface to the model.

That is how Obsidian Agent appeared.

## How my Obsidian MCP server is structured

I deliberately kept the project small:

```text
obsidian-agent/
├── app/
│   ├── mcp/
│   │   └── server.py
│   └── vault/
│       └── service.py
├── tests/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

`VaultService` knows nothing about LLMs.

It performs ordinary file operations.

The MCP layer wraps those operations as tools visible to the client.

The model currently receives six main tools:

```text
vault_ls
vault_read
vault_write
vault_glob
vault_tree
vault_search
```

`vault_ls` lists the contents of a directory.

`vault_read` reads a Markdown file.

`vault_write` creates or overwrites a note.

`vault_glob` selects files by glob pattern.

`vault_tree` returns the vault structure.

`vault_search` performs full-text search.

The separation is intentional.

The filesystem layer can be tested without MCP, and the protocol layer stays thin.

## Fewer tools usually make model behavior more predictable

When designing an API for another developer, expressive methods are often convenient.

With an LLM, there is another factor: the model itself chooses the method.

If you expose:

```text
read_note
read_notes
get_note
get_notes
find_note
find_notes
search_note
search_notes
```

you have not created a rich API.

You have created a classification problem.

The model has to guess which tool is most appropriate every time.

That is why I try to keep tools primitive and their boundaries obvious.

Need to read a file? `vault_read`.

Need to find text? `vault_search`.

Need to select files by structure? `vault_glob`.

Need to inspect the tree? `vault_tree`.

Instead of one giant “smart” operation, the model receives several simple primitives and composes them into a sequence itself.

In a sense, the rules of good API design remain the same.

The new API consumer is simply an LLM.

## Why `glob` turned out to be unexpectedly useful

One tool I initially considered secondary was `vault_glob`.

Suppose the knowledge base is structured like this:

```text
Daily/
├── 2024/
├── 2025/
└── 2026/
```

Without globbing, the model may explore it step by step:

```text
vault_ls("")
vault_ls("Daily")
vault_ls("Daily/2026")
...
```

The larger the vault becomes, the more unnecessary calls this creates.

With glob, the model can request the relevant set immediately:

```text
Daily/2026/**/*.md
```

or:

```text
Projects/**/*.md
```

or:

```text
**/*mcp*.md
```

This reveals an important principle for agent tooling: a good tool should not only give the model context; it should also help the model reduce the search space quickly.

Loading more information is not always useful.

Sometimes the better capability is a more precise way to choose what should be loaded.

## How to connect Obsidian MCP to Cursor

For local use, I prefer `stdio`.

The MCP client launches the server process itself and communicates through stdin/stdout.

In my case, the server runs inside Docker.

Clone the repository and build the image:

```bash
git clone https://github.com/tenqz/obsidian-agent.git
cd obsidian-agent

docker build -t obsidian-agent-mcp .
```

Then add the server to the MCP configuration of the client:

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "MCP_TRANSPORT=stdio",
        "-v", "/path/to/your/vault:/vault",
        "obsidian-agent-mcp"
      ]
    }
  }
}
```

Replace:

```text
/path/to/your/vault
```

with the actual path to your Obsidian vault.

After restarting the client, the MCP tools become available.

A simple connection test is:

> Show me the structure of my Obsidian vault.

If everything is configured correctly, the model should call `vault_tree`.

Then try:

> Find all notes that mention Model Context Protocol.

That should use `vault_search`.

A more interesting request is:

> Find my notes about MCP, read them, and list the ideas I have not implemented yet.

That last example shows why the integration exists: the model performs retrieval and synthesis across the knowledge base without requiring me to assemble the context manually.

## How to connect Obsidian MCP to Claude

For Claude Desktop, the local architecture is very similar.

The client can launch an MCP server through `stdio`, so the server stays local:

```text
Claude Desktop
      ↓ stdio
Docker / MCP Server
      ↓
Obsidian Vault
```

I especially like this arrangement for a personal knowledge base.

There is no public endpoint.

No domain is required.

There is no separate OAuth configuration.

The server can access only the directory that I explicitly mount into the Docker container.

One distinction is important, however: a local MCP server does not imply a local LLM.

The MCP server may read the file locally, while the content used for the answer is still sent to the LLM provider according to the behavior and privacy rules of the particular client.

If the vault contains secrets, personal data, or work information under NDA, this distinction matters.

## What about ChatGPT?

The architecture is different here.

Cursor and Claude Desktop can launch a local MCP subprocess directly through `stdio`.

ChatGPT does not directly launch that local subprocess. It needs a remotely reachable MCP server or an appropriate protected mechanism for reaching private infrastructure.

So the architecture becomes networked:

```text
Obsidian Vault
      ↓
MCP Server
      ↓
HTTPS
      ↓
ChatGPT
```

This is exactly where the security requirements increase sharply.

The first version of my server used SSE for network connectivity and OAuth 2.1 with PKCE. While I was developing the project, the MCP specification itself changed.

In the current `2026-07-28` MCP specification, the old HTTP+SSE transport is considered legacy for new implementations, and the main direction for remote servers has moved to the current HTTP-based transport model. Dynamic Client Registration, which appeared in earlier OAuth-oriented MCP examples, is also being phased out of the core architecture in favor of newer client identity approaches.

So I no longer consider the SSE configuration from the first version of the project a good recommendation for a new installation.

Local `stdio` is still a perfectly normal option.

For a network deployment, I would build against the current MCP specification rather than copying an old tutorial.

There is also a product-side constraint: as of September 2026, custom MCP capabilities in ChatGPT depend on the plan and deployment environment. Full write/modify workflows are available in some organizational plans, while other configurations may expose a more limited set of read/search capabilities.

If ChatGPT is the target client, check the current MCP capabilities available to your account and use a server that implements the modern remote transport and appropriate authentication.

## Should AI be allowed to modify notes at all?

Giving a model read access to a knowledge base is psychologically easy.

Write access is a different level of trust.

My server has:

```text
vault_write
```

and technically the model can create or completely overwrite a note.

At first, this looks very convenient.

For example:

> Turn the notes in the Research folder into a draft article and save it in Drafts.

Or:

> Create a note containing the results of today's research.

Then another scenario appears.

The model misunderstands the request, decides to “improve” an existing file, and overwrites part of the text.

Not because AI decided to destroy the knowledge base.

Any automated action will eventually behave differently from what the user expected.

That is why I treat write access roughly like repository access for a new developer.

They can work.

But I would like to see the diff.

## How to give MCP safe access to Obsidian

A few restrictions reduce the possible damage dramatically.

### 1\. Do not mount the whole vault unless the task needs it

If the task only requires:

```text
Projects/MyProject/
```

there is little reason to expose:

```text
Personal/
Finance/
Passwords/
Private/
```

Least privilege works with AI exactly as it does in every other system.

A file the model cannot access cannot accidentally be disclosed or overwritten through this integration.

### 2\. Prefer read-only access by default

For many useful scenarios, write access is unnecessary.

Search, summarization, project-context reconstruction, and research synthesis work perfectly well with read-only permissions.

If write access becomes necessary, add it deliberately rather than making it the default.

### 3\. Put important notes under Git

Markdown works well with version control.

If an agent changes something incorrectly, you want:

```bash
git diff
```

to show exactly what happened and a normal rollback path to restore the previous version.

Version control does not make automated writes safe, but it makes mistakes much cheaper.

### 4\. Restrict writable directories

A useful model is to permit writing only into explicitly safe areas such as:

```text
Drafts/**
AI/**
Projects/Current/**
```

The model can generate drafts without receiving blanket permission to rewrite the entire knowledge base.

### 5\. Prefer patches over blind overwrites

For important existing notes, I would rather have this workflow:

```text
current content
 ↓
proposed diff
 ↓
review
 ↓
apply
```

than an automatic full-file replacement.

This is the same reason code review works better with diffs than with “trust me, I updated the repository.”

A future version of an Obsidian MCP server could expose patch-oriented operations rather than only `vault_write`.

## Are MCP and RAG the same thing?

No.

They can be used together, but they solve different problems.

A classic RAG flow looks roughly like this:

```text
documents
 ↓
index
 ↓
embeddings / search
 ↓
relevant fragments
 ↓
LLM context
 ↓
answer
```

MCP describes the interface through which an AI application can call tools and reach external data.

A model using MCP may perform:

```text
search
 ↓
inspect results
 ↓
read one file
 ↓
call another tool
 ↓
answer
```

An MCP tool can itself implement RAG internally.

For example:

```text
semantic_search(query)
```

could use embeddings and a vector database to retrieve notes by semantic similarity.

In my current Obsidian project, full-text search plus globbing is enough for many tasks. If the vault grows much larger, semantic retrieval is a natural extension.

The useful architectural question is not “MCP or RAG?”

It is:

> Which operations should the model be allowed to perform, and how should each operation find the data it needs?

MCP answers the first part at the interface level.

RAG may answer part of the second.

## MCP or an AI plugin for Obsidian?

If your entire workflow happens inside Obsidian, an AI plugin may be completely sufficient.

My situation is the opposite.

My center of work may be Cursor, Claude, ChatGPT, a terminal, or another future MCP-compatible client.

I do not want to rebuild the same vault integration separately for every interface.

That is why the architecture I prefer looks like this:

```text
             Cursor
               ↑
               │
Obsidian → MCP ┼→ Claude
               │
               ↓
             ChatGPT
```

Obsidian remains the source of knowledge.

MCP becomes the reusable access boundary.

Clients can change independently.

This decoupling is the main reason the protocol is interesting to me.

## Which scenarios turned out to be useful in practice?

The most valuable requests are not “search for this exact word.” Obsidian already does that.

They are tasks that combine retrieval with reasoning.

### Recover the reason behind an old decision

> Find my notes about the Redis migration and explain why I ultimately chose PostgreSQL.

The value is not the search itself. The model can combine several pieces of context into the decision trail I no longer remember.

### Reconstruct project context

> Read the notes in Projects/MyProject and give me a short description of the current architecture.

This is useful after a long break from the project.

### Find unfinished thoughts

> Find notes about MCP that contain questions or TODOs and collect them into one list.

The knowledge base unexpectedly becomes a source of tasks.

### Work with daily notes

> Find every mention of the project in August and build a timeline of what happened.

Individual daily notes are not ideal for this kind of synthesis. For a model, combining them is natural.

### Prepare articles

> Find my notes about vector search, group the ideas, and propose an article structure.

Instead of remembering where separate pieces of research are stored, I can start from structured material.

## What I learned from building my own Obsidian MCP

Initially, I thought I was writing a small integration.

Over time, I realized that I was more interested in the idea of context itself.

A modern LLM knows an enormous amount about the world and almost nothing about my specific work.

It does not know which architectural decision the team made three months ago.

It does not know which experiment already failed.

It does not know what ideas I wrote down yesterday.

It does not know why a strange project constraint exists even though it looks pointless from the outside.

Every new conversation begins with something close to amnesia.

We try to solve this with huge context windows, RAG, memory, MCP, and many other approaches, but the fundamental task remains the same:

> Give the model the right context at the right time.

Simply putting everything into the prompt is not a solution.

The larger the knowledge base becomes, the less important the maximum context size is compared with the model's ability to select what it actually needs.

That is why the most boring parts of the project became so important to me:

```text
search
glob
tree
read
```

They do not make the model smarter.

They let it figure out what it needs to know before answering.

## A personal knowledge base gradually becomes infrastructure

I used to think of Obsidian as a good archive.

Write down a thought.

Find it a month later.

Sometimes connect it to another note.

LLMs changed that relationship.

If AI becomes a permanent part of the workflow, accumulated context stops being merely a collection of Markdown files.

It contains the history of decisions.

Project context.

Research results.

Mistakes.

Drafts.

Things I already understood once and do not want to understand from scratch again.

In that form, a personal knowledge base becomes another layer of engineering infrastructure.

Not memory inside the model, but external memory the model can access.

To me, this is more interesting than the idea of an “AI that knows everything.”

Modern models already have enormous amounts of general knowledge.

The most valuable information is often not on the public internet.

It is in our repositories, documentation, conversations, notes, and decision history.

The main challenge for the next generation of AI tools may therefore not be generating even more text.

It may be giving models safe access to the context that already exists.

I started with the simplest version I could: an ordinary directory of Markdown files and six MCP tools.

Obsidian remained Obsidian.

The LLM remained an LLM.

But the developer who spent all day pressing Ctrl+C and Ctrl+V almost disappeared from the space between them.

## Links

- [Obsidian Agent on GitHub](https://github.com/tenqz/obsidian-agent)
- [Model Context Protocol documentation](https://modelcontextprotocol.io/)
- [Obsidian](https://obsidian.md/)
- [What Is MCP (Model Context Protocol) and How Does It Work?](/model-context-protocol-mcp)
- [Context Engineering: What It Is and How to Manage LLM Context](/context-engineering)

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
