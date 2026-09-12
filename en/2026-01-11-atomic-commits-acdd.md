---
date: 2026-01-11
author: Oleg Patsay
slug: atomic-commits-acdd
excerpt: "What an atomic commit is, how to define its boundaries, write useful commit messages, keep Git history clean, and stay in control of AI-generated changes."
---

# Atomic Commits and ACDD: Git Workflow for AI Development

In this article, I want to share a way of working that I arrived at after years of building different systems. I am not the first developer to talk about atomic commits. There were developers before me, and I am sure there will be developers after me. I am not asking you to rewrite the history of every repository immediately or introduce a new team policy next Monday. I simply collected a set of arguments that seemed important enough to turn into a more explicit approach.

I call it ACDD — Atomic Commit Driven Development. In the simplest terms, you first define the next complete step, then do only that step, verify the result, and create a commit. The cycle looks like this: **thought → definition → action → verification → commit**. It does not sound complicated. Creating a commit is easy. The real question is what exactly you put into it.

Somewhere, at some IT company, a new developer once arrived and squashed the entire main branch history into a commit called `legacy code`. Do not do that. It is an extreme example, but everyday work is often not much better: `wip`, `fix`, `temp`, “tweaked authorization a little.” You open the commit and find a new feature, refactoring, dependency upgrades, tests, two typo fixes, and a forgotten debug print. Be honest: have you done this? I have. Everyone has. That does not mean we have to keep doing it.

## Why Git history turns into a dump

Developers try to keep order in code, architecture, tests, and documentation. We argue about method names, module boundaries, and how many responsibilities a class should have. Yet Git history often remains outside that engineering discipline.

A commit is treated as the final formality. First, solve the task; then somehow save the changes and write a message. By then, the working directory may contain everything that happened over several hours. We have to look at the file list and remember what we actually did. It is a slightly strange process: first we work, and then we reconstruct the meaning of that work from the traces left behind.

### One large task, one commit, thousands of changed lines

I used to enjoy getting into a flow state, sitting down with a task, and moving toward the result for six or seven hours without interruption. You can get a lot done in that time. At the end, the task works, the tests are green, the diff contains dozens of files and thousands of lines, and everything goes into one commit.

For the author, the change is obvious. They just wrote the code and still remember why they moved the class, changed the interface, added a table, updated the docs, and fixed an old method along the way. In their head, it is one task. For another developer, it is a large batch of decisions delivered all at once.

### Why it is convenient for the author and expensive for the reviewer

To review a large diff, the reviewer has to rebuild the context, understand the existing architecture, identify the actual goal, connect changes across dozens of files, and only then evaluate individual decisions. When functionality, refactoring, and incidental fixes are mixed together, the reviewer has to switch continuously between different reasons for change.

