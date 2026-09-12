---
date: 2026-09-04
author: Oleg Patsay
slug: ai-in-legacy-systems
excerpt: "Keep the legacy application as the system of record and add AI beside it as a new layer: adapters, read-only scenarios, shadow mode, and gradual expansion of capabilities."
---

# How to Introduce AI into a Legacy System Without Rewriting It

When AI comes up in the context of an old project, there is an immediate temptation to solve two problems at once. If the system was written ten years ago, is poorly documented, still runs on old PHP or Java in places, and contains modules nobody fully understands anymore, why not rewrite it on a modern stack first and then add AI on top of the new architecture?

It sounds logical.

It also sounds very similar to how countless legacy rewrites started long before LLMs existed.

The problem is that an old production system contains much more than old code. It contains years of business knowledge: conditions added after incidents, stored procedures nobody wants to touch, strange cron jobs, integration workarounds, implicit contracts with other teams, and behavior that may no longer be documented anywhere.

AI does not create a new requirement to rewrite all of that.

In many cases, the safer architecture is almost the opposite: keep the legacy system as the system of record and introduce AI beside it as a separate layer.

## First decide what AI is supposed to do

“Implement AI” is not a useful engineering task. It is roughly as specific as “implement a database.”

Start with one workflow.

A support operator spends twenty minutes reconstructing customer history before writing a reply.

A developer searches through an old module, several repositories, and documentation to understand why a piece of code exists.

A manager manually combines information from five internal systems.

A user wants to search transaction history in natural language.

These are concrete problems.

The safest first use cases are usually informational rather than operational: search, summarization, classification, drafting, explanation, and recommendation.

The architecture can initially be very simple:

```text
Legacy system
      ↓
existing data
      ↓
AI layer
      ↓
search / summary / recommendation
      ↓
human
```

If the model is wrong, a human sees the result before anything changes.

If the model is unavailable, the core legacy system still works.

That is a very useful starting property.

## The most expensive part of legacy is usually not the code

When people talk about modernizing a legacy system, code is the most visible problem. The harder problem is often understanding the system well enough to know what can be changed safely.

Old applications accumulate business capabilities and dependencies that are distributed across source code, database schemas, stored procedures, jobs, configuration, documentation, and people's memory.

This is one of the places where AI can be useful before it becomes part of the product at all.

It can help:

- navigate a large codebase;
- find similar business logic in different modules;
- map dependencies;
- summarize old components;
- connect code with documentation;
- identify potentially dead areas;
- explain migrations and database schemas;
- build a rough capability map;
- trace integrations between systems.

This is close to the direction described in guidance on generative AI for legacy modernization from organizations such as Thoughtworks and AWS: understanding the existing system is itself a major modernization task.

But one rule is important.

If an LLM says “this method calculates commission,” treat that as a hypothesis, not as the specification.

Validate it against code, data, tests, runtime behavior, and people who know the domain.

AI can accelerate archaeology. It cannot magically turn undocumented behavior into truth.

## AI does not have to live inside the legacy application

Imagine a classic monolith:

```text
┌────────────────────────────┐
│        Legacy App          │
│                            │
│ Billing Users Orders ...   │
└────────────────────────────┘
```

For a small experiment, adding an LLM SDK directly to the application may be completely reasonable.

The problem begins when the AI-related part grows.

Soon there are prompts, model routing, embeddings, vector search, agent state, tools, token budgets, retries, evaluations, guardrails, and provider-specific behavior.

That changes much faster than the legacy core.

At that point, I prefer a separate boundary:

```text
                ┌─────────────────┐
                │    AI Layer     │
                │                 │
                │ LLM             │
                │ RAG             │
                │ Agents          │
                │ MCP / Tools     │
                └────────┬────────┘
                         │
                   Adapter / API
                         │
                ┌────────▼────────┐
                │   Legacy App    │
                └─────────────────┘
```

The legacy system continues to own what it already does well: business rules, transactions, authoritative data, and existing workflows.

The AI layer owns the probabilistic part.

AWS's Agentic AI guidance describes a similar separation: existing systems are exposed through adapters and abstraction interfaces, while the agent sees a constrained tool contract instead of knowing the internal legacy protocols directly. Rate limiting and access control can live at that boundary as well.

This separation is useful for another reason: AI infrastructure changes much faster than an ERP, billing system, or old monolith. Models, SDKs, providers, and agent frameworks may change several times while the core business system remains untouched.

## The adapter matters more than the model

Suppose the old CRM exposes something like:

```text
/customer/get.php?id=123
```

Or maybe SOAP.

Or XML-RPC.

Or a stored procedure.

The agent does not need to know any of that.

From its perspective, the interface can be:

```text
get_customer(customer_id)
find_orders(customer_id)
create_support_note(customer_id, text)
```

