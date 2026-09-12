---
date: 2026-09-04
author: Oleg Patsay
slug: context-engineering
excerpt: "Context Engineering is the design of an LLM's working memory: what to put into it now, what to keep outside, and when to retrieve, compress, isolate, or persist information."
---

# Context Engineering: How to Manage Context for LLMs

For the last several years, much of the discussion around LLMs has focused on Prompt Engineering. Formulate the task correctly, write a good system prompt, add examples, specify the output format, and the model will produce the result you want. For simple scenarios, that was often enough. One request, one prompt, one answer — most of the work happens inside the text sent to the model.

Agents make the problem more complicated. The model receives conversation history, search results, documentation, the list of available tools, tool outputs, information about the user, task state, and another dozen pieces of context. If the agent runs for a long time, all of this accumulates. Eventually you notice something strange: the prompt seems fine, the model is strong, the necessary information is somewhere in the input — and response quality still degrades.

This is where the term **Context Engineering** becomes useful.

I think of it as designing the working memory of an LLM.

Not only what instruction to write, but what the model should see at the next inference step, what should remain outside the context window, what should be retrieved on demand, what should be compressed, what should be persisted, and what should be removed.

Anthropic has described the goal as finding the optimal set of tokens for the next step. Vercel frames a similar problem as deciding what should enter the next context window and how it should be managed over time.

The important shift is simple: the prompt is only one part of the input system.

## What is actually inside an LLM context?

A modern agent's context can include much more than the user's latest message.

For example:

```text
Context
├── System instructions
├── User request
├── Conversation history
├── Examples
├── Retrieved documents
├── Memory
├── Tool definitions
└── Tool results
```

From the model's point of view, the final input is still tokens.

But from the application's point of view, these tokens come from different sources, have different life cycles, and should be managed differently.

System instructions may be stable across the whole session.

Retrieved documents may be useful for one step only.

A tool result can become obsolete after the next action.

A user preference may need to survive for months.

A huge test log may be relevant only until we understand why the build failed.

The fact that all of this can technically fit into one context window does not mean it should all be sent every time.

## Why a good prompt is no longer enough

Imagine a prompt for code review:

> Review this change. Pay attention to possible bugs, architectural problems, and backward compatibility.

The instruction is reasonable.

But without the diff, relevant files, project conventions, architectural constraints, and the original task, the review will be generic.

Now take the opposite extreme. Give the model the whole repository, all architecture documents, the complete conversation history, fifty tool definitions, and twenty large tool outputs.

The necessary information is definitely present.

But it is buried inside a large amount of irrelevant or stale information.

The problem has shifted from:

> How should I phrase the request?

To:

> What does the model need to know at this exact step?

That is the central Context Engineering question.

## A large context window does not mean you should put everything into it

Large context windows are useful, but they do not remove the need for selection.

Anthropic uses the term **context rot** for the way performance can degrade as a context becomes larger and more cluttered. The model still has a finite attention budget, even when the absolute token limit is large.

A human analogy is simple.

Imagine trying to work with twenty browser tabs, five IDE windows, several documentation pages, Slack, an issue tracker, and three terminal logs open in front of you at once.

Technically, all the information is available.

That does not mean your thinking becomes better.

A large context can contain:

- irrelevant documents;
- stale decisions;
- conflicting versions of documentation;
- repeated information;
- huge JSON responses from tools;
- old intermediate conclusions that are no longer true.

The goal is therefore not to maximize the amount of information visible to the model.

The goal is to maximize the amount of useful information for the next decision.

## How to build context

I find four actions useful as a mental model:

```text
WRITE
SELECT
COMPRESS
ISOLATE
```

### WRITE

Put stable, known information into the context directly.

This can include system instructions, project-wide rules, the current task, explicit constraints, and information that is definitely required for the next step.

### SELECT

Retrieve relevant information from external sources.

This is where search, RAG, vector search, SQL queries, file-system tools, and MCP tools appear.

The full knowledge base stays outside the context. Only the relevant fragments enter.

### COMPRESS

Reduce accumulated context while preserving the information needed for future work.

Instead of keeping a 20,000-line test log forever, keep the reason for the failure and the current unresolved state.

Instead of preserving fifty tool calls verbatim, keep the decisions and open questions they produced.

### ISOLATE

Keep some work outside the main context entirely.

A subagent can investigate an independent module and return only its conclusion.

