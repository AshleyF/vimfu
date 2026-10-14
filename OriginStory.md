# Closing the Loop: What Building VimFu Taught Me About Autonomous AI

> This is the archival account of how VimFu developed, followed by a shorter version suitable for a post or video.

We should stop treating AI as a machine that ought to produce a correct answer in one shot. Give the AI tools with which to act in the real environment, an objective way to verify its work, and time to revise. The human chooses the objective and judges the final result; the AI closes the loop in between. VimFu is the small, personal project through which I learned this.

I have used Vim professionally for more than twenty years. I keep returning to the same idea: Vim is not merely a collection of shortcuts. It is a small editing language.

I am not presenting VimFu as a frontier AI achievement. It is a personal project about a tool I know well, and that familiarity gave me a good view of what the agents were getting right and wrong. Its value here is as a small case study whose entire feedback loop I could observe. The consequential examples are much larger, but this is the one I saw from the inside.

Years ago, that idea led me to build [VimSpeak](https://github.com/AshleyF/VimSpeak), an F# experiment that mapped spoken grammar onto Vim's grammar. You could say “select three words” and have it produce the corresponding keystrokes, or dictate a complicated substitution and have it translated into a Vim command. It was a weekend project, but it made me think seriously about Vim's structure and how people should learn it.

Eventually, I designed a curriculum and began recording YouTube Shorts that taught one idea at a time. This was before I used AI for the project. I made roughly fifty videos by hand, which probably took a hundred hours. Choosing examples, scripting, performing the edits, narrating, correcting mistakes, and publishing every video was too much work. The project stalled.

## Automating the videos

I had already built a Windows-only recorder that replaced live performance with deterministic scripts. A script could launch real Neovim, send keystrokes, capture the terminal, and assemble a video with narration from Neural Voice, a neural network trained on recordings of my voice. I thought that part was especially cool. Correcting a lesson meant changing the script and running it again.

When I returned to VimFu, I rebuilt that system for macOS with AI doing much of the implementation. Its foundation became ShellPilot: a programmable terminal that exposes every screen cell, character, color, highlight, and cursor position. It can send arbitrary keystrokes and control anything that runs in a terminal. Around it, I added narration, frame capture, `ffmpeg` assembly, and fully automated YouTube publishing.

AI first helped me expand the curriculum, find gaps, add `tmux`, and improve the progression. Then I asked it to write the lessons. Given a topic, it could usually invent a compact example, write the narration, choose the keystrokes, and produce a plausible demonstration. Eventually, the pipeline could take a topic and publish the finished video.

Plausible, however, was not the same as correct.

The cursor might begin on the wrong line. The narration might describe a change that had not happened yet. A motion might affect different text from the text named in the script. The lesson's idea was often good, but its execution was wrong in some small way.

For a while, I watched every result and explained each defect to the AI. That made me the test harness. The process could not continue when I walked away.

My aha moment was realizing that ShellPilot could turn the visual artifact back into text. I changed it to record a textual snapshot after every keystroke: visible characters, colors, highlights, and cursor position. Together, those snapshots formed a large but precise textual representation of everything that had appeared on screen.

The AI could now consume a representation of its own artifact and compare it with the script it had generated. If the cursor was misplaced, the wrong text changed, the timing drifted, or the video exceeded one minute, it could revise the lesson and try again.

The AI did not stop making mistakes. It stopped requiring me to find them.

Reliability improved enough that I could request fifty videos and inspect the batch later. Eventually, I stopped reviewing them before publication. For a full year, the system published two videos each day, producing roughly 750 in total. I saw each video for the first time only after it went public, alongside everyone else. That still seems incredible to me. Only occasionally did I have to delete, correct, and republish one.

## Lesson one: close the loop

The first lesson was not simply that AI can generate useful work. It was that generation is only one step in an autonomous system:

1. Propose an artifact.
2. Execute it in the real environment.
3. Observe what actually happened.
4. Compare the observed result with the intended result.
5. Revise and repeat.

The AI must perform that whole loop. If a person has to inspect every interface, describe every defect, and request every correction, the person remains the bottleneck.

For a website, closing the loop might mean giving the AI Playwright so it can operate the page, inspect the DOM, capture the result, and test the behavior. For a desktop application, it might require UI automation and screen inspection. For VimFu, it was ShellPilot and the terminal log.

This changed how I thought about model choice. I did not run a controlled model comparison, but in practice a faster, less expensive model often did fine once it could inspect and correct its work. It might require five attempts instead of one, but I was not inside those attempts.

Autonomy changes what efficiency means. I can vacuum a floor faster than a Roomba, but the Roomba lets me do something else while it wanders around and eventually finishes the job. Likewise, the useful measure of an autonomous system is not whether it succeeds in one shot. It is whether it reaches a verified result without continuous supervision.

There is an important limit: the loop improves only what it can measure. The video harness could verify duration, cursor position, visible text, selection, and synchronization. It could not prove that the original lesson idea was insightful. A human might still want to approve the example or decide which part of a topic matters.

The human role moves upward. People choose goals, judge novel ideas, approve architecture, and define success. The system should handle the repeated implementation and correction beneath that level.

## Lesson two: find an objective verifier

A model criticizing another model is useful, but criticism is not verification. Two agents can share the same false assumption and confidently reinforce it. The loop needs an external check:

- A known-good reference implementation.
- An executable test suite with meaningful coverage.
- A compiler, type checker, proof checker, simulator, or physical measurement.
- A rigorous specification with observable requirements.

Even without a perfect oracle, the finished system should be compared with the original approved objective. Passing thousands of local tests is not enough if the assembled product quietly implements the wrong architecture.

## A compiler with a golden oracle

Anthropic's experiment [*Building a C compiler with a team of parallel Claudes*](https://www.anthropic.com/engineering/building-c-compiler) suggested a stronger version of this pattern. Sixteen agents created a C compiler in Rust capable of compiling the Linux kernel. The project took nearly 2,000 Claude Code sessions over two weeks and produced roughly 100,000 lines of code.

It was not one shot in the sense of one response. It was one high-level assignment followed by thousands of autonomous attempts.

The compiler problem came with unusually good verification. Compiler test suites exercised language behavior. Open-source projects supplied integration tests. Compiling Linux tested the system at enormous scale. When kernel failures became difficult to isolate, the harness used GCC as a known-good compiler and varied which files were compiled by each implementation.

GCC was a *golden oracle:* an independent source of ground truth that could automatically supply the expected behavior.

Anthropic's account says that most of the human effort went into the tests, environment, and feedback. That is the real achievement. The agents were placed in a world where they could keep asking, “Does this behave like the known-good implementation?” without waiting for a person to answer.

## Building Vim again, in a browser

I wanted VimFu's lessons to be interactive without requiring anyone to install Vim. A reader should be able to open a browser and try an example immediately. That meant building the [VimFu Simulator](https://vimfubook.com/sim/): a Vim-like editor, shell, and `tmux` environment implemented for the web.

This was much larger than the video pipeline. Vim's motions interact with operators, counts, registers, modes, undo history, visual selections, command-line editing, windows, syntax colors, shell filters, and plugins. The curriculum also demonstrates interactions among Vim, `tmux`, and ordinary terminal programs.

But I already had golden oracles: real Neovim, real `tmux`, and ShellPilot's ability to control them and capture their state.

The documentation became an implementation specification. Hundreds of lesson scripts became behavioral scenarios. The agents generated more cases for boundaries and combinations. The harness ran identical keystrokes against the real program and the simulator, then compared the text, cursor, selection, colors, and terminal state. It ignored environmental details expected to vary between runs, such as the hostname and machine clock, while preserving differences that represented actual defects.

The current differential suite contains thousands of Neovim-grounded cases across dozens of feature suites, plus tests for syntax highlighting, the virtual shell, sessions, and `tmux`. The important fact is not the count. The expected answers come from the real programs rather than from the simulator's own assumptions.

Once the harness existed, agents worked for weeks. The loop eventually produced a browser implementation broad enough to run the VimFu curriculum.

I was astonished. I manually tried examples from the videos, and they worked.

Then I returned to the loop at a higher level. Now that the agents had read the documentation and implemented Vim's behavior, I asked them to audit the curriculum again. We found missing material, added lessons, generated more videos and tests, and repeated the process.

I was no longer correcting cursor positions. I was judging completeness and deciding what the project should contain.

## Where else it applies

Some problems are especially well suited to this method because finding an answer is difficult while checking one is comparatively easy. Formal proof is an example. OpenAI's [proposed solution to the Navier–Stokes Millennium Prize Problem](https://openai.com/index/navier-stokes-solution/) was published with a Lean formalization. Lean does not choose the theorem or guarantee that humans formalized the intended claim, but it can mechanically determine whether a proof follows from that formal statement.

The VimFu Simulator is effectively a software port: it reproduces Vim's behavior in a different implementation and environment. Other software ports have the same useful shape. The existing application can act as the behavioral oracle for the new one. The comparator must understand which differences are legitimate -- an Android application should use Android conventions rather than imitate an iPhone pixel for pixel -- but that equivalence can be designed into the harness.

Brandon Thomas's [ArtCraft applications](https://getartcraft.com/apps) are an eye-opening adjacent example. They are deliberate, direct open-source clones of Photoshop, Illustrator, Premiere, After Effects, Lightroom, InDesign, Word, PowerPoint, Excel, and other major applications, built to reproduce the originals' interfaces and behavior. Many are still labeled early alpha or in development, and long-tail compatibility remains difficult. They should not be described as finished replacements yet. Even with those qualifications, the breadth of software one person can now attempt is remarkable.

These examples are far more impressive than my Vim project. VimFu did not give me comparable scale or novelty. It gave me direct experience with one mechanism that helps make such work possible: give the agents a real environment, objective feedback, and enough time to correct themselves.

The better the verifier, the farther a person can move out of the execution loop.

## Conclusion

VimFu suggested two lessons to me:

1. Do not optimize for one-shot generation. Build a feedback loop in which the AI can execute, observe, verify, and correct its own work.
2. Find a golden oracle whenever possible. A reference implementation or other objective verifier can turn an enormous project into independently checkable steps.

These are observations from one project, not universal laws or controlled experimental results. When no oracle exists, people still provide purpose, taste, architecture, and final judgment. The goal is not to remove human judgment. It is to stop spending it on work that an objective feedback loop can verify more reliably.

## Short version

Here are some things I've learned over the last year or so. Nothing profound, but they've been helpful for me to keep in mind.

The first is probably familiar by now: let the AI see and touch its own artifact. If it's building a website, give it Playwright so it can open the page, click things, inspect the DOM, and see what actually rendered. If it's building a desktop app, give it UI automation. If it's working on CLI tools, give it access to the terminal. Don't make a human look at every artifact and describe what went wrong.

My little VimFu project is where the power of this really clicked for me. I've used Vim for decades. Before AI, I started making a Vim curriculum. I'm working on a book, a website, and a series of YouTube Shorts. The first fifty videos took about a hundred hours, and I got tired of it.

I revived the project with ShellPilot, an AI-accessible VT100 terminal emulator that Claude and I made. Atop this, we built a whole video-production pipeline. The AI could author a Vim lesson script, control real Neovim and `tmux`, read the screen, make and narrate the demo video, assemble it with `ffmpeg`, and publish it through YouTube's API. Completely automatically. It also made mistakes constantly. Wrong cursor position. Wrong text. Narration out of sync.

My aha moment was to turn the visual artifact back into text. I changed ShellPilot to save a log of textual snapshots after every keystroke: the characters, colors, highlights, and cursor position. The log represented what appeared in the video in a form the LLM could easily consume. It could compare its own artifact with the script it had generated, find the mistake, and try again.

For a full year, that loop published two videos every day. Roughly 750 videos. [Here is one example.](https://youtube.com/shorts/u-tpto3mR0c) I didn't review them first. I saw each one for the first time after it went public, along with everybody else. That still seems kind of incredible to me.

### Golden oracle

The more important idea is what I call a *golden oracle:* an independent source of ground truth that can objectively tell the AI whether its artifact is correct. The AI doesn't merely critique its own work. It compares the work with an answer that comes from outside the model.

Anthropic's [C compiler in Rust](https://www.anthropic.com/engineering/building-c-compiler) is a great example. The agents had a giant test suite and GCC as a known-good compiler. GCC was the golden oracle. They could keep asking, “Does my compiler behave like this compiler?” and iterating until their compiler could build Linux.

I used the same idea to build the [VimFu Simulator](https://vimfubook.com/sim/), a Vim-like editor, shell, and `tmux` environment that runs in a browser. Real Neovim and real `tmux` were the golden oracles. The harness sent the same keystrokes to both implementations and compared the resulting text, cursor, selection, colors, and screen state across thousands of cases. The agents worked on the mismatches for weeks. Eventually, the simulator could run the examples from the VimFu curriculum. It's a pretty complete Vim and `tmux` implementation.

The bigger examples are much more consequential. OpenAI published a [proposed solution to the Navier–Stokes Millennium Prize Problem](https://openai.com/index/navier-stokes-solution/) with a Lean formalization. Lean is the golden oracle that can check the proof. Brandon Thomas's [ArtCraft applications](https://getartcraft.com/apps) are an eye-opening adjacent example: open-source clones of Photoshop, Illustrator, Premiere, After Effects, Lightroom, InDesign, Word, PowerPoint, Excel, and more. The original applications can supply the expected behavior. The [FilmCraft agent instructions](https://github.com/storytold/filmcraft/blob/main/AGENTS.md) explicitly allow black-box observation of the reference application while forbidding access to its internals. Some of his clones are still early, but they look and behave like the real applications. One guy plus Claude. Astonishing.

Getting the human out of the implementation loop is useful. Letting the AI see and touch its own artifact is super important. But the real unlock is a golden oracle: something outside the model that can say, objectively, “No. That is not the right answer.” Human judgment can stay where it belongs -- choosing the goal, judging taste, and deciding whether the thing was worth building at all.

### Follow-on: every LLM output is a hallucination

I think of a golden oracle as the scientific method applied to AI. I think everything an LLM produces is a hallucination of sorts. The model isn't finding the correct answer. It's producing what *looks like* the most plausible completion of your prompt. A conjecture. Generating conjectures is also a form of creativity. The problem is allowing a plausible conjecture to become an accepted answer without exposing it to reality. Correctness is a separate, external measurement.

Humans hallucinate too. The ancient Greeks explained lightning with Zeus and the sea with Poseidon. There was no clean way to prove those explanations false. Whole cultures could repeat and elaborate the same story until agreement felt like verification. In this sense, ancient myths and religions were collective human hallucinations. Swarms of agents verifying each other can do the same thing.

The scientific method gave us a way out. It closes the loop on human conjecture through Nature. We still generate all kinds of crazy explanations, but Nature determines when they're false. Nature is the ultimate golden oracle.

Essentially, AI needs the same solution: a golden oracle that closes the loop through some external reality. Otherwise, we risk building artifacts on foundations of myth.