The adapter hides the legacy mechanics:

```text
AI Agent
   ↓
get_customer()
   ↓
Adapter
   ↓
SOAP
   ↓
Legacy CRM
```

This is essentially an anti-corruption layer: the new part of the system does not inherit every historical protocol and data structure from the old part.

I would expose only the operations needed for the current workflow rather than trying to wrap the entire legacy application at once.

If several AI clients need the same capabilities, MCP can become the standardized boundary:

```text
Claude ──┐
Cursor ──┼→ MCP Server → Adapter → Legacy
Agent  ──┘
```

The internal system does not need to know anything about MCP, an LLM, or an agent.

It keeps serving its existing application contract.

## Start with read, then add write

I find it useful to think about AI integration as several levels of risk.

First, AI only reads information.

Then it proposes a change.

Then it performs a change after explicit approval.

Only after that do some narrow operations become autonomous.

Suppose we have a support system. The first version can collect customer information and prepare a draft reply:

```text
Customer data
     ↓
AI
     ↓
Draft
     ↓
Operator
```

The next version may suggest:

> Add the `refund_requested` tag.

But a human still applies it.

After accumulating enough quality data, the agent can be allowed to perform a few low-risk operations itself:

```text
add_tag
create_internal_note
assign_category
```

while an operation such as:

```text
refund_payment
```

remains human-controlled or inside a deterministic workflow.

I like this model because autonomy becomes a property of a specific operation rather than a vague property of the technology.

Instead of saying:

> Our agent is autonomous.

it is more useful to say:

> It can perform this operation independently, this one only after approval, and this one never.

## Do not give business invariants to the model

Suppose the business rule is:

> A refund is allowed only within 30 days and only for certain transaction types.

You can put that rule in a prompt and ask the LLM to decide:

```text
should_refund(transaction)
```

It may even work quite well.

I still would not design it that way.

If the rule can be expressed as deterministic application logic:

```php
$refundPolicy->canRefund($transaction);
```

then ordinary code should make that decision.

The LLM can understand the user's natural-language request, determine that they are describing a duplicate charge, find the relevant transaction, and prepare the arguments for an operation.

But the final invariant should still be enforced by the application:

```text
User
 ↓
LLM
 ↓
refund_payment(transaction_id)
 ↓
Application Service
 ↓
RefundPolicy
 ↓
Payment System
```

A tool should not become a bypass around the architecture.

If a rule is deterministic, testable, and important for correctness, there is usually little reason to move it from code into a prompt.

## If you only need context, the legacy system may barely need to change

A large class of AI features does not require operational access to the old application at all.

For search, summarization, and knowledge retrieval, you can build a derived index beside the legacy system:

```text
Legacy / Documents
        ↓
export / CDC / connector
        ↓
indexing
        ↓
embeddings
        ↓
vector search
        ↓
AI
```

The legacy database remains authoritative.

The vector database is a derived index.

If necessary, it can be rebuilt.

The same principle applies to embeddings, chunks, generated summaries, and other retrieval artifacts: they are representations of the source, not a new source of truth for business state.

RAG should not silently become an alternative business model of the system.

## What if the legacy system has no API at all?

That is common.

For read-only access, there are still several options:

- a read replica;
- CDC;
- periodic export;
- an event stream;
- a materialized view;
- a reporting database;
- a narrowly scoped read-only adapter.

Write access is where the risk rises sharply.

This architecture is very tempting during a prototype:

```text
AI
 ↓
SQL
 ↓
production database
```

It is also a good way to discover why the database schema is not the same thing as a business API.

For example:

```sql
UPDATE orders
SET status = 'refunded';
```

may create a state that the normal application could never produce because the real refund flow also checks permissions, writes accounting records, updates a payment provider, emits events, and enforces invariants.

For write operations, I would create a narrow facade that calls the same application services and rules used by the existing system.

The database is storage.

It should not accidentally become the agent's application layer.

## The Strangler pattern works well for AI too

The Strangler Fig pattern existed long before LLMs. It is usually used for gradual replacement of a monolith: a facade appears in front of the old system, and capabilities move to new components one by one. AWS and Microsoft recommend this kind of approach for incremental modernization because the old application continues working throughout the migration.

AI can be introduced with the same logic.

Not this:

```text
Legacy
↓
REWRITE
↓
AI-native platform
```

But this:

```text
             ┌→ Legacy workflow
User → Facade
             └→ New AI-assisted workflow
```

The old support search keeps working.

A semantic search appears next to it.

Then an AI summary.

Then a recommendation.

Then several controlled actions.

If the new path fails, traffic or the workflow can return to the old one.

This is particularly attractive for AI because the model layer will probably evolve much faster than the underlying legacy system.

You do not need to make the life cycle of a ten-year-old ERP depend on the life cycle of the current LLM stack.