A large document can remain in storage until a specific section is needed.

A tool result can be referenced by an ID rather than expanded into the prompt immediately.

The important point is that Context Engineering is not only about adding information.

A large part of the work is deciding what not to add.

## Retrieval: bring information in when it is needed

RAG became popular largely because it solves a straightforward problem: the external knowledge base can be large while the model receives only the pieces relevant to the current question.

Agents extend this idea further because retrieval can happen during the task, not only before the first model call.

Anthropic often describes this as **just-in-time context**.

The model can first see lightweight references: file paths, IDs, metadata, a directory tree, or search results. Then it reads the full content only when necessary.

This is how my Obsidian MCP workflow works:

```text
vault_tree
 ↓
vault_search
 ↓
vault_read
 ↓
relevant notes
 ↓
LLM
```

The model first sees the structure or performs a search, then reads only a few documents that actually matter. The other thousands of Markdown files remain on disk.

This also shows the difference between a context window and a knowledge base.

The knowledge base may be huge.

The context for a particular step should usually stay comparatively small.

## Memory lives outside the model

The word `memory` creates some confusion in AI systems. It can sound as if the model itself remembers a user or previous work somewhere internally.

In most practical architectures, memory is much more mundane: information is stored externally and injected into the context again on a future call.

It is useful to separate at least three levels.

There is the current working memory: the context window of this particular inference.

There is session state: recent conversation history and results of recent actions.

And there is long-term memory: data stored in a database, vector store, files, or a dedicated memory service.

Suppose an agent spends several hours migrating a project and makes an important architectural decision. You can leave that decision only inside the conversation history. As long as the history fits into context, everything works. Later, the conversation is compacted or a new session starts, and the decision disappears.

Another option is to persist it explicitly:

```text
Decision:
Store refresh tokens separately from access tokens.
Rotate refresh tokens on every refresh.
```

Now the decision can be retrieved later regardless of what happened to the original conversation.

This leads to a useful rule:

If information must survive a context reset, move it outside the context window.

A memory subsystem is therefore not magic model memory. It is storage plus retrieval rules plus update rules.

## What to do with long-running sessions

Long-running agents accumulate history quickly.

A coding agent can search files, read documentation, run tests, inspect logs, make edits, run tests again, ask another agent for analysis, and repeat the cycle many times.

If every intermediate artifact remains in context forever, the input eventually becomes both expensive and noisy.

Compaction is the obvious answer, but naive summarization can lose exactly the constraint that later turns out to matter.

Structured state is often safer than a free-form summary.

For example:

```text
Goal:
Add refresh token rotation.

Done:
- changed Token model
- added refresh_tokens table
- created migration

Decisions:
- access token remains stateless
- refresh tokens are stored in the database

Open:
- verify concurrent refresh behavior
- add integration tests
```

This is much more useful for the next step than fifty pages of chronological tool history.

The question during compaction should not be “how do I make the context shorter?”

It should be:

> What must survive so that the next decision is still correct?

Anthropic's work on long-running agents points in the same direction: compaction, structured notes, and separation of work across agents become increasingly important as sessions grow.

## Tools are context too

Tool definitions are easy to overlook because they do not look like ordinary conversation text.

But the model sees their names, descriptions, and schemas. They consume context and, more importantly, create a choice space.

If an agent has one hundred possible tools, it has one hundred actions to reason about before every step.

For a code task, the useful tool set may be only:

```text
read_file
search_code
run_tests
git_diff
```

The model does not need to see:

```text
send_email
create_calendar_event
search_crm
generate_invoice
```

just because those tools exist somewhere in the application.

Vercel describes tool context in essentially these terms: tool names, descriptions, and schemas are part of what the model has to reason over.

This is one reason I prefer a small set of non-overlapping primitives in MCP servers.

For an Obsidian vault, operations such as:

```text
vault_search
vault_read
vault_glob
vault_tree
```

create clearer boundaries than twenty subtly different note-reading functions.

A smaller tool space is itself a form of Context Engineering.

## A coding-agent example

Suppose the task is:

> Add support for refresh tokens.

A poor approach is to dump the entire repository, all documentation, and the full Git history into the model before it does anything.

A more useful sequence is progressive:

```text
Task
 ↓
Repository tree
 ↓
Search "auth"
 ↓
Relevant files
 ↓
Existing tests
 ↓
Architecture decisions
 ↓
LLM
```