I do not think that is a fair trade. The author saves time by not separating the work, and the reviewer — sometimes several reviewers — pays for that saved time later. Research on code review confirms a fairly intuitive point: the size and complexity of a change affect cognitive load and defect-detection effectiveness. In an [experiment with 50 developers](https://sback.it/publications/emse2019a.pdf), larger and more complex changes were associated with lower effectiveness at detecting some classes of defects. This does not mean every large diff is bad. But if it contains several independent ideas, the reviewer has to separate them mentally. We could have done that in advance.

### Git history reflects engineering thought, not just code

Someone always reads code, even if that someone is you a month later. Git history gets read too: through `git log`, `git blame`, pull requests, regression investigations, or attempts to understand why the system is designed the way it is.

A good history does not need to preserve every doubt and failed attempt. It should preserve the logic of accepted decisions: where we started, what step we took, and why the system ended up in its current state. Git history should reflect the movement of engineering thought, not the developer's level of exhaustion at the end of the day.

### AI accelerates code writing, but not understanding

AI-assisted coding makes the problem more visible. In a few minutes, we can now produce a volume of changes that used to take hours. But a human still has to read that code, verify it, and take responsibility for it.

AI scales not only speed but habits. If a developer defines the task boundary well, the tool helps them move through a clear path faster. If the boundary is vague, AI can rapidly generate a large, plausible diff in which it becomes difficult to distinguish the necessary change from accidental work. Generation has become cheap. Understanding has not.

## What is an atomic commit in Git?

An atomic commit usually means a commit that contains one logically complete change. It can be understood, reviewed, and, when necessary, reverted independently from the surrounding changes. The key word is not **small**. It is **one**.

### One commit — one reason for change

Every commit should have one primary reason to exist: fix a bug, add behavior, rename an entity, update documentation, or prepare the architecture for the next change. These are different reasons. They should not be mixed merely because they happened during the same workday.

A commit may touch several files. It may cross several application layers. If one reason requires changing a controller, a service, a model, a test, and documentation, it can still be one atomic commit.

But if you added a feature, upgraded a library, reformatted a neighboring module, and fixed an unrelated bug you noticed along the way, there are now several reasons for change — even if all of them happen to be in the same file.

### An atomic commit does not have to be small

Fixing one typo is a small atomic commit. An automatically generated migration containing several hundred lines may be large and still atomic. Two lines can be small but non-atomic if one fixes a bug and the other renames an unrelated variable.

Line count is easy to measure, so many rules are built around it. Atomicity is not measured in lines, however. It is measured by whether the change can be separated without losing meaning. If a commit can be split into two independent parts and both remain understandable and functional, it probably should have been split.

### Five properties of an atomic commit

#### One complete idea

A commit answers one question: what changed, and why does this change exist? If the answer repeatedly needs the phrase “and also,” there is probably more than one idea inside it.

#### A working project state

After the commit, the project should build and existing checks should pass. This is not merely about having a pretty history. Working intermediate states let you move safely between versions, search for regressions, and revert individual changes.

#### Independent reviewability

Another developer should be able to review the commit without loading several later steps into working memory. Project context will still be needed, but the reason for this particular change should be local and understandable.

#### Safe revert and cherry-pick

A good atomic commit can be reverted with `git revert` or moved with `cherry-pick` without accidentally dragging along unrelated refactoring and half of another feature. This matters when a fix needs to be moved quickly to a release branch or selectively removed from production.

#### The message matches the contents

A commit message is a promise the author makes to the future reader of the history. If it says “fix phone number validation,” the diff should not unexpectedly contain a redesigned registration page and a new library version.

## Why atomic commits matter

You can build software perfectly well without atomic history. A huge number of projects do exactly that. The question is not whether development is possible without it. The question is what the team pays for the lost structure.

### Clean and understandable Git history

A good history shows not only the current state of the project but the path that led there. You do not have to open every diff to get the general picture; commit titles already show the sequence of decisions. It is like a table of contents in a book. It does not contain every detail, but it tells you where to look for the chapter you need.

### Easier and more attentive code review

Small complete changes are easier to review. The reviewer first understands the goal of the commit, then checks whether the implementation matches it. They do not have to untangle several mixed reasons for change on their own. Google's code review guidance describes a good change as one self-contained change and explicitly recommends separating noticeable refactoring from functional changes. There is no universal hard line count; [size depends on context](https://google.github.io/eng-practices/review/developer/small-cls.html).

### Safer `git revert`, `bisect`, and `cherry-pick`

Atomicity becomes especially valuable when something goes wrong. Reverting one complete step is easier than extracting a fix from a commit containing a new feature, refactoring, and configuration changes. The same applies to `git bisect`: if each intermediate commit works and contains one change, finding the point where a bug appeared is much easier. If half the commits do not build and the rest contain five separate reasons for change, the tool still technically works, but much of its value disappears.

### Faster recovery after an interruption

Development is constantly interrupted by messages, meetings, colleague questions, food, sleep, and occasionally life outside the IDE. After an interruption, you have to recover what was already done and what the next step was. In a study of [10,000 work sessions from 85 programmers](https://chrisparnin.me/pdf/parnin-icpc09.pdf), developers resumed editing within a minute only in a relatively small share of cases. Usually they first navigated the project and reconstructed the task state.

ACDD does not eliminate context switching, and creating a commit itself requires a small switch to Git. But completing one step reduces the number of unfinished thoughts that have to be restored later. The history shows where you stopped, and a pre-defined next commit shows where you were going.

### Project history as the team's collective memory

Developers leave companies, move between teams, and forget their own decisions. The code remains. Alongside it remain commit messages, issue references, and the sequence of changes. A clean history does not replace documentation or the issue tracker, but it preserves context near the code and reduces how often every investigation has to begin with archaeology through old chat messages.

## What is ACDD — Atomic Commit Driven Development?

Atomic commits are not new, and neither is the idea of formulating a commit before writing code. When I started researching the topic more deeply, I found Toby Osbourn's article on [Commit Driven Development](https://tosbourn.com/commit-driven-development/), published back in 2012. His idea was to write the future commit message first and then work until the code matched that message exactly.

Around the same time, Arialdo Martini described [pre-emptive commit comments](https://arialdomartini.wordpress.com/2012/09/03/pre-emptive-commit-comments/), connecting them with focus, micro-tasks, a small Definition of Done, and returning to context after an interruption. So I am clearly not the first developer to arrive at this idea, and that is a good thing. When different people independently discover a similar working rhythm, there may be something useful in it.

### What ACDD adds to familiar practices

I see ACDD as a stricter combination of several ideas:

- intent is formulated before the code changes;
- work is limited to one engineering reason;
- the result must be complete and verified;
- the commit remains an independent point in history;
- the next step begins only after the current one is complete.

Simply committing often is not enough. A hundred tiny `wip` commits do not become ACDD. Beautiful Conventional Commit messages do not guarantee anything either if each one contains a random collection of files.

### The commit as a unit of engineering thought

In a conventional workflow, the commit is at the end: first the developer does something, then tries to describe it. In ACDD, the commit appears at the beginning as the boundary of the next action.

The main question is:

> What commit am I going to make next?

The answer forces a pause before the first line of code. What exactly should change? Where does the action end? How will I know that it is complete? Which checks must pass?

This is a small design session. Sometimes it takes a few seconds. Sometimes it reveals that the task is not understood well enough and it is too early to write code.

### The core ACDD cycle

#### Intent

First comes the thought about the change: add a check, change an interface, prepare a table, or document method behavior. It should be expressed precisely enough that the desired result is clear.

#### Define the boundary

Decide what belongs in this step and what already belongs in the next one. This is also where completion criteria appear, along with the list of things we consciously choose not to touch yet.

#### Action

Perform only the defined change. Anything discovered along the way is recorded separately unless it is necessary to complete the current step.

#### Verification

Review the diff, run the tests, and compare the result with the original intent. If the contents have become broader than the definition, split the change or redefine the boundary honestly.

#### Commit

Record the complete change in history. Then move on to the next thought with working memory freed from the previous one.

## How ACDD differs from other approaches

ACDD does not try to replace TDD, Conventional Commits, design, or task management. These practices operate at different levels.

### Atomic commits are a property of history; ACDD is a work process

Atomicity describes the result: one commit contains one complete change. ACDD describes the path: define the next commit first, then do the work that belongs to it. You can create an atomic history after the fact with `git add --patch` and interactive rebase. The resulting history may be excellent, but the development process itself was not driven by commits.

### ACDD and Conventional Commits

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) defines the message format: type, optional scope, description, body, and footers. This helps people and automated tools understand the nature of the change, but it does not define its boundary. You can write a perfect title such as `feat(auth): add OAuth support` and still put five independent changes inside the commit. Conventional Commits answers “how should I name this change?” ACDD answers “how should I isolate, perform, and verify it?”

### ACDD and Test-Driven Development

TDD drives development through behavior expressed as a test. ACDD drives development through complete changes recorded in history. They fit together well: a test helps define the expected result, while the commit defines the boundary of the next step.

A red test can be useful as a temporary local checkpoint in a branch. But if every published commit must leave the project green, the test and the minimal implementation usually belong in the same complete commit. A standalone test commit makes sense when it captures existing behavior before refactoring and already passes on the current version of the project.

### ACDD and Spec-Driven Development

Spec-Driven Development first describes requirements, design, and a sequence of tasks. For example, this is the direction taken by [GitHub Spec Kit](https://github.com/github/spec-kit) for AI-agent workflows. A specification defines the route and target result; ACDD defines the next safe step. In that analogy, the specification is the route, and atomic commits are the individual segments of the journey.

## How to work with ACDD: the atomic commit cycle step by step

ACDD does not require a special tool. Git, an editor, and somewhere to record the next thought are enough. It can be a note, an item in a task, or a commit plan written in advance.

### Before changing code

#### Answer: “What commit am I going to make next?”

Do not ask only “what task am I solving?” Ask what complete result should exist at the next point in history. A large task may be “add password recovery,” while the next commit is much more specific: “add password recovery token model,” “implement token creation,” “add recovery email delivery,” or “handle password replacement.”

#### State the intent in one sentence

For example: “Document the behavior of method X.” That sentence already defines a scope. If you also decide to rename the method, you have introduced another reason for change and probably another commit.

#### Define the completion criteria

What must exist after the change? Which tests must pass? Should documentation change? Is the new API usable at this point, or is this only a preparatory step? The clearer the end of the step, the easier it is to stop on time instead of dragging several extra changes into it.

### While working

#### Keep one stream of attention

If you are writing a test, write the test. If you are changing documentation, change documentation. This does not mean that one commit may touch only one file type. The rule is about one reason, not one file extension.

#### Do not include fixes discovered along the way

You will inevitably notice a badly named variable, an old dependency, or a method you have wanted to rewrite for months. The fix may take twenty seconds, but it changes the story of the current commit. Record the thought and make it the next commit if it is actually important. Git will still be there.

#### Revisit the boundary if the change grows

The preliminary definition is not a blood oath. Sometimes work reveals that a step cannot be completed independently or that the original decomposition was wrong. In that case, change the boundary. The goal is not loyalty to the first plan but honest correspondence between intent and result.

### Before creating the commit

#### Review the resulting diff

Look at the change as if you were the reviewer. Does every line belong to the stated intent? Did debug code remain? Did an automatically modified file sneak into the diff?

#### Run tests and project checks

Every independent commit should, where practical, leave the project working. In my repositories, the rule is explicit: each commit should build and pass checks independently.

#### Compare the contents with the original intent

If the message no longer describes the diff, there are two choices: change the definition or split the change. There is little point in inventing a beautiful message for a chaotic collection of edits.

#### Record the change and move on

After the commit, the thought is complete. History stores the result, and your head can move to the next step. If you cannot explain what exactly was completed, the commit may have been created too early.

## How to define the boundary of an atomic commit

A good commit ends where one reason for change ends. The sentence sounds simple. In practice, this is where most arguments begin.

### Questions that help find the boundary

#### Can the change be described by one reason?

If the description sounds like “added the method and also updated documentation for another module,” there are two reasons. Words such as “and also,” “while I was there,” or “along the way” often expose the split point. The conjunction itself proves nothing, of course, but it is a useful reason to inspect the diff again.

#### Can it be reviewed independently?

The reviewer should understand what they are reviewing in this commit. If correctness of the first part cannot be evaluated without the third future commit, the boundary may be wrong. Dependencies between steps are fine, but the current step should not be a meaningless fragment of a future solution.

#### Can it be reverted without reverting other changes?

Imagine the new feature causes a production incident. Can it be removed with one `revert` without restoring an old class name and deleting a useful refactoring? If rollback requires manually selecting lines from several different decisions, the commit boundary is almost certainly too wide.

#### Will the project still work after the split?

Do not split work merely to increase the number of commits. If the first half does not build, cannot be tested, and has no independent meaning, it is not an atom — it is just a half. Good decomposition creates a sequence of working states, not a collection of beautifully numbered fragments.

#### Does the reviewer need the next commit to understand the current one?

Some changes naturally depend on each other, and that is fine. But each step should still explain its own role in the sequence. The reviewer may know what comes next, but the current commit should already answer why it exists.

### How to separate different kinds of changes

#### New functionality

A large feature can be split by complete vertical capabilities or by safe preparatory steps. For example, add an independent interface first, then an implementation, then connect it to the existing flow. The preparatory step should be justified on its own and should not leave the system in a half-changed behavioral state.

#### Bug fix

A commit should contain the cause of the bug, the fix, and evidence that the result is correct — usually a regression test. Incidental refactoring is better placed before or after the fix so the behavioral change remains visible in the diff.

#### Refactoring

Refactoring changes structure while preserving behavior, so it is useful to separate it from new functionality. You can first prepare the code for a change and then alter behavior separately. The diff then makes it obvious where code moved and where new logic appeared.

#### Tests and documentation

Tests required to prove new behavior may be part of the same atomic change. Documentation for a public interface can also be part of feature completeness. But fixing an old article or adding an independent test set is better recorded separately.

#### Dependency and configuration updates

A library upgrade creates its own risks and should be visible in history. Do not hide a new dependency version inside a functional commit unless it is inseparable from the feature. A separate commit makes it easier to inspect the changelog, roll back the version, and identify the source of a regression.

### When a large commit can still be atomic

#### Database migrations and API changes

One schema transition can affect the migration, models, queries, and backward compatibility with the previous application version. The diff may be large while the reason remains one. File count matters less than whether the transition can be applied and reverted safely as one complete step.

#### Automatically generated code

Generated files can add thousands of lines, so their size says little about the complexity of the decision. Still, generated output should not be mixed with hand-written refactoring; otherwise the reviewer has to find a few meaningful lines inside mechanical noise.

#### Large-scale renaming or formatting

A mechanical edit may touch the whole project. Keeping it separate prevents it from creating noise around behavioral changes. History remains readable, and the next functional diff is not buried in whitespace and renamed identifiers.

#### Changes across multiple repositories

A single Git commit cannot span multiple repositories. Here atomicity becomes organizational: publication order, backward compatibility, and cross-links between changes matter. Sometimes the real atom exists at the release level rather than inside one repository.

## How to write commit messages

A good message cannot make a bad commit atomic, but a bad message can hide the meaning of a good change. Contents and wording should therefore be reviewed together: each should honestly describe the other.

### A good message describes the intent of the change

The diff usually tells you which lines were added and removed. The message should help explain why this new version of the project exists. The title briefly states the result. The body explains reasons, constraints, and non-obvious decisions. A one-character typo does not need a philosophical essay.

### Why an issue number is not enough

A message such as `PROJ-1234` links code neatly to an issue tracker, but tells nothing to a person who does not currently have access to that issue. Years later, the tracker may move or the link may disappear while the repository remains. The issue number is useful as an additional reference, not as a replacement for meaning.

### Conventional Commits as a message format

The basic structure looks like this:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The `feat` type represents new functionality, `fix` a bug fix, and `BREAKING CHANGE` or `!` marks a backward-incompatible change. These elements are connected to Semantic Versioning. Teams may define other types by convention.

Common examples include:

- `docs` — documentation;
- `refactor` — structural change without new behavior;
- `test` — adding or fixing tests;
- `perf` — performance;
- `style` — formatting;
- `build` — build system and dependencies;
- `ci` — CI configuration;
- `chore` — technical changes that do not fit another category.

If one commit simultaneously looks like `feat`, `fix`, and `refactor`, the problem may not be choosing the type. There may actually be three changes inside it.

### How a thought becomes a commit message

Suppose the initial thought is: “Add documentation for method X.” It becomes a preliminary statement: “Documented method X behavior.” Then the work is limited to explaining the method's purpose, constraints, and result. During verification, we confirm that the diff contains only the relevant documentation and create a commit such as `docs: document method X behavior in class A`. That is all: a small thought became a complete commit, and we can move on.

### Commitlint as a guardrail, not a replacement for thinking

[Commitlint](https://github.com/conventional-changelog/commitlint) can validate message format, allowed types, and title length. It cannot determine whether an incidental style edit belongs in an authorization fix. A linter can enforce an agreement that people already made; it cannot invent the agreement for them.

## Anti-patterns: commits that destroy Git history

The names below are not part of an official specification. I use them because labels make familiar situations easier to recognize.

### The monolith commit

One large task, several days of work, one commit. Everything belongs to the same high-level task but not to one reason for change. It is difficult to read, review, revert, and discuss.

### The polyglot commit

A developer builds a feature, notices a poor name, upgrades a library, fixes styles, and writes documentation for a neighboring module. Every edit may be useful, but together they speak different languages. This is the classic “fixed it while I was there” commit after which nobody can explain the common reason for the diff.

### The bait-and-switch commit

The message promises one change while the diff contains another. Sometimes the developer simply forgot to update the original wording. Sometimes the message was written only after the work and not everything was remembered.

### The universe commit

“Rewrote the module.” Under that message may live a new architecture, changed behavior, removed functions, and an updated public API. There is an entire world inside, but no map.

### The “what did you do?” commit

`fix`, `wip`, `update`, `temp`. Such a message does not save time. It transfers the work of reconstructing meaning to every future reader.

### The lost-thought commit

The change may have been atomic, but the reason for it was never preserved. The code shows what happened. Why it was necessary is already forgotten.

## Atomic commits in pull requests and code review

Commit, task, and pull request are often treated as the same unit. That leads to rules like “one task — one commit,” which sound good but scale poorly to large tasks.

### One task may contain many atomic commits

A task describes the goal. Commits describe complete steps toward that goal. If password recovery requires eight independent decisions, eight understandable commits are better than one large one. One step — one commit. One task — a coherent sequence of steps.

### One pull request should tell one complete story

Think of a commit as a paragraph, a pull request as a chapter, and a release as a larger section of the project's history. Paragraphs should stand on their own while still leading toward one result. If half of a pull request can be released independently and provides complete value, you may actually have two pull requests.

### Why smaller changes are easier to review

A small PR is easier to open between other tasks, easier to hold in working memory, and easier to return to the author with specific feedback. If ten percent of a five-thousand-line change is controversial, that ten percent blocks the other ninety. Splitting work also protects the author: if the direction turns out to be wrong, less work is lost.

### How many lines should a good pull request contain?

There is no universal number. Google mentions 100 lines as often reasonable and 1,000 as usually too large, while immediately noting that context and file count matter. I like an informal target of up to about 350 lines of meaningful hand-written changes. This is not an ACDD rule and it is not a reason to reject a PR with 351 lines. Generated code, deleted files, and mechanical formatting are different. The number is useful as a signal to stop and ask whether the change can be smaller.

### Should tests and implementation live in the same commit?

If a new test fails without an implementation that has not yet been added, publishing the red test separately violates the working-state rule. In that case, the test and minimal implementation form one complete step. If the test captures already-existing behavior before refactoring and passes on the current code, it can be an independent commit. The important property is completeness of state, not file type.

### How to read a pull request commit by commit

A good sequence lets the reviewer follow the same logical path as the author: preparatory refactoring first, new behavior next, integration into the system after that. Each step can be evaluated independently while the overall diff shows the final result. If the commits cannot be read in order without constantly jumping backward and forward, the branch history is worth revisiting before review.

## Working history and published Git history

A fair question appears here: what do we do with `wip`? Sometimes the day ends in the middle of a change. Sometimes we need to switch urgently. Sometimes we want a safe checkpoint for an experiment that is not yet complete.

### Are WIP commits acceptable?

A local WIP commit can be useful insurance. Saving incomplete work is better than losing it or keeping it in one working tree for a week. But such a commit is a checkpoint, not a complete ACDD step. Before publishing the branch, it can be combined with the target commit, renamed, or reorganized.

### Work history and decision history are not the same thing

Real development is nonlinear. We try things, make mistakes, go back, and change our minds. There is no need to preserve a literal transcript of every movement. Published history should show the logic of the result, not every uncertainty along the way — just as an article draft differs from the version you are reading now.

### When to use fixup and interactive rebase

If review requires adjusting one particular atomic commit, it is convenient to create a `fixup` and attach it to the correct place with interactive rebase before merging. The correction then sits next to its cause rather than becoming a dangling `fix review comments` commit. Rewriting your own branch is safe when nobody else is building on it. Rewriting a shared published branch without agreement is not.

### Should commits be squashed?

Squash is useful when a branch consists of experimental and temporary checkpoints: it turns noisy working history into one understandable change. But if the branch already contains a sequence of independent atomic decisions, a full squash destroys that level of detail and leaves only the final diff. There is no universal answer. First decide what history the team finds useful: one commit per PR or a sequence of complete engineering steps.

## ACDD with AI and coding agents

AI can write code faster than a human can read it carefully. That does not mean AI always speeds development up. In a [METR study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), experienced developers working on familiar open-source projects with the studied tools took more time on average even though they expected to become faster. The reason is understandable: generated code still has to be read, corrected, and verified. Sometimes it is quicker to write the exact solution yourself than to explain every constraint of an old system to an agent.

The [DORA 2024 report](https://dora.dev/research/2024/dora-report/) associated AI adoption with gains in individual productivity and satisfaction, but also with challenges around delivery stability and throughput. Small batches of change and reliable testing remain foundational practices. ACDD is useful here not as a way to make AI generate more code, but as a way to stop generation at the right time.

### Why large AI-generated changes are dangerous to accept wholesale

AI is good at producing plausible code. A large diff can look coherent, survive superficial review, and contain one small wrong architectural assumption repeated across several places. The larger the change, the harder it becomes for a human to prove to themselves that they genuinely understood it. The Accept All button saves seconds and can create days of work.

### One work cycle — one verifiable commit

When working with an agent, the cycle can look like this:

1. State one intent.
2. Specify what may change and what must not change.
3. Define completion and verification criteria.
4. Ask the agent to perform only that step.
5. Review the diff and test results.
6. Accept the commit or reject the change as a whole.

The number of messages sent to the agent does not matter. One commit may require several rounds of clarification. What matters is that the work cycle ends with one verified idea.

### Why AI should not define its own responsibility boundaries

An agent can propose decomposition, but the developer should confirm the boundaries. The human knows the business context, acceptable risk, release plan, and consequences for other teams. If AI defines the task, changes the code, and validates its own result, human control becomes ceremonial.

### How ACDD helps preserve understanding of AI-generated code

After each step, the developer has to answer simple questions: what changed, why, what evidence supports it, and am I willing to leave my name next to this commit? That pause does not meaningfully slow work. It simply prevents generation speed from outrunning understanding speed. Code production can be delegated to a tool. Responsibility for the result cannot.

## Benefits and limitations of ACDD

ACDD is not a universal recipe. It is a way of organizing work that requires time and discipline. In some situations it helps; in others it can turn into ritual.

### What ACDD gives an individual developer

- less unfinished context in working memory;
- a clear point from which to resume work;
- visible progress inside a large task;
- the ability to roll back individual decisions safely;
- a habit of formulating intent before action.

A small complete commit creates a sense of movement. A large task stops looking like one wall and becomes a sequence of steps.

### What ACDD gives a team

- clearer code review;
- a history of engineering decisions next to the code;
- easier rollback and regression search;
- the ability to discuss individual steps rather than the entire diff at once;
- more predictable boundaries for changes produced by AI agents.

### When atomicity becomes over-fragmentation

A commit for every variable rename does not automatically improve history. If a step cannot be understood outside the next commit, it may be too small. Atomicity means minimum completeness, not minimum line count. Split work down to independent meaning, not down to individual keystrokes.

### Is ACDD appropriate during research and prototyping?

During a spike or while learning an unfamiliar library, the result may not be known in advance. Temporary checkpoints are fine, and there is no need to build perfect history immediately. Once the direction becomes clear, the useful part of the experiment can be reconstructed as a sequence of complete changes. A draft is allowed to be messy. That does not mean the final published history has to be.

### When the cost of order exceeds its value

If a developer spends more time rearranging three obvious commits than the team will ever spend reading them, the process has stopped serving its purpose. Order exists to accelerate understanding and reduce risk, not to win a beauty contest for `git log`.

## How to start using ACDD

There is no need to introduce a formal policy or install a company-wide linter. Take one ordinary task and, before starting, write down the sequence of commits you expect to make. The plan does not have to be correct, and it may change while you work. The point is not to predict the future. The point is to understand the next step every time.

Try it for a few weeks and observe:

- whether returning to a task after an interruption is easier;
- whether diffs become easier to understand;
- whether incidental changes become less common;
- whether code review becomes easier;
- whether individual decisions can be reverted safely;
- whether history still explains the work a month later.

If a team adopts the approach, a few rules are enough to begin:

1. One commit contains one reason for change.
2. After every published commit, the project remains in a working state.
3. The commit message matches its contents.
4. Unrelated changes are separated.
5. Pull request boundaries are discussed before the diff grows to several thousand lines.

Everything else can be added as needed: Conventional Commits, commitlint, CI, message templates, or a rough PR-size guideline. Agreement first. Automation second.

## ACDD is not only about commits

ACDD begins with Git, but it quickly extends beyond Git. The commit becomes a unit of meaning, and history becomes a narrative of how the project evolved. One step corresponds to one action, and the thought is better recorded before it escapes. At that point, a commit stops being an archive of changes and becomes a tool for thinking.

A commit message is an act of honesty toward yourself, your colleagues, and future developers. Atomicity is a form of respect for the reader of the code. Small complete changes provide structure, project history preserves part of the team's collective intelligence, and discipline first feels like a constraint before it starts creating freedom.

I am not asking anyone to treat ACDD as the one correct methodology. Try taking one task from commit to commit and compare how it feels. Maybe the rhythm will not suit you. Or maybe, afterward, a large undivided diff will start to feel as strange as a thousand-line method.

Creating a commit is easy. The question is still the same: what exactly did you put into it?

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
