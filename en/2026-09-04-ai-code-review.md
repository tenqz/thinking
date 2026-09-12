---
date: 2026-09-04
author: Oleg Patsay
slug: ai-code-review
excerpt: "AI has made code generation cheaper, but not understanding. Review shifts from syntax to intent, scope, architecture, business invariants, failure paths, and whether the code should exist at all."
---

# AI Code Review: What to Check in AI-Generated Code

Over the last couple of years, writing code has become noticeably easier. Not in the familiar sense where a new framework appears and five files can suddenly be replaced with one. The cost of producing code itself has changed. I can describe a task to an agent, go review another pull request, and come back a few minutes later to an implementation, tests, a migration, and a couple of extra files nobody particularly asked for.

At first glance, this looks like a fairly straightforward productivity gain. If a developer used to spend several hours on a change and now gets it in twenty minutes, development should speed up by roughly the same factor. In practice, it quickly turns out that writing code was only one part of the system.

The code still has to be understood.

Someone has to verify that it solves the right problem, does not break the old one, fits the architecture, does not duplicate an existing implementation, does not introduce an unnecessary dependency, and was worth adding to the project in the first place. Later, someone will maintain it, change it, and eventually debug it at night during an incident.

AI has dramatically reduced the cost of generation, but it has barely reduced the cost of understanding. The more code we can produce per unit of time, the more visible that gap becomes.

That is why I think code review is becoming more important in the AI era, not less. We just need to review slightly different things.

## Code is no longer naturally expensive

Writing code used to have a useful built-in brake. To add another abstraction layer, a developer had to come up with it, write the interfaces, implement it, test it, and then deal with the consequences. The cost of the decision at least occasionally forced you to stop and ask whether the new code was actually necessary.

With an agent, that constraint has almost disappeared. Asking for another service, adapter, or mapper costs almost nothing. If you do not like the first implementation, you can get a second one in a minute. Then a third. Generating five hundred lines can now be easier than carefully reading fifty lines that already exist.

And this gradually changes the codebase.

Research on AI-assisted development already points to a fairly predictable effect: developers produce more pull requests and more changes, and review load grows with them. GitClear has also reported more duplication and less reuse of existing code in AI-heavy workflows. The reason seems fairly obvious to me.

For a model, it is often easier to complete a task locally by writing new code than to understand which existing abstraction should be extended or which lines could simply be deleted.

A developer is at least occasionally too lazy to write yet another class.

AI is never too lazy.

So the first question in review increasingly should not be “is this code written correctly?” but “why does this code exist at all?”

## I would not start a review at the top of the diff

When you open a neat pull request, it is natural to read the changes from top to bottom. Especially when the diff is well structured, methods are short, variable names are clear, and tests sit right next to the implementation. AI is very good at creating exactly this feeling of completeness.

With agent-generated changes, I would do the opposite and avoid looking closely at the implementation at first. I would reconstruct the original task.

What were we trying to change? What were the acceptance criteria? Where was the intended boundary of the change? What explicitly should not have changed? Which existing system constraints had to remain intact?

Suppose the task was to fix timeout handling in an external API, but the pull request changes twelve files, introduces an abstraction for all external clients, and rewrites the retry policy at the same time. Maybe that really is a good idea. But the author of the change should explain why that scope is necessary; the reviewer should not have to discover it after half an hour of reading code.

This happens especially often with AI because it is easy to give an agent a prompt like:

> Fix the problem and clean up the code while you're there.

A few minutes later, you get a mixture of bug fix, refactoring, and new architecture in a single diff. It may even work. But reviewing it becomes much harder because the necessary change is mixed with improvements that appeared along the way.

So before reading the implementation, I would check three things: intent, scope, and necessity.

If those are unclear, it is too early to discuss details.

## The most useful question: should this code exist at all?

AI almost always proposes writing something. That is natural: you asked it to solve a problem with code, so it generates code.

But good engineering surprisingly often means not adding a new implementation.

Sometimes the required function already exists in a neighboring module. Sometimes one existing abstraction can be extended. Sometimes a new class exists only because the model failed to find the old one. Sometimes the condition can be expressed in configuration. And sometimes the correct change actually reduces the amount of code.

This is something I now check separately in AI-generated diffs.

Suppose the agent adds:

```php
final class UserAccessValidator
{
    public function canViewInvoice(User $user, Invoice $invoice): bool
    {
        return $invoice->userId() === $user->id();
    }
}
```

