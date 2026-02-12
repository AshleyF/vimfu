"""
ShellPilot Lesson Player

Plays VimFu lessons defined as JSON files. Each JSON file is the
single source of truth for a lesson — this module parses the JSON
and orchestrates the demo (setup, recording, steps, teardown).

Usage:
    python player.py path/to/lesson.json
    python player.py ../curriculum/0001_what_is_vim.json
"""

import json
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union


#  Step Types 

@dataclass
class Comment:
    """Display a comment/narration in the log."""
    text: str

    def execute(self, demo):
        demo.comment(self.text)


@dataclass
class Say:
    """Speak text aloud using text-to-speech."""
    text: str
    wait: bool = True

    def execute(self, demo):
        demo.say(self.text, wait=self.wait)


@dataclass
class Type:
    r"""Type text character by character. Supports \b for backspace, \n for enter."""
    text: str

    def execute(self, demo):
        demo.type_text(self.text)


@dataclass
class Keys:
    """Send raw keystrokes.

    Args:
        keys: One or more characters to send (e.g. "q", "qa", "gg").
              Multi-character strings are sent as one action and shown
              as a single overlay.
        overlay: Override the key-overlay caption.  Pass "" to suppress.
    """
    keys: str
    overlay: str = None

    def execute(self, demo):
        demo.send_keys(self.keys, overlay=self.overlay)


@dataclass
class Line:
    """Send a command line (typed char by char then Enter)."""
    command: str
    delay: float = None

    def execute(self, demo):
        demo.send_line(self.command, delay=self.delay)


@dataclass
class Wait:
    """Pause for a duration (seconds, adjusted by speed)."""
    seconds: float = 0.5

    def execute(self, demo):
        demo.wait(self.seconds)


@dataclass
class Escape:
    """Send the Escape key."""

    def execute(self, demo):
        demo.send_escape()


@dataclass
class Enter:
    """Send the Enter key."""

    def execute(self, demo):
        demo.send_enter()


@dataclass
class Backspace:
    """Send backspace key(s)."""
    count: int = 1

    def execute(self, demo):
        demo.send_backspace(self.count)


@dataclass
class Ctrl:
    """Send a control character (e.g., Ctrl+C)."""
    char: str

    def execute(self, demo):
        demo.send_ctrl(self.char)


@dataclass
class Pause:
    """Pause and wait for human Enter press (interactive)."""
    message: str = "Press Enter to continue..."

    def execute(self, demo):
        demo.pause(self.message)


@dataclass
class IfScreen:
    """Conditionally send keys if the screen contains text."""
    contains: str
    then_keys: str

    def execute(self, demo):
        demo.if_screen_contains(self.contains, self.then_keys)


@dataclass
class WaitForScreen:
    """Wait for text to appear on screen."""
    text: str
    timeout: float = 5.0

    def execute(self, demo):
        demo.wait_for_screen(self.text, self.timeout)


@dataclass
class Overlay:
    """Show a visual overlay with optional caption."""
    text: str
    caption: str = ""
    duration: float = 2.0

    def execute(self, demo):
        demo.show_overlay(self.text, self.caption, self.duration)


@dataclass
class WriteFile:
    """Write content to a file via heredoc.

    Content is automatically dedented (leading common whitespace removed).
    """
    path: str
    content: str

    def execute(self, demo):
        clean = textwrap.dedent(self.content).strip()
        # Use absolute sleeps (not speed-adjusted) to prevent ConPTY
        # buffer deadlock when running in fast mode.
        demo.send_keys(f"cat << 'VIMFU_EOF' > {self.path}\n")
        time.sleep(0.1)
        for line in clean.split('\n'):
            demo.send_keys(line + '\n')
            time.sleep(0.05)
        demo.send_keys('VIMFU_EOF\n')
        time.sleep(0.3)


# Type alias for any step
Step = Union[
    Comment, Say, Type, Keys, Line, Wait, Escape, Enter,
    Backspace, Ctrl, Pause, IfScreen, WaitForScreen, Overlay, WriteFile,
]


#  Demo Definition 

