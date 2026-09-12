---
date: 2026-09-07
author: Oleg Patsay
slug: agent-ready-codebase
excerpt: "How Git, ACDD, DDD, SOLID, tests, documentation, backlog, and linters help AI agents understand a codebase and safely change legacy systems."
---

# Agent-ready codebase: how to prepare your code for AI agents

AI can already write a method, a test, a migration, or a controller, fix a bug from a stack trace, and sometimes even make it all the way from a task description to a pull request on its own. But there is an effect that becomes obvious when you use coding agents not on a demo project, but inside an old, large system. The same model can look almost like a strong developer in one repository and then start going in circles in another one: reading random files, duplicating existing logic, and confidently breaking rules that seemed obvious to everyone on the team. The problem is not always the model.

Over the last few years, I have increasingly come to think of the codebase itself as part of the AI infrastructure. We used to design systems primarily for the business, the runtime, and other developers. Now there is another reader: an AI agent. It was not in your meetings. It does not remember the incident from two years ago. It does not know why the “obvious” solution cannot be used here, and it never heard the architect say, “don’t touch this module yet, we’re extracting it next month.” The agent only sees what it can reach.

Put simply, a good codebase for AI is a project that can explain itself. Where to find the relevant code. What that code means. Why the solution is structured this way. Which behavior is considered correct. Which changes are allowed. How to verify the result. And when to stop instead of continuing to “improve” the system on its own initiative. I will call this kind of project an **agent-ready codebase**.

The term is not a formal software engineering standard; it is a useful frame for talking about a project that has been prepared for AI agents. Most of that preparation coincides with the engineering practices we used long before LLMs appeared: clean architecture, explicit boundaries, documentation, good tests, reproducible environments, linters, and an atomic Git history. We used to call all of this good engineering; now it also determines the quality of AI-assisted development.

In this article, I want to turn these ideas into one practical system: first, understand how an agent actually sees a repository; then go through ten practices from my own experience; and finally assemble a concrete plan for legacy projects, a task template, a maturity model, and a checklist. The goal is not to invent another layer of process around AI, but to understand which parts of ordinary engineering become especially important once code is changed not only by humans.

## Why AI-generated code quality depends on more than the model

### Modern AI agents can already write code, but they still struggle to understand systems

Writing an isolated function and changing a real system are two different tasks. At the level of one method, an LLM may see a signature, a description, and a few neighboring types. At the repository level, it has to understand architectural boundaries, find several related files, reconstruct a business rule, inspect tests and configuration, and sometimes study the change history. That is why discussing AI coding only in terms of “which model writes code best right now” is not very productive. The model matters, but after a certain capability threshold the environment we place it into matters more and more.

A classic example is a real task like “allow a payment retry only after a certain status.” In a tiny example, adding an `if` is enough. In a production system, the actual rule may be spread across an aggregate, a policy class, a queue handler, the database schema, an external API contract, and a test that was introduced after an incident three years ago. If the agent sees only the handler, it can easily produce a locally elegant and globally wrong change.

A syntax error is quickly caught by the compiler. A misunderstood business rule compiles, passes some of the tests, and looks plausible — which is exactly why it is the hardest thing to notice during review.

### Why the same model produces different results in different projects

I have seen developers compare AI tools roughly like this many times: “Claude works great in this project, but Cursor is dumb here,” “Codex handled the new feature well but fell apart on the legacy code,” “this model just does not understand our codebase.” Sometimes that conclusion is correct, sometimes it is not. Imagine two projects. The first has clear modules, tests that run with one command, names that reflect the domain model, documentation next to the code, linter errors that explain the problem, and a Git history made of small, meaningful changes. In the second, `src/Service` contains 400 classes, half the behavior is hidden in framework lifecycle hooks, the documentation lives in an old wiki, tests only run on one developer’s laptop, and the last twenty commits are called `fix`, `fix2`, `final`, `final-final`.

The model is the same, but the information environment is completely different. In the first project, the agent can reduce uncertainty step by step: find the module, read its instructions, inspect a test, make a local change, get deterministic feedback. In the second, it has to guess, and LLMs are all too good at that: producing a plausible continuation for missing information.

### The codebase becomes part of the AI infrastructure

When people say “AI infrastructure,” they usually mean the model, embeddings, a vector database, MCP, tools, a sandbox, and everything else around inference. But for a coding agent, the repository itself becomes one of the main sources of context. In practice, it is a knowledge base that the agent keeps exploring while it works. The current code says how the system works now. Git explains how it got there. Documentation explains decisions. Tests capture expected behavior. The backlog hints at a possible future. Linters and CI formalize rules that must not be broken. The codebase stores not only the program itself, but also part of the team’s engineering memory.

The more work we delegate to AI, the more important the quality of that memory becomes.

### The real bottleneck is not code generation, but engineering context