Locally, the class looks fine. The name is clear, the method is small, and writing a test for it is easy.

Then you discover that the project already has an `InvoiceAccessPolicy` containing all the other invoice access rules. The new code is not wrong in the conventional sense. It may work perfectly.

The problem is that it should never have existed.

This is one of the more unpleasant properties of AI-generated code: the model can produce a very good local implementation that makes the system worse as a whole.

During review, I would therefore explicitly look for:

- existing logic that could have been reused;
- nearly identical abstractions;
- new classes with one trivial responsibility;
- helpers that have been reimplemented;
- new layers introduced only for the current ticket;
- places where modifying existing code was replaced by adding new code.

The principle that less code is usually easier to maintain has not gone anywhere. It has simply become harder to follow because extra code is almost free at generation time.

## Local correctness does not make a good change

Most automated checks are good at answering local questions. Does the project compile? Do the tests pass? Are there type errors? Has static analysis found a violation?

All of that is useful, and it should happen before human review.

But the most expensive mistakes are usually one level higher.

Imagine the requirement:

> A user must never be able to access an invoice that belongs to another tenant.

AI might write:

```php
$invoice = $invoiceRepository->find($invoiceId);

if ($invoice->tenantId() !== $currentTenant->id()) {
    throw new AccessDeniedException();
}
```

Functionally, the check exists.

But the architectural rule of the system may be that objects belonging to another tenant must never cross the repository boundary at all:

```php
$invoice = $invoiceRepository->findForTenant(
    $invoiceId,
    $currentTenant->id()
);
```

Both implementations may pass the tests. The first may even look more obvious.

But the second preserves a system invariant: data from another tenant never appears above a certain application layer.

A model rarely knows these things on its own. Even with good documentation, a mature codebase contains a huge number of conventions that have never been properly written down. The team simply knows where authorization belongs, how transactions are structured, which services are allowed to talk to each other, and which data must never cross bounded contexts.

That is why human review increasingly shifts toward architectural context.

The question is not only “does this method work?” but “is this logic even located at the right level of the system?”

## Business invariants deserve a separate review pass

There is another class of rules that is especially easy to miss: business invariants.

For example:

```text
An invoice cannot be edited after settlement.

A payment operation must be idempotent.

A user from one tenant must never see another tenant's data.

An order cannot return to draft status after it has been shipped.

A balance must not fall below a defined limit.
```

Rules like these are often spread across code, tests, documentation, and people's heads. AI can implement a specific ticket perfectly without understanding one of those constraints at all.

And the happy path will work.

Suppose we need to retry a payment after a network timeout. The agent implements retry logic, tests pass, and the API behaves correctly. But if the external provider processed the first request and merely failed to return the response, the second request creates a duplicate operation.

The syntax is correct.

The test suite may be green.

The ticket appears complete.

But the central invariant of the payment system has been violated.

That is why I find it useful to separate implementation correctness from system behavior correctness during review. The more code is generated automatically, the more important it becomes for someone to remember which properties of the system must never be broken.

## AI is much more eager to write the happy path

If you ask a model to implement an API endpoint, the main scenario usually appears quickly. The request is valid, the object exists, the external service responds, the database is available — everything is fine.

The more interesting questions are around it.

What happens on timeout?

What if the external service responds twice?

What if the transaction rolls back after a successful HTTP call?

What happens under concurrent requests?

Can the operation be retried safely?

What happens to partially persisted data?

What if the response is empty?

Is there a retry limit?

Do logs contain sensitive data?

Failure paths are often what separates an implementation that “works on my machine” from code that can survive several years in production.

AI amplifies an old human problem here. Developers have always liked writing the happy path first. The difference is that now it appears so quickly and looks so complete that it is tempting to treat it as an almost finished solution.

After understanding the main logic, I would deliberately switch into destructive mode:

> What has to happen for this code to stop working?

Then I would look for that place in the implementation.

## Error handling sometimes looks better than it works

AI has another unpleasant habit: it likes to make code look resilient, at least visually.

For example:

```php
try {
    return $client->request();
} catch (\Throwable $e) {
    $logger->warning($e->getMessage());

    return null;
}
```

The error is handled.

The application does not crash.

Everything looks tidy.

Except now the caller has no way to distinguish “there is no result” from “the network failed.” The actual error has been masked.

Or the agent adds:

```php
catch (\Exception $e) {
    // fallback
}
```

and returns an old value because that makes the tests pass and the scenario look more “robust.”