## Shadow mode is more useful than a beautiful demo

AI prototypes often look impressive because they are tested on examples chosen by the people building them.

Production contains the other examples.

Shadow mode is one of the simplest ways to learn what the model actually does before giving it authority.

Suppose a support ticket needs a category.

The existing process continues to use the human decision, while the AI runs in parallel:

```text
Ticket
 ├→ Human → category
 └→ AI    → category
```

The AI result does not affect production behavior.

But over several weeks, you can compare outcomes.

Where do they disagree?

Which categories are confused?

Which tickets lack context?

Which rare cases produce dangerous mistakes?

The same approach works for recommendations, summaries, and proposed actions.

Before automating a decision, it is useful to observe the cost and distribution of errors on real traffic.

A demo answers “can the model do this sometimes?”

Shadow mode starts answering “how does this system behave under our actual workload?”

## Write operations need the usual boring guarantees

Once an AI agent can change real state, the architecture suddenly needs all the old engineering practices again:

- idempotency;
- authentication;
- authorization;
- rate limits;
- timeouts;
- audit logs;
- validation;
- transactions;
- retry policy;
- human approval for high-risk operations.

Suppose the tool is:

```text
create_refund(transaction_id, amount)
```

The agent should not implement refund logic itself.

The call should go through an application service that checks the current state, permissions, policy, amount limits, idempotency, and other invariants.

And the audit trail should answer at least:

```text
who initiated
which agent/model
which tool
arguments
result
timestamp
approval
```

An AI agent is simply a new actor in the system.

Actors need permissions and auditability.

AWS guidance for agent integration emphasizes constraining legacy interfaces through adapters, access control, and rate limits. OWASP guidance for agentic systems adds least privilege, allowlisting of permitted actions, human approval for irreversible operations, and audit trails.

All the boring engineering practices suddenly become useful again.

## AI failure has to be designed explicitly

If AI becomes part of the product, answer this question in advance:

> What happens if the model is unavailable tomorrow?

Especially when you rely on an external provider.

For an auxiliary feature, the fallback is straightforward:

```text
AI unavailable
↓
show the old interface
```

It is much worse if an order can no longer be created or a payment can no longer be processed because the LLM did not respond.

I like this rule: the more critical the business flow, the less its correctness should depend on a probabilistic external service.

AI can help make a decision.

Where possible, the core transaction should remain deterministic.

For some new AI-native products, that is obviously impossible. But in legacy modernization, we usually start with a system that already works. Making it less resilient just to add a new capability would be a strange trade.

## What I definitely would not do

First, I would not start an AI integration with a major rewrite. If the system genuinely needs modernization, that is a separate initiative with its own business case. AI may help accelerate it, but tying two large transformations together increases risk.

Second, I would not give the model direct write access to the production database simply because that makes the prototype easy.

Third, I would not move deterministic business rules into prompts. If an invariant can be expressed in code, keep it in code.

Fourth, I would not put every available piece of information into the model's context. Give it the relevant context for the current decision. This is a Context Engineering problem, not a “bigger context window” problem.

Fifth, I would not give an agent the same permissions as a backend service. It should receive only the operations required for its workflow.

Sixth, I would not introduce an AI dependency without a fallback for failure.

Seventh, I would not evaluate the system only by asking whether “the model answers well.” Measure workflow time, accuracy, human corrections, cost, latency, and error distribution.

## How I would introduce AI step by step

I would start with one workflow rather than an AI platform.

Then I would understand the existing system: where the data comes from, which capabilities exist, which rules matter, and which parts need reverse engineering.

Then I would create a clean boundary:

```text
AI
↓
Adapter / API / MCP
↓
Legacy
```

The first production version would be read-only.

After that, I would run the model on real data in an assistive or shadow mode and collect metrics.

Then I would expose a small number of narrow tools that call existing application logic and follow least privilege.

Only after that would I increase autonomy — separately for each operation.

The progression looks roughly like this:

```text
1. Understand
2. Read
3. Recommend
4. Act with approval
5. Act autonomously within limits
```

The order matters more than the exact technologies.

## Instead of a conclusion

Legacy systems look like an obstacle because of their old stacks, strange APIs, and accumulated history.

For an LLM, however, the internal age of the system matters much less than the quality of the interface it receives.

SOAP can stay SOAP.

Stored procedures can stay stored procedures.

Twenty-year-old business logic can remain in place.

The agent may see only five clean tools.

You do not need to modernize everything before introducing AI. You do not need to turn the LLM into the business logic. And you definitely do not need to rewrite the system that currently earns money just to make it look AI-native.

Often the best first modernization step is simply a well-designed boundary: one that exposes the data and capabilities AI actually needs while leaving the authoritative business system intact.

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