Generating lines of code is becoming less and less of a problem: you can get hundreds of lines in a few minutes, sometimes too many. The scarce resource is something else: correctly understanding **what needs to change and why**. This is visible in research on repository-level code generation. In [RepoCoder](https://aclanthology.org/2023.emnlp-main.151/), the authors explicitly study information distributed across multiple files in a repository. Their iterative retrieval-generation approach performed noticeably better than a variant that only looked at the current file. More recent work goes even further: similarity search alone is not enough, because dependent code may be semantically important while looking nothing like the wording of the task.

For example, in [Effective and Efficient Context Retrieval via Partial Dependency Graph for Repository-Level Code Generation](https://arxiv.org/abs/2608.01927), accepted at ASE 2026, the researchers build context around a partial dependency graph. In their experiments, this approach produced a substantial Pass@1 improvement over standard RAG baselines. What matters here is not the exact percentage but the direction: for real software development, finding similar text is not enough; you have to reconstruct relationships inside the system. I would formulate the problem like this:

> The stronger the generator becomes, the more valuable the system’s ability to provide the right context and automatically verify the result becomes.

This changes the conversation about AI development: instead of endlessly optimizing prompts, we get an engineering question: **how ready is the project itself to be understood by a machine?**

## What is an agent-ready codebase?

### A simple definition of an agent-ready codebase

An agent-ready codebase is a codebase in which an AI agent can move through five steps with reasonable reliability:

1. Find the place that needs to change.
2. Understand the meaning of the current behavior.
3. Make a constrained change.
4. Verify the result.
5. Stop when confidence or authority is insufficient.

The last point matters: a well-prepared project does not have to give the agent maximum autonomy. A mature system makes it explicit where autonomy ends. If a change affects a public contract, payments, access control, production configuration, or a destructive migration, a perfectly valid agent output may be not a finished commit, but a plan and a request for confirmation.

### How agent-ready differs from AI-friendly

I would separate these concepts. An **AI-friendly** project is simply easy for a model to read: understandable names, documentation, reasonably sized files, good structure. An **agent-ready** project additionally makes it possible to **act** : start the environment, run tests, get feedback, understand constraints, stay within task boundaries, and produce a verifiable result. Readability is only the first level.

You can write perfect architecture documentation, but if the project cannot be started locally without three secret commands that exist only in a senior developer’s head, that documentation will not help a full-fledged agent very much. You can have 90% test coverage, but if the tests are flaky and randomly fail, the agent gets a poor feedback loop. You can have an excellent style guide, but if half the rules are not enforced automatically, the model will still break them from time to time. Agent-ready is about the entire code-changing environment, not just a tidy repository.

### What properties should a prepared project have?

#### The agent can find the relevant part of the system

Navigation is the first problem. If a task mentions `subscription renewal`, the project should contain enough clues to lead the agent to the right bounded context, use case, handler, entity, and tests. Good naming, a module map, a stable directory structure, symbol search, documentation links, and architectural boundaries dramatically reduce the search space.

#### The agent can understand the purpose of the code it found

Finding `RenewSubscriptionHandler` is not enough. The agent also needs to understand why it allows one operation and rejects another, which invariants it protects, which side effects it triggers, and which external contract must remain intact. This is where DDD, documentation, ADRs, tests, and Git history begin to matter.

#### The agent can safely make a local change

Locality is an underrated architectural property. The smaller the area of effect, the easier it is for the agent to preserve the causal chain. If adding one business rule requires changing twelve layers, three services, and a shared utility class, that is not only an AI problem. Humans struggle with that kind of project too.

#### The agent can verify the result on its own

The agent needs a way to get machine-checkable rather than subjective feedback: tests, static analysis, linting, type checking, architectural checks, contract tests. In [Helping LLMs Improve Code Generation Using Feedback from Testing and Static Analysis](https://arxiv.org/abs/2412.14841/), the authors showed that models failed to identify some of their own mistakes without external feedback, but improved code much more effectively when they received test and static analysis results. The practical conclusion: do not rely on the agent to “double-check everything itself” — give it a verifier.

#### The agent knows when to stop and ask a human

There must be explicit boundaries: which directories may be changed, which commands are forbidden, whether migrations may be created, whether APIs may be changed, whether approval is required before deleting data, whether network access is allowed. Without such boundaries, autonomy quickly becomes a lottery.

### Codebase readiness and agent autonomy are not the same thing

You can have an agent-ready project while only allowing agents to handle small refactoring tasks. That is perfectly reasonable: maximum autonomy is not a goal in itself. The goal is to make changes to the system **cheap to understand and safe to verify**. The level of delegation can then be chosen based on risk.

When describing Codex, OpenAI emphasizes a similar idea: the agent works better in a properly configured environment, with reliable tests and clear documentation, and its output should still be reviewable by a human. In 2025–2026, `AGENTS.md` became one of the practical formats used to give coding agents instructions about project structure, test commands, and local rules. This is how the repository gradually becomes an interface between the team and the agent.

## How an AI agent sees a software project

### A context window is not the same as memory

Large models now have enormous context windows. This sometimes leads to the conclusion that you can just “feed it the entire repository” and the understanding problem will disappear. It does not: a context window is input capacity, not a guarantee that every piece of information receives equal attention. The classic paper [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) showed that performance can change significantly depending on where relevant information appears in a long context. Information placed near the beginning and end was used more effectively than information buried in the middle.

The study was not specifically about coding agents, but the engineering conclusion transfers well: **available information and information that is actually used are not the same thing**. That is why I dislike the idea of one giant 8,000-line `AGENTS.md`. Formally, the agent has been given everything; in practice, we created another repository inside the repository, which also has to be searched.

### An agent does not read the entire repository before every task

A normal coding-agent workflow looks much more like investigation. It gets a task, searches for mentions of an entity, inspects the project tree, opens a few files, follows imports or usages, looks for tests, and sometimes checks Git. Then it forms a hypothesis, makes a change, and runs verification. The agent has its own “attention path.” The quality of that path depends on how easily it can move from one useful point to the next. A good class name leads to a domain concept. A test sits nearby. The test reveals a fixture. Documentation points to an ADR. The commit message explains why the constraint exists.

A bad project forces the agent to perform broad searches, open dozens of files, and keep a lot of noise in context.

### How an agent searches for files, symbols, and dependencies

At the simplest level, with ordinary text search. Then symbol search, references, and imports. More advanced tools add embeddings, semantic search, a language server, AST analysis, and dependency graphs. Research confirms a developer’s intuition: code cannot be treated as just a bag of text chunks.

[GraphCoder](https://ieeexplore.ieee.org/document/10765009/) uses a code context graph and coarse-to-fine retrieval. [InlineCoder](https://arxiv.org/abs/2601.00376/) builds context around upstream and downstream relationships. The newer DyRetriever follows a partial dependency graph. The methods differ, but the core idea is the same: **the structure of relationships inside code carries information of its own**. The practical implication is straightforward: project architecture affects not only humans and runtime behavior. It also affects the quality of context an agent can assemble for a specific change.

### Why project structure affects retrieval quality

Suppose you have two options. In the first project:

```text
src/
  Billing/
    Domain/
    Application/
    Infrastructure/
    Tests/
```

In the second:

```text
src/
  Controllers/
  Services/
  Managers/
  Helpers/
  Utils/
```

The first option is not automatically better. But if the names correspond to real business boundaries, the agent gets a useful prior directly from the file tree. In the second case, the word `Service` says almost nothing about meaning. Good structure reduces search entropy. The agent understands earlier where it is and which neighboring parts of the system matter.

### What sources does an agent use to build context?

I tend to split project context into several sources. **The current code** shows the present state of the system. It is the implementation closest to the truth. **Git** shows the past. Why a check was introduced. In which change a field appeared. Which files tended to change together. Where the boundary of the previous task was. **Documentation** stores meaning that cannot always be recovered from code alone: decisions, constraints, flow diagrams, conventions. **Tests** show expected behavior in concrete scenarios. A good test often explains a rule faster than reading the implementation.

The **backlog** shows the intended future. It is a less reliable source because plans change, but sometimes it is critical. **Linters and CI** define the normative layer. They may not explain why a rule exists, but they state unambiguously that violating it is not allowed. Together, these sources start to look very much like the team’s external memory.

### Why available context does not automatically become used context

You can create a `/docs` directory in the repository, write ADRs, and add a README for every module. But the agent is not guaranteed to find the exact document it needs. Information has to be not only stored, but made **navigable**. For example, a root `AGENTS.md` can say:

```md
## Architecture

- System overview: `docs/architecture/overview.md`
- Billing rules: `src/Billing/README.md`
- Architecture decisions: `docs/adr/`
- Test conventions: `docs/testing.md`

Do not read all ADRs by default.
Open only ADRs related to the module being changed.
```

That is much more useful than pasting the contents of every ADR directly into the initial instruction.

### What progressive disclosure of context means

I like the principle of progressive disclosure: at each level, show the agent only the amount of information needed to make the next decision. At the repository root, provide the project map and key commands. Inside a bounded context, provide local rules. In a specific ADR, explain the reason behind an architectural decision. In a test, show the behavior of a scenario. This solves two problems at once. First, the initial context stays compact. Second, knowledge lives close to the area it belongs to. The structure might look like this:

```text
AGENTS.md
  ↓
docs/architecture/overview.md
  ↓
src/Billing/AGENTS.md
  ↓
src/Billing/README.md
  ↓
docs/adr/0042-retry-policy.md
  ↓
specific code + tests
```

The agent goes deeper only when the task requires it.

## Agent-ready codebases, Context Engineering, and Harness Engineering

### How these three concepts relate

By 2026, AI development had accumulated enough terminology that it became easy to mix things up. I would separate these ideas by responsibility. **Context Engineering** is responsible for which information enters the model’s working context at a given moment. An **agent-ready codebase** is responsible for whether the right information can be extracted from the project in an understandable form at all. **Harness Engineering** is responsible for the execution environment: tools, commands, sandboxing, permissions, loops, checks, observability, and the rules governing how the agent interacts with the system. If we compare it to a regular application, the codebase is the data and domain structure, context engineering is the retrieval mechanism, and the harness is the runtime.

### Context Engineering is about selecting information

Too little context, and the agent starts filling in the gaps. Too much, and the signal gets buried in noise. The wrong context, and the agent builds a correct solution for the wrong part of the system. Context engineering is not “write a very long prompt” but working-memory management: what to load now, what to keep outside, when to perform additional retrieval, which history to summarize, and what should be treated as the authoritative source.

### An agent-ready codebase makes information accessible

No intelligent retriever can retrieve an ADR that never existed. No giant context window can explain a business invariant that lived only in the head of someone who left the company two years ago. No agent can run stable verification if the project does not have a reproducible test environment. Repository preparation is the foundation; context engineering works on top of it.

### Harness Engineering turns rules into an operational process

You can write in an instruction, “do not violate architectural layers.” That is a preference. You can add an architecture test that forbids `Domain -> Infrastructure`. That is a constraint. You can write, “run tests after making changes.” That is an instruction. You can give the agent one command, `make verify`, that runs unit tests, integration tests, static analysis, and linting. That is a harness. The more important a rule is, the less I want to leave it only in natural language.

### What Repository Intelligence is

Another useful term is repository intelligence. By that I mean the set of mechanisms that let an agent do more than just read files: text search, symbol search, semantic retrieval, dependency graphs, Git history, and co-change analysis. I think this is one of the areas where tooling will develop especially quickly over the next few years. For now, modern agents mostly imitate the path of a developer: `grep`, tree, language server, tests, Git. But repository-level generation research already shows that structural retrieval can produce meaningful gains.

Do not confuse search quality with source-data quality: an intelligent search system over a chaotic project is still a search over chaos.

### Why a large context window does not fix bad architecture

A large context window can temporarily hide an architectural problem. If you stuff twenty related classes into it, the agent may eventually figure things out. But that is an expensive form of compensation. Bad architecture expands the reasoning surface. The more components that must be held in mind at the same time, the higher the chance of missing a non-obvious relationship. For a human, that is cognitive load. For an agent, it is tokens, retrieval steps, and additional failure points. AI does not invalidate the old engineering principle of locality; it makes locality measurable by the number of files that have to be read before one safe change can be made.

## Why good engineering practices matter even more for AI

### Practices invented for humans become interfaces for agents

Most “AI-ready” practices existed before AI. Single Responsibility was not invented for LLMs. DDD was not designed for coding agents. Unit tests did not appear to support self-healing generation loops. ADRs were not created for retrieval. But all of them make engineering intent more explicit, and that is exactly what models are constantly missing. A good class name reduces ambiguity. A Bounded Context narrows the search space. A test turns a requirement into an executable check. A linter turns an agreement into deterministic feedback. An ADR preserves the reason behind a decision. What helped humans has become an interface for AI.

### Explicitness reduces the amount of guessing a model has to do

There is one principle running through this entire article: **make the implicit explicit**. Not `string $status`, but `OrderStatus`. Not a comment in a three-year-old Jira ticket, but a test + ADR. Not “this is how we usually do it,” but a lint rule. Not “I think this service should not be called from the domain,” but an architecture test. Not “don’t touch production,” but technically restricted permissions. Every piece of explicitness shrinks the space the model has to reconstruct on its own.

### Locality reduces the potential change surface

If a task fits inside one module, the agent has an easier time understanding the context and verifying the consequences. If the code is tightly coupled, the scope expands quickly. This is why I prefer to look not at method length by itself, but at the **change radius**. How many files must be opened? How many concepts must be understood? How many contracts must be checked? How many independent subsystems can the diff accidentally affect? That is the real complexity of a task for an agent.

### Deterministic checks compensate for model nondeterminism

An LLM is probabilistic. A test runner is not. A static analyzer is not. A schema validator is not. A compiler is not. That is why automated checks are one of the central elements of an agent-ready codebase. Tests do not make the model smarter, but they make an error visible and give the agent a way to take the next step based on a fact rather than an assumption.

In [Test-Driven Development for Code Generation](https://arxiv.org/abs/2402.13521/), the authors experimentally tested adding tests to the original task specification and observed a higher success rate on code-generation benchmarks. These are function-level experiments, so they should not be transferred directly to a huge legacy system, but the idea itself is practical: a test is not only a final check; it is also part of the specification.

### A codebase should not only store code; it should explain itself

I would think of a repository as several parallel representations of the same system. Code answers: **how does it work?** Tests answer: **what must keep working?** Documentation answers: **why is it designed this way?** Git answers: **how did we get here?** The backlog answers: **where are we trying to go?** Linters and CI answer: **what is not allowed to change?** When these representations agree, the agent gets a much more stable model of the project.

## 10 practices from my experience that help AI understand code better

What follows is not an academic list of best practices for LLMs, but a set of things I arrived at through ordinary software development and that became even more useful with AI coding. I used some of them long before modern agents existed; now it is simply easier to see why they matter to another type of reader as well.

### 1\. ACDD and atomic Git history preserve the path of engineering thought

I have already written separately about [ACDD](/atomic-commits-acdd) — Atomic Commit Driven Development. This is not another methodology for the sake of an acronym, but a working rhythm. The formula is simple:

> Thought → record → action → commit.

One meaning, one action, one commit. When a change is small and coherent, it is easier for a human to review. But with AI, there is an additional effect: Git becomes a source of historical context. Imagine this line:

```php
if ($payment->isExpired()) {
    throw new RetryNotAllowed();
}
```

The current code tells us **what** happens. But why exactly are expired payments not allowed to retry? Is this a business constraint? A provider quirk? Protection against double charging? A temporary workaround? If `git blame` leads to a commit like this:

```text
Prevent retry for expired payments after ProviderX incident

ProviderX can accept delayed retries after the payment session expires,
creating a second charge with a new transaction id.
Refs: INC-2417
```

the context changes completely. A good Git history is not cosmetic; it is a journal of engineering decisions at the lowest level.

#### Why one commit should represent one complete change

Atomicity does not mean “every two lines should be a separate commit.” I would define it in terms of meaning. A good commit can be explained in one sentence. It has a clear reason. It can be reviewed independently. Ideally, it can also be reverted independently. A bad commit looks like this:

```text
Update billing
```

and contains:

- a new retry policy;
- a renamed DTO;
- formatting changes across 80 files;
- dependency updates;
- a fix for an old test;
- removal of a debug log.

For a human, that is an expensive review. For an agent, it is poor historical context: it becomes impossible to tell which changes were causally related.

#### What an agent can learn from a good Git history

Git provides several useful types of information. `git log -- path` shows how a specific file evolved. `git blame` helps locate the change that introduced a line. `git show <commit>` gives a local diff together with its message. A sequence of related commits reveals the progression of a solution. Sometimes it is almost a ready-made reasoning trace of the team, just without anyone’s internal monologue.

The more important point is this: **Git will not enter the agent’s context automatically just because the history is good**. The agent has to know when it should inspect history. I would make that explicit in the instructions: if the code contains a non-obvious constraint, a workaround, backward compatibility logic, or a strange branch, inspect `git blame` and the related commits before changing it.

#### Why I do not like mindless squash

Squash is useful when the intermediate history is genuinely noise: `wip`, `fix typo`, `oops`. But if five independent engineering steps become one giant commit called “Implement feature,” we lose the structure of the change. I do not think squash is always bad. The question is what remains afterward. If the post-merge history still answers “what changed and why,” great. If it becomes a series of snapshots of huge PRs, part of the project’s external memory disappears.

### 2\. Class and method documentation reveals hidden meaning

I am not a fan of documenting every getter or writing comments just to increase documentation coverage. A comment like this:

```php
// Get user by id
public function getUserById(int $id): User
```

helps no one. Useful documentation begins where the signature and implementation fail to convey important meaning. For example:

```php
/**
 * Retries a payment using the original provider session.
 *
 * Business invariant:
 * - allowed only while provider session is active;
 * - must never create a new external transaction;
 * - duplicate provider response is treated as success.
 *
 * This method is intentionally not used for manual recovery.
 */
public function retry(Payment $payment): void
```

Now the agent gets information it would otherwise have to reconstruct across several files.

#### What exactly is worth documenting

I would prioritize:

- business invariants;
- important side effects;
- non-obvious constraints;
- valid and invalid states;
- reasons for unusual behavior;
- backward-compatibility requirements;
- relationships with external systems when they influence logic.

Documentation is useful when it answers “why” rather than repeating “how.” At the same time, there is a risk of creating the opposite problem: information noise. If every method has half a page of obvious prose above it, the agent has an even harder time separating signal from boilerplate.

### 3\. AAA-style tests give the agent a clear scenario structure

I like Arrange, Act, Assert not out of dogma: a test written this way reads like a tiny story.

```php
public function testExpiredPaymentCannotBeRetried(): void
{
    // Arrange
    $payment = PaymentFixture::expired();

    // Act
    $action = fn () => $this->retryPayment->execute($payment);

    // Assert
    self::assertThrows(RetryNotAllowed::class, $action);
}
```

First, the state of the world. Then the action. Then the expected result. The structure is obvious to a human, and to an agent too. A chaotic test that mixes fixture creation, three use-case calls, time manipulation, six unrelated assertions, and then a mock verification is a poor specification. To understand which rule it protects, the scenario has to be reconstructed.

#### One test, one logical outcome

It is important not to turn this into the formalism of “one test = one `assert`.” Sometimes one logical outcome is verified by several technical assertions. For example, “the payment was completed successfully” may mean:

```php
self::assertSame(PaymentStatus::PAID, $payment->status());
self::assertNotNull($payment->paidAt());
self::assertCount(1, $events->ofType(PaymentPaid::class));
```

That is still one outcome. A simpler criterion is this: can you give the test one concrete name without `and`, `also`, or “then somehow”?

### 4\. Test documentation explains the business meaning of behavior

This practice is especially valuable in complex domains. A test name often tells you **what** is being checked, but not **why it matters**. For example:

```php
/**
 * ProviderX expires the original payment session after 30 minutes.
 * Retrying after expiration may create a second external transaction,
 * therefore the system must reject this operation.
 *
 * Introduced after INC-2417.
 */
public function testExpiredPaymentCannotBeRetried(): void
```

Now the test becomes a small archive of business context. I like to think of code, tests, and documentation as three representations of one intent:

- production code implements the rule;
- a test proves the observable behavior;
- documentation preserves the reason.

This is especially useful for AI because the reason often cannot be inferred unambiguously from the behavior alone.

#### When test documentation becomes dangerous

When it becomes stale. An old comment above new behavior is worse than no comment at all because it creates false confidence. That is why changing business behavior should include checking the whole chain: code → tests → docs. Ideally, this belongs in the Definition of Done and in the agent’s instructions: if behavior changed, inspect the related documentation and test description as well.

### 5\. SOLID and Single Responsibility reduce the agent’s reasoning surface

Single Responsibility has many interpretations. For this article, I care about one practical effect: a component with one coherent responsibility creates a smaller reasoning boundary. If `InvoiceService` creates invoices, sends email, calculates VAT, writes audit logs, calls the ERP, and updates user statistics, every change pulls in a wide analysis surface. If those responsibilities are separated into understandable components, the agent can work more locally. This does not mean splitting everything into two-line methods.

In fact, excessive decomposition can make understanding worse. A scenario that used to read top-to-bottom in one use case turns into jumps across fifteen private methods. The call graph grows while local meaning shrinks. I would phrase it this way: **a method or class should be small enough to have one responsibility, and cohesive enough that the responsibility can be understood without archaeology**.

#### Blast radius matters more than line count

I would judge decomposition quality not by LOC, but by blast radius. If a rule can be changed in one aggregate and three tests, that is good. If you have to touch a shared base class, a helper, an event subscriber, and four unrelated modules, the responsibility boundaries are probably blurred.

### 6\. DDD makes the domain visible directly in code

The more I work with AI in software development, the more I like DDD again. Not as a collection of heavy patterns, but as a way to make business meaning part of the code itself. An LLM knows perfectly well what `Manager`, `Service`, `Helper`, and `Processor` are. The problem is that these words say almost nothing about your business. `CreditLimit`, `RepaymentSchedule`, `SubscriptionRenewal`, `WithdrawalPolicy`, and `InvoiceNumber` do.

#### Ubiquitous Language as a shared language for business, developers, and AI

If the task says “renew subscription,” the documentation says `renewal`, the code uses `ProlongationManager`, the database says `recurrent`, and the UI says “auto-renewal,” even a human has to build a translation dictionary first. An agent has the same problem. Ubiquitous Language reduces the number of these transformations. One concept flows through the issue, code, tests, and documentation. It is essentially semantic compression: fewer terms, less ambiguity.

#### Bounded Context as a natural boundary for an agent task

A Bounded Context works very well as scope. Is the task about Billing? Then the agent first reads `src/Billing/AGENTS.md`, the Billing architecture, and tests from that module. It only leaves the boundary if it discovers an external contract. That is better than starting every change by exploring the entire monolith.

#### Aggregates, Value Objects, and domain events

An Aggregate is useful because it collects invariants in one place. A Value Object turns a constraint into a type. Instead of “a string that is actually an ISO currency code,” you get `Currency`. A Domain Event makes a meaningful change explicit: `PaymentPaid`, `SubscriptionCancelled`, `LimitExceeded`. For the agent, these are additional anchors: it has to infer less of the business from low-level technical details.

#### Why framework magic gets in the way

AI is especially weak at behavior that cannot be observed from local code. Hidden lifecycle hooks. Implicit autowiring. Global state. Configuration that silently swaps implementations. Active Record callbacks. Magic methods. Even a human with years of experience in a particular framework can spend an hour asking, “what even calls this code?” An agent does not have years of muscle memory for your project. I am not arguing that all framework magic should be eliminated. But critical relationships should be made observable through documentation, explicit interfaces, integration tests, and clear entry points.

### 7\. System documentation inside the repository creates long-term memory

I am in favor of docs-as-code not because Markdown is prettier than Confluence, but because documentation that lives next to the code:

- is versioned together with it;
- enters the same pull request;
- is accessible to the coding agent;
- can link to specific modules and ADRs;
- is easier to include in review.

An external wiki can be useful too. But if the agent has no tool access to it, that part of memory simply does not exist from the agent’s perspective.

#### What to document at the system level

A minimal set I would want to see in a large project looks something like this:

```text
docs/
  architecture/
    overview.md
    modules.md
    data-flow.md
  adr/
  integrations/
  operations/
  testing.md
  development.md
```

The exact layout does not matter. The content does:

- product purpose;
- key business processes;
- architectural layers;
- modules and their responsibilities;
- external integrations;
- data flow;
- entry points;
- known constraints;
- technical debt that affects decisions.

####  `AGENTS.md` should be a navigator, not an encyclopedia

This is one of the main practical ideas of the article. The root agent file should quickly answer:

1. What kind of project is this?
2. How do I run it?
3. How do I verify a change?
4. Where do I read about the architecture?
5. Which rules must not be broken?
6. Where are the local instructions?

Everything else should be linked. Incidentally, this hierarchical approach is already appearing in tools. GitHub Copilot coding agent supports root and nested `AGENTS.md`, while OpenAI Codex takes instruction scope along the directory tree into account. That makes sense: rules in a large monorepo are rarely identical for frontend, billing, and infrastructure.

### 8\. A TODO list and backlog show the intended future of the system

This is the most debatable item on the list. Why give AI plans at all if the source of truth is the current code? Because an architectural decision often depends on where the system is headed. Imagine the agent sees duplication between two modules and decides to extract a shared abstraction. Locally, the solution is elegant. But the team has already decided that one of those modules will be extracted into a separate service in two weeks. The new abstraction only strengthens a coupling the team intended to break. In that case, the backlog provides strategic context.

#### What is useful to keep close to the code

Not the entire Jira backlog. What I find useful are things that change today’s engineering decisions:

- current major changes;
- planned migrations;
- known technical debt;
- deprecated areas;
- “do not touch yet” decisions;
- rejected architectural ideas and the reasons they were rejected.

At the same time, you should clearly distinguish a **decision** , a **plan** , and a **hypothesis**. Otherwise, the agent may treat raw brainstorming as a requirement. For example:

```md
## Status

Decision: Orders remain in the monolith in 2026.
Plan: extract Notifications after Q4 load testing.
Hypothesis: Billing may move to a separate service later; no decision yet.
```

#### A stale backlog is dangerous

An outdated strategy can be worse than no strategy at all. If a document says “we are migrating to Kafka next quarter,” while the team has been happily using RabbitMQ for three years and no longer plans to move, the agent may start optimizing the system for an imaginary future. Strategic context should have an owner, a status, and a review date.

### 9\. Linter rules turn requirements into automated feedback

I try to move everything that can be checked automatically into automated checks. Not because I enjoy red pipelines, but because human agreements are easy to forget, and agreements with an LLM are nondeterministic on top of that. Things that can be checked include:

- formatting;
- forbidden dependencies;
- layer boundaries;
- cyclomatic complexity;
- type rules;
- nullable contracts;
- security patterns;
- naming;
- forbidden APIs;
- required annotations;
- public API compatibility.

Custom architecture rules are especially valuable. Instead of only writing:

```md
Domain layer must not depend on Infrastructure.
```

it is better to also have a test:

```php
Architecture::expect('App\\Domain')
    ->notToDependOn('App\\Infrastructure');
```

Now the agent can make a mistake, but the system immediately explains it.

#### What linter messages should look like for AI

A good message should be actionable. Bad:

```text
Architecture violation.
```

Better:

```text
Billing\Domain must not depend on Billing\Infrastructure.
Move the interface to Domain or Application and keep the implementation in Infrastructure.
See docs/architecture/dependencies.md.
```

That is almost a built-in repair prompt.

### 10\. A style guide defines a common language for changes

The last point seems the most boring until you start reviewing hundreds of AI-generated diffs. A model adapts easily to local patterns if those patterns are actually consistent. But if half the project uses factories and the other half constructors, if errors are represented as exceptions in one area, result objects in another, and `null` somewhere else, the agent has to choose for itself. Which means it may add yet another variation. A style guide is not mainly about fighting over spaces. The important decisions are the ones that affect structure:

- class and method naming;
- module structure;
- error handling;
- exceptions;
- logging;
- transaction handling;
- test conventions;
- documentation;
- DTOs / Value Objects;
- dependency rules.

And again: whatever can be checked should preferably be checked automatically. A style guide should explain meaning and exceptions, while formatters and linters mechanically enforce the form.

## Five layers of context in an agent-ready codebase

After all these practices, I started to think of a repository as five layers of memory.

### Historical layer: why the system became this way

This includes Git, pull requests, ADRs, and incident references. This layer answers the question: **why does this solution exist?** Without it, an agent is especially likely to “fix a weird thing” that is actually protection against a real production case.

### Semantic layer: what the code means

DDD, naming, module boundaries, documentation, schemas. It answers: **what are these entities and what role do they play in the business?**

### Behavioral layer: what the system must do

Tests, acceptance scenarios, contracts, examples. It answers: **which observable behavior must not be broken accidentally?**

### Strategic layer: where the system is supposed to go

Backlog, migration plans, technical strategy, deprecations. It answers: **which decisions today are compatible with the near future?**

### Normative layer: which changes are allowed

Linters, static analysis, CI, permissions, security boundaries, agent instructions. It answers: **what is the agent allowed to do, and which constraints must remain true?** When all five layers are available and consistent, the agent has much less to guess.

## What even well-written code is still missing

Good architecture, clear naming, and tests already get you a long way. But they are not enough for a real agent workflow. The agent has to do more than read the project; it has to work with it in practice.

###  `AGENTS.md` as the entry point for an AI agent

In a root `AGENTS.md`, I would keep only things that are truly global. For example:

```md
# Project

Payment platform monolith.
PHP 8.2, Symfony, PostgreSQL, RabbitMQ.

## Start here

- Architecture: `docs/architecture/overview.md`
- Module map: `docs/architecture/modules.md`
- Testing: `docs/testing.md`
- ADR: `docs/adr/`

## Commands

- Install: `make install`
- Unit tests: `make test-unit`
- Full verification: `make verify`

## Rules

- Do not change public API contracts without explicit approval.
- Do not modify production infrastructure.
- Do not access real secrets or production data.
- Keep changes within the requested bounded context unless a dependency requires otherwise.
- For non-obvious legacy behavior, inspect Git history before changing it.

## Local instructions

Nested `AGENTS.md` files may define stricter module-specific rules.
```

The main job of this file is to reduce the cost of the first step. The agent should not spend ten minutes figuring out how to run the tests or where the architecture documentation lives.

#### What is better moved into separate documents

Detailed domain descriptions, the full list of integration contracts, dozens of ADRs, troubleshooting, and test conventions should live separately. Otherwise, the root instructions grow too quickly. The `AGENTS.md` format is already used at least by OpenAI Codex and GitHub Copilot coding agent. Other tools have their own equivalents, such as `CLAUDE.md`, but the idea matters more than the filename: a repository should have a compact, machine-readable entry point.

### Architecture decisions in ADR format

Code almost always shows the decision that was chosen. It is much worse at showing rejected alternatives. Suppose a project uses an outbox instead of publishing an event directly. The agent sees an extra table, a worker, and additional complexity, and may decide to “simplify” the system. An ADR can explain that direct publishing was already tried and caused inconsistencies between the transaction commit and the message broker. A minimal format can be short:

```md
# ADR-0042: Use transactional outbox for payment events

Status: accepted
Date: 2026-02-14

## Context

Payment state and emitted events must not diverge when RabbitMQ is unavailable.

## Decision

Persist events in the same database transaction and publish them asynchronously.

## Alternatives rejected

Direct publish after commit: creates an unrecoverable gap when broker publishing fails.

## Consequences

Additional outbox table and worker are intentional complexity.
```

The phrase `intentional complexity` here is more useful than ten code comments. It immediately protects the architecture from being “improved” away.

### One command to run all checks

If an agent has to remember seven commands after making a change, eventually it will forget the eighth one. I prefer a single entry point:

```bash
make verify
```

or:

```bash
just verify
```

or any equivalent appropriate for the project’s ecosystem. Internally, it may run:

```text
formatter check
lint
static analysis
unit tests
integration tests
architecture tests
schema validation
contract tests
```

Not all of these have to run for every tiny change. You can have `verify-fast` and `verify-full`. But the agent should understand the difference, while CI remains the final authority.

### A reproducible local environment

Here AI exposes an old problem. If a new developer gets a five-page README containing phrases like “if this doesn’t start, ask Vasya,” the agent will not be able to work reliably either. Reproducibility means setup is documented and automated where possible:

- pinned dependencies;
- container or development environment;
- migration setup;
- test database;
- fixtures;
- predictable service dependencies;
- documented environment variables;
- no hidden manual steps.

This is one reason I like that SWE-bench eventually moved to a containerized evaluation harness: real-world software tasks cannot be evaluated honestly if the environment itself is not reproducible. The same principle applies to production projects.

### Explicit contracts and data schemas

The more behavior is described by types and schemas, the less has to be explained in natural language. Useful tools include:

- typed interfaces;
- OpenAPI;
- JSON Schema;
- protobuf;
- database schemas;
- event contracts;
- generated clients;
- boundary validation.

If an API accepts `status: string`, the model has to search for allowed values. If there is an enum or a schema:

```yaml
status:
  type: string
  enum:
    - pending
    - paid
    - failed
```

part of the context becomes executable.

### Observability that is accessible to the agent

If the task is to fix a runtime bug, unit tests alone are sometimes not enough. It is useful if the agent can:

- run the application locally;
- reproduce a request;
- read structured logs;
- inspect a trace;
- check metrics in a test environment;
- run a deterministic reproduction script.

I emphasize “test environment.” Giving a coding agent unrestricted access to production for convenience is a bad trade-off. Observability should expand the ability to verify, not expand the blast radius.

### Permission boundaries and security

The stronger the agent, the more important this section becomes. You have to define not only **what it can do** , but **what it is technically allowed to do**. I would separate actions by risk at minimum. **Low risk:** reading the repository, local search, running unit tests, changing scoped code. **Medium risk:** updating dependencies, migrations, network access, generated code, CI configuration. **High risk:** production, secrets, destructive commands, real customer data, IAM, billing infrastructure. For high-risk actions, a natural-language prohibition is not enough. You need a sandbox, network policies, scoped credentials, and human approval.

By 2026, this is no longer a theoretical concern. In its descriptions of safe internal Codex usage, OpenAI explicitly talks about constrained execution, network policies, managed configuration, and telemetry. The principle applies to any coding agent: permissions should match the task.

## What kind of architecture is convenient for AI agents?

### Locality of behavior

This is the most important property. If you open a use case and can see its domain objects, contracts, and tests nearby, the task becomes understandable faster. If behavior is scattered across global hooks and shared helpers, reasoning gets longer. Locality does not mean “put everything in one file.” It means related concepts live in predictable proximity and have explicit relationships.

### High cohesion within a module, low coupling between modules

The old cohesion/coupling formula becomes a practical metric for AI. High cohesion helps assemble a complete context inside a bounded context. Low coupling reduces the number of external files that must be read before a change. Ideally, the agent can say: “this task belongs to Subscription; I only need this module and two public contracts from neighboring modules.”

### Explicit dependencies

Constructor injection, interfaces, imports, and explicit message contracts are usually better than hidden service locators, globals, and magic resolution. It is not that the agent does not understand a DI container — it does. But an explicit dependency is visible immediately in code, while a hidden one has to be discovered through configuration.

### Stable interfaces

If every module has a small public surface, the agent can understand more easily what is a contract and what is an implementation detail. This also protects against scope creep. Changing an implementation inside a module should not require rewriting half the project.

### A controlled change surface

I would introduce an internal metric: how many files does an agent have to open, on average, before it can produce its first correct plan? It is not a perfect metric, but it forces you to look at architecture from an interesting angle. If an ordinary bug fix constantly requires exploring fifty files, that is not only an AI-readiness problem.

### A modular monolith as a convenient starting architecture

I do not consider microservices automatically more agent-ready. Often the opposite is true. A well-organized modular monolith gives you a strong combination:

- one codebase;
- one local environment;
- simple transactions;
- fast search;
- explicit domain boundaries.

For a coding agent, this is convenient territory: it can explore the whole system without distributed operational context while still working locally inside a module.

### Microservices and the problem of distributed context

In a microservices architecture, a business flow may span five repositories, a message broker, an API gateway, and a shared schema repository. Each service may be small, but the end-to-end context is distributed. In that case, the agent-ready approach has to exist at the ecosystem level:

- service catalog;
- contracts;
- ownership;
- architecture map;
- versioned schemas;
- distributed tracing;
- links between repositories;
- a clear way to run local integration tests.

A 2,000-line microservice can be harder for an agent than a million-line monolith if understanding one operation requires assembling five disconnected sources.

### Why architectural simplicity is not the same as primitiveness

A simple architecture does not mean “all classes in one folder.” It means the causal relationships can be reconstructed without a large number of hidden assumptions. Sometimes an extra Value Object makes the system simpler. Sometimes a separate adapter makes it simpler. Sometimes an outbox adds code but makes reliability easier to reason about. File count is a poor metric for simplicity.

### How to verify that boundaries exist outside the diagram

Try to violate them. If `Billing\Domain` can technically import `UserInterface\Controller` and nobody notices, the boundary exists only in a presentation. You need architecture tests, dependency rules, static analysis, package boundaries, or at least CI checks. A diagram shows intention; an automated rule proves that the boundary actually exists.

## How to prepare a legacy project for AI agents

The most dangerous idea in legacy work sounds roughly like this: “AI can write so much code now, so let’s ask it to rewrite everything properly first.” I would do the opposite. Legacy systems are rarely hard because they use old syntax. They are hard because they have accumulated implicit contracts, historical exceptions, integrations, strange data, and business behavior that nobody fully documented. A large rewrite destroys exactly the context we have not yet managed to understand. So I would first make legacy code **observable and verifiable** , and only then increase AI autonomy.

### Step 1. Make the project reproducible

The first step is not about LLMs. You need to make sure a new environment can be brought up from documentation and automated commands. If the project only runs on two developers’ laptops, there is nothing for an agent to do autonomously yet. Check:

- how dependencies are installed;
- how the database is started;
- how migrations are applied;
- how test data is created;
- how services are started;
- which environment variables are required;
- which runtime versions are needed.

I would start here even in a project with no AI. Agent-readiness is additional motivation to pay down old operational debt.

### Step 2. Capture current behavior with characterization tests

In legacy code, you often cannot immediately tell whether the existing behavior is correct. But you can capture what it does today. A characterization test does not claim the behavior is ideal. It says: **before the change, the system behaves like this in this scenario**. That gives you a safety net before refactoring. If you ask an agent to clean up a 400-line legacy method with no tests, it may make the code much prettier while changing a ten-year-old edge case. Characterization tests at least create a signal. The important thing is not to fool yourself with coverage. Ten tests around critical business paths are better than a thousand snapshot checks that protect nothing meaningful.

### Step 3. Identify the key business invariants

The next step is to understand what the system must never violate. For example:

- the ledger must balance;
- a paid invoice cannot be deleted;
- an order number must be unique within a tenant;
- a repeated webhook must be idempotent;
- a user cannot see another user’s account;
- a payout cannot be changed locally after it has been sent to the provider.

These are exactly the rules worth lifting out of implicit code into explicit tests, Value Objects, domain methods, and documentation. In other words, we gradually translate knowledge from people’s heads and scattered `if` statements into machine-readable form.

### Step 4. Describe a map of modules and integrations

You do not need to start with a perfect hundred-page C4 model. One map is enough:

```text
HTTP API
  ↓
Orders ─────→ Billing ─────→ ProviderX
  │             │
  │             └──────────→ Ledger
  ↓
Notifications ─────────────→ Email/SMS
```

Add a few sentences explaining the responsibility of each block. The goal is to let the agent answer quickly: “if payout behavior changes, where is the related behavior likely to live?”

### Step 5. Select safe areas for the first tasks

Do not start with core banking logic or production migrations. The first tasks are better chosen where:

- the scope is small;
- tests exist;
- the result is easy to verify;
- there are no destructive side effects;
- no sensitive data is involved;
- rollback is simple.

For example: refactoring a local parser, adding validation, extending unit tests, fixing a well-understood bug in an isolated module. This lets the team learn how to assign work to the agent while also exposing weak spots in the repository.

### Step 6. Add automated checks

Every recurring AI mistake is a candidate for automation. The agent keeps forgetting `strict_types`? Add a check. Creates a dependency from Domain to Infrastructure? Add an architecture rule. Writes unsafe SQL? Add static analysis or a security linter. Forgets to update OpenAPI after changing a DTO? Add a contract check. I like this approach because a bad result from one iteration gradually improves the harness itself.

### Step 7. Introduce instructions and permission boundaries

Only after basic verifiability exists does it make sense to invest seriously in `AGENTS.md`, scoped instructions, and permissions. An instruction without verification is a request. An instruction plus a test is a process. An instruction plus a technically restricted permission is a boundary.

### Step 8. Improve architectural locality gradually

Do not launch a “DDD transformation quarter.” Use real changes as opportunities to improve the system. Touched payment retry? Extract a Value Object and move the invariant. Working on notifications? Document the module’s public contract. Changing reporting? Separate the query model. This way, agent-readiness grows together with ordinary development instead of becoming a separate multi-month project with no business outcome.

### Step 9. Accumulate decision history

After every substantial change, leave a trace:

- atomic commits;
- a useful PR description;
- an updated ADR if the decision is architectural;
- a test if a new invariant appeared;
- documentation if behavior is non-obvious.

We are not just closing the task; we are adding context for the next developer and the next agent.

### Step 10. Increase autonomy only after feedback exists

First, the agent proposes a plan. Then it makes a small patch. Then it runs checks. After that, you can let it implement a constrained task end to end. Later, let it open a pull request. Only after you have enough statistics should you expand the class of tasks it can handle. Autonomy should be a consequence of verifiability, not faith in a new model.

## What a task for an AI agent should look like

A good repository does not eliminate the need for a good task description. More than that: if a human cannot explain the goal of a change briefly, an agent-ready codebase will not save the situation. I like a task template that separates intent, scope, and verification explicitly.

### Goal of the change

Start with one sentence describing the outcome:

```md
Allow customers to retry a failed card payment while the original provider session is still active.
```

Not “refactor payment service.” Not “fix retry.” State the observable goal.

### Business context

Explain why this is needed and which rule stands behind it:

```md
ProviderX keeps a failed payment session active for 30 minutes.
During this period the same transaction may be retried without creating a new external payment.
After expiration retry must be rejected to avoid duplicate charges.
```

Sometimes these three sentences save the agent twenty search calls.

### Task boundaries

What is in scope:

```md
Scope:
- Billing/PaymentRetry use case
- ProviderX adapter
- related unit and integration tests
```

### Acceptance criteria

What must be true after the change:

```md
- failed payment can be retried while provider session is active;
- expired session returns RetryNotAllowed;
- retry reuses original provider transaction;
- existing idempotency behavior remains unchanged.
```

### Non-functional requirements

If performance, security, backward compatibility, or audit logging matter, state them explicitly.

```md
- no public API changes;
- no new database queries in the hot path;
- existing audit event names must remain unchanged.
```

### What must not be changed

A useful block.

```md
Do not:
- change Payment status model;
- modify database schema;
- refactor unrelated ProviderX code;
- update dependencies.
```

It sharply reduces creative scope creep.

### Related modules and documentation

You do not need to hand the agent twenty files in advance if it knows how to search. But it helps to provide starting points:

```md
Start with:
- `src/Billing/PaymentRetry/`
- `src/Billing/README.md`
- `docs/adr/0042-payment-idempotency.md`
```

### How to verify the result

```md
Verification:
1. `make test-billing`
2. `make static-analysis`
3. `make architecture-test`
4. `make verify`
```

### Stop and escalation conditions

This is a part of the task people often forget.

```md
Stop and ask for review if:
- public API must change;
- current tests contradict the task;
- retry requires a database migration;
- ProviderX behavior cannot be reproduced locally.
```

This gives the agent permission **not to guess**.

### Why a good task description matters more than a long prompt

A long prompt often consists of trying to compensate for a poorly defined task with more words. A good task does the opposite: it reduces uncertainty. Goal. Context. Scope. Constraints. Acceptance criteria. Verification. Everything else the agent can collect from an agent-ready repository.

## The full workflow of an AI agent in a prepared codebase

When all the pieces are in place, I like the following workflow.

### 1\. Analyze the task and find related context

The agent does not write code immediately. It first identifies the domain, entry points, and related modules.

### 2\. Study current behavior

It reads production code and tests. If the behavior is unclear, it reproduces it locally.

### 3\. Consult documentation and Git history

If it encounters a strange constraint, it looks for an ADR, docs, `git blame`, and previous commits.

### 4\. Build a change plan

The plan should be small and tied to concrete files and contracts. For example:

```text
1. Add active-session invariant to PaymentRetryPolicy.
2. Reuse existing ProviderTransactionId in ProviderX adapter.
3. Add expired-session unit test.
4. Extend ProviderX integration test.
5. Run Billing verification.
```

### 5\. Have a human review the plan

For low-risk tasks, this step can be skipped. For architectural or sensitive changes, I would still keep it for now.

### 6\. Write or update tests

This does not have to be dogmatically test-first. What matters is that the behavior is captured independently from the implementation.

### 7\. Implement the smallest change

The smallest change, literally: AI makes it easy to generate “while I was here, I also improved this.” I usually want the opposite: the smallest coherent diff.

### 8\. Run automated checks

Start with targeted tests, then run the full verification suite if the cost is reasonable.

### 9\. Self-review the resulting diff

The agent should inspect its own diff as if it were the reviewer:

- does every change relate to the task?
- is there accidental formatting noise?
- did the public API change?
- did new dependencies appear?
- does the code follow the local style?
- were docs and tests updated where needed?

### 10\. Human review

The human no longer checks every brace. They review intent, architecture, security, edge cases, and the quality of the evidence that the change is correct. The cheaper generation becomes, the more expensive review becomes relative to it.

### 11\. Create an atomic commit

The commit message should explain the change and the reason behind it. If the task naturally breaks into several independent steps, the history should preserve that structure.

### 12\. Update documentation and backlog

If a rule changed, update the docs. If a decision was made, update or add an ADR. If technical debt was resolved, update the backlog.

### 13\. Turn recurring agent mistakes into new rules

This is the final feedback loop. If, during review, we write the same comment to AI for the third time, the problem is no longer only the AI. It means the rule is not expressed clearly enough in the repository or harness. Add a lint rule, a test, an instruction, or documentation. Over time, the codebase becomes better trained **not in the sense of fine-tuning the model, but in the sense of improving the environment in which the model operates**.

## What an AI agent should verify on its own

Before handing the result to a human, I would make the agent go through its own checklist.

### The actual diff matches the task

Every changed file should be related to the task. If imports were randomly reordered across a hundred files, remove that noise. If the agent started refactoring a neighboring module “for cleanliness,” restore the original scope.

### Tests pass

Not just write tests, but actually run them. And report exactly what was run. “Tests pass” without the command and result is weak evidence.

### Linter and static analysis results are clean

Tool errors are input for the next repair iteration, not a reason to stop with “it should probably work.”

### Architectural boundaries are respected

Check dependency rules and look for new cross-module imports.

### Public contracts have not changed unexpectedly

APIs, events, schemas, public interfaces, CLI behavior, database contracts. Sometimes a tiny change like renaming a field creates a much larger blast radius than 500 lines of internal refactoring.

### Backward compatibility is preserved

Especially in shared libraries, public APIs, and distributed systems.

### Security and data handling are correct

Permissions, validation, secrets, logs containing PII, SQL, shell commands, deserialization, SSRF, and whatever else is relevant to the particular project.

### Documentation matches the new behavior

If the code says one thing, the test says another, and the README says a third, the task is not done.

### There are no accidental changes outside the task

One of the most useful final questions is:

> If we remove everything that is not required for the acceptance criteria to remain satisfied, what is left in the diff?

That question disciplines both humans and AI.

## Common mistakes when preparing a project

### Trying to put all context into one `AGENTS.md`

The most obvious mistake. The file keeps growing. Every team adds more rules. Six months later it contains architecture, Git workflow, naming conventions, incident history, a service list, deployment instructions, and 80 prohibitions. The root context becomes noise. A small index plus progressive disclosure works better.

### Excessive documentation that repeats the code

Documentation written for its own sake becomes stale quickly. If a `README` manually lists every method of a class, it is almost guaranteed to drift away from the implementation. Document intent, concepts, boundaries, invariants, decisions, and workflows — the information that is expensive or impossible to recover from code every time.

### Contradictory rules

The root file says “all domain errors are exceptions.” The module README says “return Result.” An old style guide says `null`. And the codebase contains all three. AI will choose one. Possibly the wrong one. You need an authority hierarchy: executable checks > current scoped instructions > system documentation > historical documentation. It is better to describe this explicitly.

### Stale plans and backlog

A plan without a status is potential misinformation. Add `status`, `owner`, and `last reviewed`.

### Tests that verify implementation instead of behavior

If a refactoring breaks half the tests while observable behavior stays unchanged, those tests will get in the way of both humans and agents. AI will start preserving accidental implementation details simply because the test suite declared them part of the contract.

### Generating tests with the same agent without independent verification

If the agent misunderstands the requirement, it can write an implementation and a test that agree with each other while both being wrong. Green CI then proves nothing about intent. That is why critical acceptance tests, business invariants, and security checks should have an independent source: the original requirement, an existing test suite, human review, a contract, or an external oracle.

### Methods that are too small and loss of scenario coherence

We already touched on this in the SRP section. Do not turn readability into a scavenger hunt through the call graph. AI is good at following references, but every extra hop is another chance to lose meaning.

### Formal DDD without an actual domain model

Folders called `Domain/Application/Infrastructure` do not give you anything by themselves. If `Domain` contains `DataManager`, `CommonService`, and framework DTOs, the agent gets no semantic benefit. DDD works when the language of the business is actually expressed in code.

### Architectural rules that exist only in documentation

“Do not import X from Y” should be enforced wherever possible. Otherwise, it is advice, not an architectural boundary.

### Blind trust in green CI

CI can be green because the necessary test simply does not exist. Or because the assertion checks the wrong thing. Or because the agent weakened the test along with the code. Checks are evidence only within the scope of what they actually verify.

### Giving the agent excessive permissions

If the task is to fix a unit test, access to production Kubernetes does not make the agent smarter. The principle of least privilege applies literally here.

### Trying to compensate for a weak project with a more expensive model

Sometimes it helps: a stronger model will navigate chaos better. But the economics are strange: you keep paying extra tokens and reasoning cost for architectural debt that could be removed once. It is like hiring a very smart developer and making them rediscover how to run the tests every single day.

## How to tell whether the codebase has become easier for AI to work with

I would not measure success by the number of generated lines. The more mature the agent workflow becomes, the less the raw volume of generation matters. It is more useful to look at the path from task to accepted change.

### The agent finds the change location faster

You can measure time or the number of tool calls before a correct plan is produced.

### The agent reads fewer irrelevant files

If a bug fix used to require opening 60 files and now, after documenting module boundaries, it takes 15, the repository has become easier to navigate.

### Fewer clarification iterations are needed

Not because the agent is forbidden from asking questions, but because the answers are already present in the project context.

### A smaller share of changes fall outside task scope

Scope adherence is a very useful metric.

### Architectural rules are violated less often

Especially when violations are caught before human review.

### More errors are found before human review

An ideal review receives a diff that has already passed compilation, tests, linting, static analysis, and self-review.

### Pull request review time decreases

This is a direct business effect. If the agent generates code twice as fast but review takes three times longer, nothing was accelerated.

### Rollbacks and regressions decrease

Production is always the final metric. A faster merge process with more incidents is not a productivity gain.

### Why generated line count is not a success metric

Lines are the generator’s output. The value is a safe change in system behavior. Sometimes the best AI result is deleting 300 lines. Sometimes it is finding an existing function and writing nothing new. Sometimes it is stopping and saying that the acceptance criteria contradict the current contract. I would measure **accepted changes per unit of human review and production risk** , not generation volume.

## A maturity model for an agent-ready codebase

Instead of turning project preparation into a binary “ready / not ready” checkbox, I find it more useful to think in levels. You do not have to formalize the journey, and not every project needs to reach the highest level. This is simply a way to identify which next improvement will have the greatest effect.

### Level 0. Opaque project

The project only runs for a few developers. A significant amount of knowledge lives in people’s heads. Build and tests depend on the local environment. Documentation is missing or obviously stale. Architectural boundaries are known “by agreement.” In a project like this, AI can be used as autocomplete or a local assistant. I would not rush to give it autonomous repository-level tasks. The main goal at this level is not to add `AGENTS.md`, but to remove magic from the basic development workflow.

### Level 1. Agent-readable

The agent can open the repository, install dependencies, find the main entry points, and read the code. There is:

- a working README;
- a basic project structure;
- setup commands;
- at least minimal documentation;
- an understandable runtime.

At this level, AI can already answer questions about the codebase and make small local changes.

### Level 2. Agent-navigable

The project is not only readable; it helps the agent understand **where to go**. There is:

- a module map;
- local README files or agent instructions;
- clear naming;
- a documentation index;
- explicit entry points;
- links to architecture decisions;
- predictable test locations.

The agent spends less time exploring and is less likely to assemble the wrong context.

### Level 3. Agent-verifiable

This is the turning point. The agent can not only write a patch, but also obtain high-quality feedback on its own:

- tests;
- static analysis;
- linting;
- type checks;
- a reproducible test environment;
- integration checks;
- one clear verification command.

From this point on, delegated tasks become a serious option because a real feedback loop exists.

### Level 4. Agent-constrained

Architectural and operational boundaries begin to be enforced technically. For example:

- architecture tests forbid invalid dependencies;
- CI verifies contracts;
- a sandbox restricts filesystem and network access;
- secrets are unavailable;
- destructive actions require approval;
- scoped instructions apply to specific modules.

The agent does not merely know the rules. It becomes difficult for it to violate them accidentally.

### Level 5. Agent-operable

The agent can take a well-described constrained task, investigate context, propose a plan, change code, update tests and docs, run verification, and produce a pull request. A human remains the reviewer and owner of the decision. This is already a full production workflow, but it is not “an autonomous developer with no humans.” It is a new executor inside a managed engineering process.

### Level 6. Agent-adaptive

The most interesting level is when the process can improve its own environment. A recurring review comment becomes a lint rule. A production regression becomes a characterization test. A confusing architectural decision becomes an ADR. A navigation failure becomes a module map. An ambiguous instruction becomes a scoped rule. Experience from working with the agent gradually becomes new structure in the repository and harness. This is one of the strongest effects AI can have on engineering. We stop fixing individual outputs every time and start improving the system that produces those outputs.

## Agent-ready codebase checklist

Below is a checklist you can literally run through on an existing project. You do not have to satisfy every item before using AI for the first time. I would instead mark weak areas and improve them in order of risk and frequency of change.

### History and change management

- [ ] Commits have a clear scope and reason for the change.
- [ ] Git history is not dominated by `fix`, `wip`, and `misc`.
- [ ] `git blame` can lead to a meaningful commit or PR.
- [ ] Large changes are broken into logical steps.
- [ ] Non-obvious changes reference an issue, incident, or ADR.
- [ ] The team understands when squash preserves meaning and when it destroys useful history.

### Architecture and domain model

- [ ] Major modules are named explicitly.
- [ ] The responsibility of each module can be explained in a few sentences.
- [ ] Business terminology is consistent across tasks, code, and documentation.
- [ ] Critical invariants are expressed in domain code or tests.
- [ ] Dependencies between layers are understandable.
- [ ] Critical architectural boundaries are checked automatically.
- [ ] Module public surfaces are separated from implementation details.
- [ ] Critical paths do not rely on large amounts of unexplained framework magic.

### Documentation

- [ ] The repository has an up-to-date entry point for developers.
- [ ] There is an architecture or module map.
- [ ] Documentation lives close to the code or is accessible to the agent through tools.
- [ ] Significant decisions are captured in ADRs or an equivalent format.
- [ ] Documentation explains reasons instead of merely repeating implementation.
- [ ] Documents have an owner/status where information becomes stale quickly.
- [ ] Root instructions are compact and link to more detailed documents.
- [ ] Local rules live close to the relevant module.

### Testing

- [ ] Key business scenarios have tests.
- [ ] Legacy behavior is captured with characterization tests before refactoring.
- [ ] Tests read like scenarios rather than collections of implementation details.
- [ ] Arrange/Act/Assert are distinguishable.
- [ ] One test protects one logical outcome.
- [ ] Critical acceptance criteria have independent verification.
- [ ] Tests can be run reliably locally.
- [ ] Flaky tests are not considered normal.
- [ ] Test failures provide enough information to act on.

### Automated checks

- [ ] There is a formatter or format check.
- [ ] There is a linter.
- [ ] Static analysis/type checking exists where appropriate.
- [ ] Architecture checks exist for important boundaries.
- [ ] API/event/schema contracts are verified.
- [ ] Security checks are integrated into CI for critical classes of errors.
- [ ] There is one command for the main verification suite.
- [ ] Tool errors are written clearly enough to act on.

### Task definition and storage

- [ ] Every task has a concrete goal.
- [ ] Business context is included.
- [ ] Scope is defined.
- [ ] Acceptance criteria are verifiable.
- [ ] Constraints and non-goals are stated.
- [ ] It is clear which parts of the system must not be changed.
- [ ] Complex tasks have useful starting points.
- [ ] Stop conditions and escalation paths to a human are defined.
- [ ] The backlog does not mix decisions, plans, and hypotheses.
- [ ] Outdated plans are removed or clearly marked.

### Local environment

- [ ] Setup is reproducible from a clean environment.
- [ ] Runtime and dependency versions are pinned.
- [ ] The test database is created automatically.
- [ ] Fixtures or seed data are available without production data.
- [ ] External services can be replaced with test doubles or local equivalents.
- [ ] There are no required hidden manual steps.
- [ ] The agent can run the relevant part of the application in a sandbox.

### Observability

- [ ] Logs are structured and suitable for local analysis.
- [ ] Bugs can be reproduced without production access.
- [ ] Traces or correlation IDs are available for complex flows.
- [ ] There are test-friendly ways to verify external side effects.
- [ ] Debugging does not require real customer secrets or data.

### Security

- [ ] The agent operates according to the principle of least privilege.
- [ ] Production credentials are unavailable by default.
- [ ] Network access is limited to what the task requires.
- [ ] Destructive commands require separate confirmation or are technically blocked.
- [ ] Sensitive paths have additional rules.
- [ ] IAM, billing, security, and production infrastructure changes require human review.
- [ ] Agent actions can be audited.

### Human review and ownership

- [ ] Every merged change has a clearly defined human owner.
- [ ] The reviewer can see which checks the agent actually ran.
- [ ] AI-generated tests are not treated as independent proof on their own.
- [ ] Review checks intent and scope, not just syntax.
- [ ] The team tracks regressions after agent-generated changes.
- [ ] Recurring mistakes are turned into tests, rules, or documentation.

If roughly half the items on this list are checked, that does not mean “the project is 50% ready.” Different items carry different weight. In a financial core system, missing permission boundaries may matter more than a perfect style guide. For a small internal utility, a reproducible environment and good tests may provide almost all of the value. The checklist is a risk map, not a certification system.

## Frequently asked questions

### Is `AGENTS.md` mandatory?

No. The filename is a detail of a particular toolchain. Codex and GitHub Copilot coding agent can work with `AGENTS.md`; other tools use their own formats. What matters is the principle: the agent should have a compact repository-level instruction file containing navigation, commands, and boundaries. I would not build the process architecture around one vendor-specific filename. It is better to maintain canonical documentation and use a small adapter file that points to it.

### Do you need vector search over the codebase?

Not necessarily. For small and medium repositories, good text and symbol search may be enough. Semantic retrieval becomes more useful when the repository is large, terminology drifts, or knowledge is scattered across many files. At the same time, repository-level code-generation research suggests that simple similarity search is not the end state. Dependencies and structural context may matter more than textual similarity. I would first improve structure and ordinary navigation, and only then try to solve the remaining problem with embeddings.

### Can AI document a project by itself?

It can help, especially with the first draft. But the same problem appears here as with generated tests: AI can describe **how it understood the system** very convincingly, which is not necessarily the same as how the system was intended to work. A useful workflow is to let the agent assemble documentation from code, tests, and Git, then have the domain owner review it and commit it like any other change. After that, the document becomes part of the source base and is maintained together with the code.

### Which tests are most useful for coding agents?

The ones that provide fast, stable, and meaningful feedback. For a local domain change, that means unit tests. For database and integration behavior, integration tests. For public contracts, contract tests. For old undocumented behavior, characterization tests. For critical user flows, a small number of end-to-end tests. There is no single “AI-friendly type of test.” What matters is that the test protects real behavior and that a failure explains the problem.

### Should every class, method, and test be documented?

No. I would deliberately avoid doing that. Document the places where the code does not make important information obvious: the business reason, invariant, side effect, exception, or historical constraint. If a comment can be deleted without losing anything, it is probably unnecessary.

### Does DDD help AI agents write code?

I would not claim there is a universal study saying “DDD improves coding-agent quality by X percent.” At least, I do not build this article around such a claim. But the engineering causality is straightforward: Ubiquitous Language reduces terminological ambiguity, Bounded Contexts define scope, Aggregates localize invariants, and Value Objects make constraints explicit. All of this reduces the amount of hidden context. In other words, DDD is useful to AI for the same reasons it is useful to people working in a complex domain.

### Should you change an existing architecture specifically for AI?

I would not do it just for AI. If a change improves locality, testability, explicitness, and human onboarding, then AI-readiness becomes an additional benefit. I like a simple filter here: **if a practice helps only the agent and makes the project worse for humans, think carefully about why you need it**.

### Can good documentation replace tests?

No. Documentation explains intention. A test provides executable evidence of concrete behavior. You can write “retry is forbidden after expiration” ten times, but only a test will actually catch an accidental change to the condition. And the reverse is also true: a test can capture behavior without explaining why that behavior exists. These sources complement each other.

### Can an AI agent work with a project that has a messy Git history?

Of course. Git history is an additional source of context, not a prerequisite for starting. But you lose the historical layer. This is especially noticeable in legacy systems with many strange constraints. If the history is already bad, I would not rewrite the past just for AI. I would simply start creating a useful history from this point forward and capture critical old decisions in ADRs and tests as the relevant code is touched.

### How do you prevent documentation and backlog from going stale?

Tie updates to the normal workflow. Documentation changes in the same PR as behavior. ADRs have a status. Plans have a date and an owner. Deprecated docs are deleted. CI can check broken links and schemas. The worst solution is to create a large “AI knowledge base” that nobody on the team actually uses. Six months later, it will be a beautifully organized collection of lies.

### How much context should be passed to the agent?

The minimum sufficient amount: there is no universal token count. Good context is not the biggest context; it is the context after which the agent can make the next correct engineering decision. Start with the task + root instructions. Then module docs. Then code and tests. Git and ADRs only when needed. That is progressive disclosure.

### When can an agent be allowed to create pull requests on its own?

When the same class of tasks has repeatedly gone through a stable cycle:

- scope is clear;
- the environment is reproducible;
- verification is reliable;
- permissions are restricted;
- review shows acceptable quality;
- production regressions are not increasing.

The release of a new, stronger model is not by itself a reason to increase privileges.

### Can an agent-ready project operate without human review?

For some low-risk tasks, possibly. Generated documentation, mechanical formatting, or certain dependency updates can be good candidates when automated verification is very strong. But for business-logic changes, I still see human review as part of ownership. A model can prove that the tests are green. A human should make sure that we are solving the right problem in the first place and are willing to own the consequences.

## An agent-ready codebase is still a good codebase for humans

This is the main conclusion I reached while putting everything together. We do not need a separate kind of “code for AI.” We need a project whose meaning depends less on telepathy. A project that can be started from instructions. Where names match the domain. Where tests protect behavior. Where architectural decisions have reasons. Where Git tells a story. Where an important rule is either obvious from the type system or enforced automatically. Where a major plan does not exist only in one person’s head. AI turned out to be an effective test of the quality of this environment.

A person joining the team does not know your system either. They also need a map. Good names, tests, docs, and history help them too. They also do not want to spend three days figuring out how to run one worker locally. Preparing a repository for agents therefore improves onboarding, review, and maintenance for the human team at the same time.

### AI does not make engineering practices obsolete; it makes their value more visible

Over the last few years, it has sometimes felt as if stronger models would gradually eliminate parts of software engineering. So far, I see almost the opposite. The cheaper it becomes to write a change, the more important it becomes to:

- define boundaries correctly;
- preserve intention;
- verify the result;
- prevent accidental scope expansion;
- understand consequences.

Code becomes cheaper. Engineering understanding does not.

### Preparing a project for agents also improves team onboarding

If an agent can understand a repository in a few minutes because the structure is good, a new developer will ramp up faster too. If `make verify` works for the agent, it works for a human. If an ADR explains a strange decision to the agent, it will explain it to a reviewer a year later. If an architecture test prevents AI from violating a boundary, it will also stop a developer from doing the same thing on a Friday evening. Agent-ready engineering is not a separate discipline sitting next to software engineering. It is ordinary engineering with a very demanding new consumer of context.

### Autonomy starts with system verifiability, not trust in the model

When we ask “can we trust an agent with this task?”, the question sounds too psychological. Trust does not scale well. It is more useful to ask:

- can we constrain the scope?
- will we notice an incorrect change?
- will tests catch a behavioral violation?
- will an architecture rule stop a forbidden dependency?
- is there an audit trail?
- can the result be rolled back safely?

The more mechanisms like these exist, the less autonomy depends on belief.

### The codebase should store not only implementation, but engineering intent

This is where almost every part of the article converges. Implementation without intention forces the next reader to guess. Intent can be stored in many forms:

- a domain object name;
- a type;
- a test;
- a commit message;
- an ADR;
- a comment;
- a lint rule;
- task acceptance criteria.

No single format solves everything. But together they create a system capable of explaining not only **what was written** , but also **why**.

## Final thesis

When the first strong coding assistants appeared, the main question was: “how well can AI write code?” With coding agents, the question is gradually changing. **How well can our project be understood?** We can keep switching models, expanding context windows, and buying more tokens. All of that will help. But at some point, the bottleneck is no longer the agent’s intelligence. It is the entropy of the system itself.

My approach is conservative. I am not trying to redesign software engineering around AI. I take practices that already helped keep systems under control and make them more explicit: atomic Git history, class and test documentation, AAA, SRP, DDD, docs-as-code, backlog discipline, linters, and a style guide. Then I add what an agent workflow specifically needs: `AGENTS.md`, progressive disclosure, a reproducible environment, a single verification command, scoped permissions, and explicit stop conditions. The result is not some special “AI architecture,” but a codebase that can be understood and changed safely.

> A well-prepared codebase becomes the AI agent’s external memory. Git preserves the history of decisions, DDD reveals meaning, documentation explains the reasons, tests capture behavior, the backlog shows direction, and linters and CI define the boundaries of acceptable change.

And that is the best criterion for an agent-ready project: if the model becomes twice as capable tomorrow, you will not have to redesign the whole system for it. You will simply give a stronger agent the same well-organized engineering context.

## Research and references

Below are the sources I relied on for the research and tooling parts of the article. I deliberately did not try to turn the text into an academic review: these papers are here to validate individual claims, not to replace engineering experience.

1. Nelson F. Liu et al. **Lost in the Middle: How Language Models Use Long Contexts** — a study of how models use information inside long contexts.  
https://arxiv.org/abs/2307.03172

2. Fengji Zhang et al. **RepoCoder: Repository-Level Code Completion Through Iterative Retrieval and Generation** — iterative retrieval for repository-level code completion.  
https://aclanthology.org/2023.emnlp-main.151/

3. Carlos E. Jimenez et al. **SWE-bench: Can Language Models Resolve Real-World GitHub Issues?** — a benchmark of real software-engineering tasks that require repository-level changes.  
https://arxiv.org/abs/2310.06770

4. **GraphCoder: Enhancing Repository-Level Code Completion via Coarse-to-fine Retrieval Based on Code Context Graph** — structural retrieval using a code context graph, ASE 2024.  
https://ieeexplore.ieee.org/document/10765009/

5. Zhongxin Liu et al. **Effective and Efficient Context Retrieval via Partial Dependency Graph for Repository-Level Code Generation** — dependency-aware retrieval, ASE 2026.  
https://arxiv.org/abs/2608.01927

6. Chao Hu et al. **In Line with Context: Repository-Level Code Generation via Context Inlining** — use of upstream/downstream context for repository-level generation, FSE 2026.  
https://arxiv.org/abs/2601.00376

7. Greta Dolcetti et al. **Helping LLMs Improve Code Generation Using Feedback from Testing and Static Analysis** — using feedback from tests and static analysis to improve generated code.  
https://arxiv.org/abs/2412.14841

8. Noble Saji Mathews, Meiyappan Nagappan. **Test-Driven Development for Code Generation** — experiments that include tests together with the task specification.  
https://arxiv.org/abs/2402.13521

9. OpenAI. **Introducing Codex** — repository instructions through `AGENTS.md`, configured development environments, and verification.  
https://openai.com/index/introducing-codex/

10. OpenAI. **Running Codex safely at OpenAI** — boundaries, constrained execution, network policies, and telemetry for coding agents.  
https://openai.com/index/running-codex-safely/

11. GitHub. **Copilot coding agent now supports AGENTS.md custom instructions** — root and nested instructions for the coding agent.  
https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