@dataclass
class Demo:
    """A complete demo definition — parsed from JSON, executed by the player."""

    title: str = "Demo"
    steps: list[Step] = field(default_factory=list)
    setup: list[Step] = field(default_factory=list)
    teardown: list[Step] = field(default_factory=list)
    speed: float = 1.0
    rows: int = 24
    cols: int = 80
    click_keys: bool = True
    click_volume: float = 0.15
    humanize: float = 0.5
    mistakes: float = 0.0
    seed: int = None
    tts_enabled: bool = True
    tts_voice: str = "nova"
    record_video: bool = True
    video_fps: int = 30
    borderless: bool = True
    target_width: int = 1080
    target_height: int = 1080
    description: str = ""
    tags: list[str] = field(default_factory=list)
    playlist: str = ""

    def run(self, show_viewer: bool = True, output_name: str = None) -> None:
        """Execute the demo.

        Args:
            show_viewer: Whether to show the viewer window.
            output_name: Override the output directory/file name.
                         Defaults to the script filename stem.
        """
        from viewer import ScriptedDemo

        self._precache_tts()

        # Derive output title
        if output_name:
            title = output_name
        elif sys.argv[0]:
            title = Path(sys.argv[0]).stem
        else:
            title = self.title

        with ScriptedDemo(
            rows=self.rows,
            cols=self.cols,
            speed=self.speed,
            show_viewer=show_viewer,
            click_keys=self.click_keys,
            click_volume=self.click_volume,
            humanize=self.humanize,
            mistakes=self.mistakes,
            seed=self.seed,
            tts_enabled=self.tts_enabled,
            tts_voice=self.tts_voice,
            record_video=self.record_video and show_viewer,
            video_fps=self.video_fps,
            title=title,
            borderless=self.borderless,
            auto_start_recording=False,
            target_width=self.target_width,
            target_height=self.target_height,
        ) as demo:
            # Setup (not recorded) — fast, silent
            self._run_fast(demo, self.setup)

            # Flush delay: let pyte finish processing setup output
            time.sleep(3.0)

            # Start recording
            if self.record_video and show_viewer:
                demo.start_recording()

            # Main steps (recorded)
            for step in self.steps:
                step.execute(demo)

            # Stop recording
            if self.record_video and show_viewer:
                demo.stop_recording()
                self._generate_extras(demo, title)

            # Teardown (not recorded)
            self._run_fast(demo, self.teardown)

    def _generate_extras(self, demo, title: str) -> None:
        """Generate thumbnail PNG after recording."""
        recorder = demo.recorder
        if not recorder:
            return

        # Thumbnail caption from first Overlay step
        overlay_caption = ""
        for step in self.steps:
            if isinstance(step, Overlay):
                overlay_caption = step.caption
                break

        try:
            recorder.save_thumbnail(
                overlay_title="VimFu",
                overlay_caption=overlay_caption,
            )
        except Exception as e:
            print(f"[THUMB] Error generating thumbnail: {e}")

    @staticmethod
    def _run_fast(demo, steps: list) -> None:
        """Run steps at maximum speed, no clicks, no humanization."""
        if not steps:
            return

        orig_speed = demo.speed
        orig_char_delay = demo.char_delay
        orig_base_delay = demo.base_delay
        orig_humanize = demo.humanize
        orig_mistakes = demo.mistakes
        orig_clicks = demo.clicker.enabled

        demo.speed = 100.0
        demo.char_delay = 0.001
        demo.base_delay = 0.001
        demo.humanize = 0.0
        demo.mistakes = 0.0
        demo.clicker.enabled = False

        try:
            for step in steps:
                step.execute(demo)
                if isinstance(step, WriteFile):
                    time.sleep(2.0)
                elif isinstance(step, Line):
                    time.sleep(0.5)
                elif isinstance(step, WaitForScreen):
                    time.sleep(1.0)
        finally:
            demo.speed = orig_speed
            demo.char_delay = orig_char_delay
            demo.base_delay = orig_base_delay
            demo.humanize = orig_humanize
            demo.mistakes = orig_mistakes
            demo.clicker.enabled = orig_clicks

    def _precache_tts(self) -> None:
        """Pre-generate all TTS audio so playback is instant."""
        if not self.tts_enabled:
            return

        all_texts = [s.text for s in self.setup + self.steps + self.teardown
                     if isinstance(s, Say)]
        if not all_texts:
            return

        from tts import TextToSpeech, get_cache_path

        tts = TextToSpeech(voice=self.tts_voice, enabled=True)
        uncached = [t for t in all_texts
                    if not get_cache_path(t, tts.voice, tts.model).exists()]
        if not uncached:
            return

        print(f"[TTS] Pre-caching {len(uncached)} of {len(all_texts)} audio clips...")
        try:
            tts.pregenerate(uncached)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[TTS] Pre-caching error (continuing anyway): {e}")

        still_missing = [t for t in uncached
                         if not get_cache_path(t, tts.voice, tts.model).exists()]
        if still_missing:
            print(f"[TTS] Warning: {len(still_missing)} clips could not be generated")
        else:
            print("[TTS] Pre-caching complete.")


