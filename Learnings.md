# Learnings — Building Software with LLMs

Hard-won lessons from using large language models as coding partners.

---

## 1. Build Feedback Loops (The Single Most Important Thing)

The default LLM workflow is **open-loop**: the human describes what they want, the LLM generates code, and the human manually tests it, finds problems, and feeds corrections back. This is slow, expensive, and exhausting.

The goal is to make the loop **closed** — give the LLM a way to critique its own output, discover its own errors, and iterate autonomously. The human's job shifts from *verifying code* to *verifying the loop itself*.

### Ground Truth Systems

Find something authoritative that the LLM can compare against. There are several forms this can take:

- **Reference implementations.** If you're reimplementing something that already exists, use the original as an oracle. In this project, the JavaScript Vim simulator is tested by running the same keystrokes through real Neovim, capturing the resulting buffer/cursor/screen, and comparing. The LLM can run the test harness, see exactly which cases fail and how, and fix them without the human having to know the answer. This is the ideal: the LLM never has to ask "is this right?" — it can check for itself.

- **Execution logs with self-review.** Demo video scripts were initially written as dead reckoning — a sequence of keystrokes with no verification. Cursor positions drifted, edits landed in the wrong place, and the human had to watch every frame. The fix was verbose execution logs with screenshots after each step. Now the LLM runs the demo, reads the log, spots its own mistakes (wrong cursor position, missing text, etc.), fixes the script, and re-runs. After a few iterations the video is mechanically correct and the human only has to judge the *content* — is this a good demo? — not whether the cursor is on the right character.

- **Tests as ground truth.** A well-written test suite is itself a closed-loop sensor. The LLM runs the tests, sees failures with specific inputs and expected-vs-actual outputs, fixes the code, and re-runs. The human's job is authoring and curating the tests, not verifying the code. This is the most universally applicable form of ground truth — every project can have tests, even if it doesn't have a reference implementation.

  The key insight: you don't have to hand-write every test. Like any ML problem, you can **synthesize tests from known-good examples**. Write a handful of representative cases that cover the general patterns, then have the LLM generate hundreds of variations that explore the space — edge cases, combinations, boundary conditions. A human reviews a sample for correctness, and now you have broad coverage that the LLM can run against autonomously. In this project, a few dozen hand-written Vim operation tests were expanded into hundreds of generated cases covering motions, operators, counts, and combinations.

### The Pattern

1. **Establish a source of truth** — a reference implementation, a test suite, execution logs, recorded golden files, whatever fits the domain.
2. **Give the LLM a way to run the comparison** — a script, a test harness, a log viewer.
3. **Let it iterate** — run → compare → fix → repeat.
4. **Human reviews the high-level output** — not the individual lines of code.

---

## 2. Invest Heavily in Upfront Specs

Time spent specifying behavior in English before any code is written pays for itself many times over. The LLM is remarkably good at turning a clear spec into working code, and remarkably bad at guessing what you meant from a vague prompt.

### The Workflow

1. **Spec phase.** Write (or co-write with the LLM) a detailed description of what the system should do. Cover edge cases. Use concrete examples. It's fine if this takes days — it's the cheapest phase to iterate on.
2. **Test phase.** Derive tests from the spec. These tests become part of the feedback loop. The LLM can run them, see failures, and fix code without human intervention.
3. **Build phase.** The LLM writes the implementation. Most failures are caught by the tests automatically.
4. **Review phase.** The human tries the result, finds systemic issues or gaps in the spec, and feeds corrections back — *to the spec and tests first*, then lets the LLM re-derive the code.

This is essentially **test-driven development**, but with a twist: the human's primary job is maintaining the spec and the tests, not the code. The code is the LLM's problem.

### What Goes in a Spec