The agent starts with the task and a lightweight view of the project.

Then it searches for authentication-related code.

Then it reads only the relevant files and existing tests.

If there are stored architecture decisions, it retrieves those too.

After making a change and running tests, it does not need to preserve every line of test output. It needs the result and, if something failed, the reason that matters for the next step.

If the task requires investigating an independent module, that investigation can happen in a separate agent context and return a compact conclusion.

The working area is assembled progressively instead of being preloaded with the whole world.

## How Context Engineering, RAG, and MCP fit together

These terms describe different parts of one system.

Prompt Engineering is about instructions and prompt structure.

RAG selects relevant information from an external source and places it into context.

Memory stores state across calls and sessions.

MCP standardizes access from an AI application to external data and tools.

All of them can be seen as mechanisms inside the broader Context Engineering problem:

```text
Context Engineering
│
├── Prompt Engineering
├── RAG / Retrieval
├── Memory
├── MCP / Tools
└── Compression
```

Suppose a user asks an agent about internal company documentation.

Through MCP, the agent receives a tool called `search_docs`.

Inside that tool, a vector search against Qdrant may run.

The returned documents are added to the model's context.

Several steps later, an important conclusion is stored in memory.

Old tool outputs are removed during compaction.

All of these mechanisms serve the same higher-level goal: give the model the right information for the next decision.

## How to tell whether the problem is context

When an agent behaves badly, the first instinct is often to modify the prompt, change the model, or adjust temperature.

Sometimes the real problem is what the model is seeing.

Common symptoms include:

- repeating actions it already performed;
- forgetting a decision made earlier;
- choosing the wrong tool;
- using stale documentation;
- contradicting a project rule that exists somewhere in the input;
- repeatedly searching for information that was already found;
- becoming worse as the session gets longer.

Before changing the prompt, inspect the actual model request.

What information is present?

Which version of the document was retrieved?

How much history is included?

Are old tool results still there?

Does the model see tools that are irrelevant to the task?

Do system instructions, memory, and retrieved documents contradict each other?

In a serious agent system, tracing the full context payload and the provenance of each piece of information becomes an observability requirement.

Without that, debugging the model is partly guesswork.

## How I would design context

I would start with the smallest set of information that is definitely required.

Then I would separate stable context from dynamic context.

Stable information includes core system instructions and a small number of project-wide rules.

Dynamic information — documents, history, user data, search results, and tool outputs — should be fetched when needed.

Then I would decide what has to persist beyond one step or one session: architectural decisions, user preferences, long-running task state, and important facts.

I would explicitly clean up large tool outputs, debug logs, obsolete search results, and already-solved intermediate questions.

I would define what compaction must preserve instead of letting summarization decide arbitrarily.

And I would measure more than token count.

Useful metrics can include:

- task success rate;
- retrieval accuracy;
- wrong-tool rate;
- repeated steps;
- quality over long sessions;
- latency and cost;
- how often important constraints are lost after compaction.

At that point, Context Engineering stops being a prompt trick and becomes system architecture.

## What Context Engineering does not fix

Good context management is not a universal cure.

A retrieval system can still return the wrong documents.

Memory can preserve a wrong conclusion.

A tool can implement bad business logic.

A perfectly assembled context does not turn a weak model into a stronger one.

Context Engineering simply improves the information environment in which the model makes the next decision.

That is one part of the system, not the entire system.

## Instead of a conclusion

Large context windows do not make context selection less important.

They make it easier to postpone thinking about selection.

For a simple chatbot, that may be fine. For a long-running agent with tools, memory, a knowledge base, and multiple workflows, context becomes an architectural problem.

You have to decide how information is searched, assembled, stored, compressed, and isolated.

Prompt Engineering does not disappear. It becomes one component of a larger discipline.

The skill gradually shifts from “how do I talk to the model?” to “which part of the world should the model see right now?”

That question seems likely to become more important as agents get longer-lived, more autonomous, and more deeply integrated into real systems.

## What to read next

- [What Is MCP (Model Context Protocol) and How Does It Work?](/model-context-protocol-mcp)
- [MCP for Obsidian: How to Connect Your Notes to ChatGPT, Claude, and Cursor](/obsidian-mcp)
- [Vector Search and Embeddings: How Semantic Search Works](/vector-search-embeddings)

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