#  JSON Parsing 

def _parse_step(item):
    """Parse a single step from its JSON representation."""
    if isinstance(item, str):
        if item == "escape":
            return Escape()
        if item == "enter":
            return Enter()
        raise ValueError(f"Unknown string step: {item!r}")

    if not isinstance(item, dict):
        raise ValueError(f"Step must be a string or object, got {type(item).__name__}")

    if "comment" in item:
        return Comment(item["comment"])
    if "say" in item:
        return Say(item["say"], wait=item.get("wait", True))
    if "type" in item:
        return Type(item["type"])
    if "keys" in item:
        return Keys(item["keys"], overlay=item.get("overlay", None))
    if "line" in item:
        return Line(item["line"], delay=item.get("delay", None))
    if "wait" in item:
        return Wait(item["wait"])
    if "backspace" in item:
        return Backspace(item["backspace"])
    if "ctrl" in item:
        return Ctrl(item["ctrl"])
    if "pause" in item:
        return Pause(item["pause"])
    if "ifScreen" in item:
        return IfScreen(item["ifScreen"], item["thenKeys"])
    if "waitForScreen" in item:
        return WaitForScreen(item["waitForScreen"], timeout=item.get("timeout", 5.0))
    if "overlay" in item:
        return Overlay(item["overlay"], caption=item.get("caption", ""),
                       duration=item.get("duration", 2.0))
    if "writeFile" in item:
        return WriteFile(item["writeFile"], item["content"])

    raise ValueError(f"Unknown step type: {item!r}")


def _parse_steps(items):
    """Parse a list of step definitions."""
    return [_parse_step(item) for item in items]


def load_lesson(json_path: Path) -> Demo:
    """Load a lesson JSON file and return a Demo object."""
    data = json.loads(json_path.read_text(encoding="utf-8"))

    return Demo(
        title=data.get("title", "Demo"),
        description=data.get("description", ""),
        speed=data.get("speed", 1.0),
        rows=data.get("rows", 24),
        cols=data.get("cols", 80),
        click_keys=data.get("clickKeys", True),
        click_volume=data.get("clickVolume", 0.15),
        humanize=data.get("humanize", 0.5),
        mistakes=data.get("mistakes", 0.0),
        seed=data.get("seed", None),
        tts_enabled=data.get("ttsEnabled", True),
        tts_voice=data.get("ttsVoice", "nova"),
        record_video=data.get("recordVideo", True),
        video_fps=data.get("videoFps", 30),
        borderless=data.get("borderless", True),
        target_width=data.get("targetWidth", 1080),
        target_height=data.get("targetHeight", 1080),
        tags=data.get("tags", []),
        playlist=data.get("playlist", ""),
        setup=_parse_steps(data.get("setup", [])),
        steps=_parse_steps(data.get("steps", [])),
        teardown=_parse_steps(data.get("teardown", [])),
    )


#  Entry Points 

def play(json_path: str | Path) -> None:
    """Load and run a lesson from a JSON file."""
    path = Path(json_path)
    if not path.exists():
        print(f"ERROR: {path} not found.")
        sys.exit(1)

    lesson = load_lesson(path)
    lesson.run(output_name=path.stem)


def main():
    if len(sys.argv) < 2:
        print("Usage: python player.py <lesson.json>")
        sys.exit(1)

    play(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