- Expected behavior described in plain English
- Concrete input/output examples
- Edge cases called out explicitly
- Non-goals (what the system should *not* do)
- Terminology definitions (so the LLM doesn't invent its own names)

---

## 3. Maintain an Instructions File

Create an `Instructions.md` (or similar) for each major subsystem. This is the LLM's "style guide" — it tells the LLM how to do things in this particular project.

Every time you find yourself correcting the LLM's behavior — it uses the wrong naming convention, structures code in a way you don't like, makes an assumption that's wrong for this project — don't just fix it in the moment. **Add it to the instructions file.** Over time, this file accumulates enough context that the LLM does the right thing without constant shepherding.

Examples of what belongs here:

- Project conventions (naming, file organization, preferred patterns)
- Common gotchas specific to the codebase
- "Don't do X, do Y instead" rules
- How to run tests, what the expected workflow is
- Architectural constraints the LLM should respect

The instructions file is a living document. Treat it like you'd treat an onboarding guide for a new team member who is very smart but knows nothing about your project.

---

## 4. Document Architectural Decisions

This matters for any project but is *critical* when working with LLMs. Without a written record, the LLM will vacillate — making one choice in one session and a contradictory choice in the next.

Keep a record of:

- **What was decided** — e.g., "Undo saves one snapshot per macro, not per keystroke within the macro."
- **Why** — e.g., "Matches Neovim behavior; users expect a single `u` to undo an entire macro replay."
- **What was rejected** — e.g., "We considered per-keystroke snapshots but it broke the undo UX."

This doesn't need to be elaborate. A simple log or a section in the instructions file is enough. The point is that when the LLM encounters the same decision point again, it has a written answer instead of re-deriving (and possibly contradicting) the original choice.

---

## 5. Keep Context Compact and Navigable

LLMs have finite context windows. Even with very large windows, more noise means worse signal. Structure your project so the LLM can find what it needs quickly:

- **Small, focused files** over monolithic ones.
- **Clear file and directory naming** — the LLM reads your file tree.
- **Comments at the top of files** explaining purpose, not just implementation.
- **A project-level README or map** that orients the LLM to the codebase structure.

When context is well-organized, the LLM spends fewer tokens searching and more tokens thinking.

---

## 6. Let the LLM See Its Own Mistakes

When something goes wrong, don't just tell the LLM the answer. Show it the *evidence*:

- Paste the failing test output.
- Show the log with the wrong behavior.
- Include a screenshot diff.
- Let it run the command and see the error.

LLMs are much better at fixing problems when they can see the symptoms than when they're told the diagnosis. "The cursor is at column 5 but should be at column 3 after `w` on this line" is more useful than "your word motion is broken."

---

## 7. Batch Work, Then Verify

Rather than going keystroke-by-keystroke with the LLM, give it a batch of related work and let it execute. Then verify the batch. This plays to the LLM's strength (generating coherent, internally-consistent work) and minimizes the human bottleneck.

For example: "Implement all the line-motion operations (`j`, `k`, `+`, `-`, `G`, `gg`), then run the test suite and fix any failures." This is far more efficient than doing them one at a time with human verification between each.

---

## 8. Distinguish Levels of Review

Not everything needs the same level of human scrutiny:

| Level | What the human checks | Example |
|-------|----------------------|---------|
| **Mechanical correctness** | Nothing — the tests/ground truth handle this | Does `dw` delete the right characters? |
| **Behavioral correctness** | Spot-check that the spec is right | Should `dw` at end of line join the next line? |
| **Design quality** | Full human review | Is this the right API? Is the code maintainable? |
| **Content quality** | Full human review | Is this tutorial actually good? Does it teach well? |

The feedback loop handles level 1 automatically. The human focuses on levels 2–4.

---

## 9. Don't Be Overly Prescriptive

It's tempting to dictate exactly *how* the LLM should implement something — which data structure to use, how to decompose the functions, what the control flow should look like. Resist this. LLMs are surprisingly good at design decisions, and painting them into a corner often leads to worse results than letting them find their own path.

Think of it like working with a strong developer. The more you trust them, the more you leave up to them. You describe *what* you want and *why*, and let them figure out *how*. If you wouldn't micromanage a senior engineer's implementation approach, don't micromanage the LLM's either.

In practice this means:

- **Describe the desired behavior**, not the implementation steps. "Implement undo so that a macro replay is a single undo unit" is better than "push a snapshot before the loop, set a flag to suppress snapshots inside the loop, then..."
- **Ask for its opinion.** "What's a good way to structure this?" or "I'm torn between X and Y — what do you think?" LLMs will often suggest approaches you hadn't considered.
- **Specify constraints, not solutions.** "This needs to work with the existing test harness" is a useful constraint. "Use a for loop that iterates over..." is usually unnecessary.
- **Intervene on *what*, not *how*.** If the result is wrong, say what's wrong with the output. Don't rewrite the algorithm in English for it to transcribe.

The exception: when the LLM keeps making the same design mistake, that's a signal to add a rule to the instructions file (see §3). But even then, frame it as a constraint ("don't use X because Y") rather than a step-by-step recipe.

---

## Summary

| Principle | One-liner |
|-----------|-----------|
| Feedback loops | Give the LLM a way to check its own work |
| Ground truth | Find an oracle the LLM can compare against |
| Upfront specs | Spend time on English before code |
| Test-driven | Tests are the spec made executable |
| Instructions file | Teach the LLM your project's conventions once |
| Decision log | Write down choices so the LLM doesn't flip-flop |
| Compact context | Organize so the LLM finds things fast |
| Show, don't tell | Let the LLM see errors, not just hear about them |
| Batch and verify | Big chunks of work, then review |
| Tiered review | Don't manually verify what machines can verify |
| Don't micromanage | Describe *what* and *why*, let the LLM figure out *how* |