These constructs need to be reviewed semantically, not aesthetically. Should this exception be caught here at all? Who should decide whether to retry? Can the caller safely continue? Are we turning a real failure into a subtle invalid state?

GitClear has also reported growth in error-masking patterns in AI-heavy codebases. That does not surprise me. To a model, a caught exception often looks more complete than an exception deliberately propagated upward.

Production code does not have to look calm.

Sometimes the correct behavior is to fail loudly.

## Dependencies now need explicit verification

Dependencies have become their own category of risk.

AI can confidently suggest a library that looks realistic, has a plausible name, and appears to solve exactly the problem at hand. Sometimes the library exists. Sometimes it exists but is no longer maintained. Sometimes the API has changed. Sometimes the package is entirely fictional.

For application code, I would treat every new dependency as a separate review item.

Do we need it at all?

Does the package actually exist?

Who maintains it?

When was the last release?

What license does it use?

How many transitive dependencies does it bring in?

Could the task be solved with the standard library or a package we already use?

I am especially suspicious of dependencies introduced for small utility tasks. AI often solves ten lines of code by installing another package because that pattern appears constantly in training data.

In a mature system, a new dependency is not just one line in `composer.json` or `package.json`. It is another external component that someone has to update, scan for vulnerabilities, and account for during future migrations.

I would not approve a dependency simply because the agent wrote a confident installation command.

## Tests written by AI were still written by AI

One of the most misleading pull requests is the one where AI writes both the implementation and a beautiful test suite for it.

Psychologically, it looks strong. There is code, there is coverage, everything is green. The task seems closed from every angle.

The problem is that the implementation and the tests may have been born from the same wrong assumption.

Suppose the requirement says:

> The discount is valid until the end of September 10.

AI interprets it as:

```text
expires_at < 2026-09-10 23:59:59
```

and writes a test for exactly that behavior.

If the real business rule means “through the entire day in the user's local timezone,” the code and the test will agree perfectly with each other and be wrong in exactly the same way.

That is why I review AI-generated tests almost like production code.

What exactly does this test prove?

Does it validate the requirement, or merely mirror the implementation?

Is there a negative case?

Are the boundaries covered?

What happens one second before and one second after the boundary?

Is there a failure scenario?

If production code and tests were produced by the same agent in the same context, the existence of tests is still fairly weak evidence of correctness by itself.

A good test should be an independent source of requirements, not an explanation of the generated implementation.

## AI-specific smells

Over time, AI-generated changes develop some recognizable smells.

The first is duplication. The agent failed to find existing logic and wrote its own.

The second is unnecessary abstraction. One operation gets an interface, implementation, factory, and another mapper between them because that looks architecturally serious.

The third is excessive defensive code. Checks for states that are impossible by contract, nullable values where a value is mandatory, and `try/catch` around everything.

The fourth is comments that explain the obvious:

```php
// Check if user exists
if ($user === null) {
```

The fifth is a new utility function next to an almost identical old one.

The sixth is a deprecated pattern, or simply one that does not match the project. The model has seen enormous amounts of code from different eras and can confidently bring a ten-year-old solution into a modern codebase.

The seventh is over-generalization. The ticket asked for one concrete capability, and the agent built a framework for the next ten hypothetical cases.

None of these signals means the code is bad on its own. But when several appear together, I start looking much more carefully at whether the agent understood the surrounding system at all.

## Everything deterministic should be checked before a human sees the PR

A human reviewer should not manually compensate for every weakness of AI.

If an error can be found automatically, it should be found automatically.

Before review, I want to see:

```text
formatter
lint
type checking
unit tests
integration tests
static analysis
security scanning
dependency scanning
```

Depending on the project, this may also include architecture tests, API compatibility checks, migration checks, and other deterministic gates.

There is no reason to spend human attention on formatting or an obvious type error when a machine can find it in a second.

I like to divide verification into two layers.

The first answers questions that can be formalized:

```text
Does it compile?

Do the tests pass?

Is a static-analysis rule violated?

Is there a known vulnerability?

Did the API contract change?
```

The second requires judgment:

```text
Is this the right solution at all?

Do we need this code?

Is the boundary well chosen?

Does the change fit the architecture?

Is the complexity trade-off worth it?
```

The more routine implementation moves to AI, the more important the second layer becomes.

In practice, the reviewer gradually spends less time checking how code was written and more time evaluating the engineering decision.

## Pull request size now has to be constrained deliberately

There is another problem that used to be partially limited by developer speed.

Large pull requests take a long time to write.

So changes at least occasionally broke into smaller pieces naturally.

An agent can modify twenty files, add a thousand lines, and provide a convincing explanation for every one of them in a single run. Its generation speed has no relationship whatsoever to the reviewer's ability to understand those thousand lines.

Human cognitive bandwidth did not increase along with generation throughput.

That makes the old rule of keeping pull requests small even more important in AI-assisted development.

I would not let the agent's speed determine the size of the change.

If a task consists of three independent steps, I would rather create three reviewable changes even if AI could technically implement all of them in one session.

A large diff is not dangerous simply because it contains many lines. The problem is the number of states and decisions a reviewer has to keep in working memory at the same time. The larger the scope, the easier it is to miss one small assumption that later becomes the main source of failure.

One of the most useful optimizations in an AI workflow may therefore be rather boring: generate fast, merge in small pieces.

## Can AI review AI?

Of course.

And it is already useful.

You can give a pull request to another agent and ask it to find bugs, review security, identify missing tests, or compare the change with the task description. GitHub, Sonar, and other tools are actively developing automated AI review.

I would just avoid treating that review as independent proof of correctness.

A model reviewing another model's code is still subject to many of the same limitations. It may not know a hidden business invariant, may miss an architectural constraint, or may agree with a very convincing but incorrect solution.

AI review works well as an additional layer.

For example:

```text
AI writes the change
        ↓
tests / static analysis
        ↓
AI first review
        ↓
human review
        ↓
merge
```

AI can cheaply catch some obvious problems before a pull request reaches a human. That is useful.

But I would not build this pipeline:

```text
AI wrote it
↓
AI approved it
↓
production
```

when the cost of a mistake is meaningful.

Probabilistic verification of one probabilistic output by another probabilistic system is not the level of confidence I want for critical code.

## Who is the author of such a change?

After several months of working with coding agents, I care less and less about who physically typed a particular line.

If I gave the agent a task, it wrote the class, I reviewed the change, and I shipped it to production, the system does not care what percentage of the text I typed manually.

What matters much more is who decided that this code was acceptable to merge.

AI can propose a solution. It can implement it. It can add tests and perform the first review itself.

But responsibility for the change still belongs to the team.

I think that is a useful boundary.

Otherwise, there is a very convenient psychological trap:

> I didn't write it. AI did.

Production does not become easier because of that.

If a change breaks payments, architecture, or user data, nobody cares much which autocomplete produced the code.

I treat AI-generated code roughly like code from an extremely fast developer who knows a huge number of technologies, never gets tired, does not live inside our system, and occasionally invents details with complete confidence.

You can delegate production to that developer.

You cannot automatically delegate judgment.

## What I now check in an AI-generated PR

If I reduce the whole process to a short sequence, mine looks roughly like this.

First, I check the task and the scope. What were we trying to change, and why did the diff become this large?

Then I check whether the new code is necessary. Could we have reused an existing implementation? Did we introduce duplication? Are we building an abstraction for a single case?

Then comes architecture and business invariants. Is the logic at the right level? Are boundaries preserved? Did we violate a system rule the agent simply could not have known?

After that, I review failure paths and security: errors, retries, transactions, concurrency, permissions, and sensitive data.

I review new dependencies and tests separately, especially tests generated together with the implementation.

Anything that can be checked deterministically should not consume time during human review. CI exists for that.

Only then do I get to the familiar work of readability, naming, and small implementation improvements.

The order looks roughly like this:

```text
Intent
↓
Scope
↓
Necessity
↓
Architecture
↓
Business invariants
↓
Failure paths
↓
Security
↓
Dependencies
↓
Tests
↓
Implementation details
```

I like the fact that syntax and formatting are somewhere outside this list entirely.

That is probably where they belong.

## Instead of a conclusion

AI did not make code review obsolete. It changed the economics around it.

Code can now be produced much faster than a team can carefully understand it. If review remains a line-by-line correctness check, it becomes very easy to build a pipeline that produces more and more neat, tested, formally correct code while the system itself becomes steadily more complicated.

The most important part of review therefore moves upward.

Not “is this `if` written correctly?”

Why does this new service exist?

Why did the change touch eight files?

Why could we not reuse the existing abstraction?

Which invariant does this check preserve?

What happens under partial failure?

And who is prepared to say that this exact change is worth keeping in the system?

In a way, code is becoming the cheap part of software development again.

Understanding remains expensive.

And the better AI becomes at writing code, the more engineering work seems to move precisely there.

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
