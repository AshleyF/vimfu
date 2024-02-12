module Lesson

open Script

let nothing =
    [ Launch
      Setup ["Test"; "01234567890123456789"; "Line 3"]
      SetFileType "text"
      Start "Just Testing"
      Insert
      Pause 20000
      Finish ]

let tracey = // first ever test of the system
    [ Launch
      Start "Hey Tracey"
      Move BottomOfDocument
      Move Up
      ZoomMiddle
      Pause 500
      Insert
      Say "Okay..."
      SayWhile ("This is a test", Text "This is a test")
      Pause 100
      Enter
      Pause 100
      SayWhile ("And another", Text "This is another...")
      Esc
      Pause 500
      Say "Let's undo that..."
      Move Up
      SayWhile ("... with two delete line", Normal ("2dd", "two delete line"))
      OpenAbove
      Esc
      Insert
      SayWhile ("Hey Tracey!", Text "I like you!")
      Esc
      Say "Now watch this"
      Pause 500
      SayWhile ("Back two words", Normal ("2b", "two back"))
      SayWhile ("Change word", Normal ("cw", "change word"))
      Text "really love"
      Esc
      Finish ]

let dontRepeat = // using dot
    [ Launch
      Setup ["var foo = 1"; "var bar = 'a'"; "var foobar = foo + bar"]
      Start "Don't Repeat Yourself"
      Say "Let's say that we want to add semicolons after each line."
      SayWhile ("We could use dollar to move to the end of the first line.", Move EndOfLine)
      SayWhile ("Then A for after.", After)
      SayWhile ("Type a semicolon", Text ";")
      SayWhile ("Then escape to return to normal mode.", Esc)
      Say "This is a little tedious"
      SayWhile ("Down a line", Move Down)
      SayWhile ("And do it again. End of line.", Move EndOfLine)
      SayWhile ("After.", After)
      SayWhile ("Semicolon.", Text ";")
      SayWhile ("And escape.", Esc)
      Say "And once more."
      SayWhile ("Down", Move Down)
      SayWhile ("End", Move EndOfLine)
      SayWhile ("After.", After)
      SayWhile ("Semicolon.", Text ";")
      SayWhile ("And one last escape.", Esc)
      Say "This has taken us 14 keystrokes and a lot of repetition."
      Say "Let's see if there's a better way."
      Say "Undoing all of that."
      SayWhile ("Undo.", Undo)
      SayWhile ("Undo.", Undo)
      SayWhile ("Undo.", Undo)
      SayWhile ("And back to the start.", Move FirstColumn)
      SayWhile ("Instead let's use Shift-A to insert after the line in a single action.", AfterLine)
      SayWhile ("Type a semicolon", Text ";")
      SayWhile ("Then escape to normal mode.", Esc)
      Say "Best of all, this whole action can be replayed with the period or 'dot' key."
      SayWhile ("Down a line", Move Down)
      SayWhile ("Then just press dot to repeat.", Repeat)
      Say "Isn't that cool?"
      SayWhile ("Then down again", Move Down)
      SayWhile ("A repeat once more", Repeat)
      Say "And we're done, in just seven keystrokes."
      Say "It's important to note that dot remembers a single action, so using Shift-A instead of dollar followed by A, not only saves a keystroke, but makes it repeatable with dot."
      Say "Still, even down, dot, down, dot, can be repetitive with many lines."
      SayWhile ("Let's undo all of this again.", Compound (150, [Undo; Undo; Undo; Move FirstColumn]))
      SayWhile ("And let's make more lines; yanking to the last line.", YankToLastLine)
      SayWhile ("Then put it back several times.", PutBefore)
      SayWhile ("Put.", PutBefore)
      SayWhile ("Put.", PutBefore)
      SayWhile ("Put.", PutBefore)
      Say "Again, let's add semicolons after each line, but this time we'll recored a macro."
      SayWhile ("Press Q Q to record. Q is the record key and I like to use Q as a quick temporary macro register.", Record 'q')
      SayWhile ("Then do Shift-A to insert after the line as before.", AfterLine)
      SayWhile ("Add our semicolon", Text ";")
      SayWhile ("And escape.", Esc)
      SayWhile ("And down a line, while still recording.", Move Down)
      SayWhile ("And finally, stop recording.", StopRecording)
      SayWhile ("If we play the macro back now with at Q, it adds the semicolon and advances to the next line.", Macro 'q')
      SayWhile ("We can press at, at to repeat again.", RepeatLastMacro)
      SayWhile ("And again.", RepeatLastMacro)
      Say "Or we can repeat the macro the remaining 11 times in one shot!"
      SayWhile ("With eleven at !", RepeatMacro ('q', 11))
      Say "We've made pretty quick work of that with the power of Vim!"
      Finish ]

let numbers = // numbering list with `g^a`
    [ Launch
      Start "Numbering Lists"
      Say "Here's a quick trick to create numbered lists."
      Insert
      Text "Milk"
      Pause 100
      Enter
      Text "Bread"
      Pause 100
      Enter
      Text "Hot dogs"
      Pause 100
      Enter
      Text "Mustard"
      Pause 100
      Enter
      Text "Jalapenos"
      Esc
      Say "To add numbers, we can go to the first column."
      Move FirstColumn
      Say "And select block with Control-V"
      SelectBlock
      Pause 800
      SayWhile ("And move to the top with G G.", Move TopOfDocument)
      Pause 800
      SayWhile ("Then insert before with Shift-I.", InsertBefore)
      Pause 800
      SayWhile ("And number the line with a zero.", Text "0. ")
      Pause 800
      SayWhile ("Escape then does this to the whole vertical selection.", Esc)
      Say "That's pretty neat by itself. Here's the trick though."
      SayWhile ("We reselect the first column with G V.", Reselect)
      Pause 800
      SayWhile ("And press G followed by Control-A to increment as ordinals.", IncrementOrdinals)
      Say "It automatically increments the whole select in order. Very cool!"
      Finish ]

let alignText = // aligning text with `:norm` commands
    [ Launch
      Setup ["{ first: \"Ash\","; "  last: \"Ford\","; "  height: 1.83,"; "  age: 50,"; "  eyes: \"blue\" }"]
      SetFileType "javascript"
      Start "Align Text"
      Pause 2000
      Say "The property names here are nicely aligned on the left, but the values aren't."
      SayWhile ("It looks like the height is furthest over.", Compound (150, [Move Down; Move Down; Move (Find '1')]))
      Say "We can see that it's at column eleven."
      Say  "Here's the trick."
      SayWhile ("We select the block.", Compound (150, [SelectBlock; Move (Span AroundBlock)]))
      SayWhile ("And enter a normal mode command with colon-norm.", Text ":norm ")
      Say "This will apply normal mode command to every selected line."
      SayWhile ("We'll find the colon...", Text "f:")
      SayWhile ("And insert 4 spaces after it.", Text "4a ")
      Enter
      Say "Look at that. Of course it's too much space for some of them."
      SayWhile ("We'll reselect the block.", Reselect)
      SayWhile ("And with another normal mode command...", Text ":norm ")
      SayWhile ("We can go to column eleven on each line.", Text "11|")
      SayWhile ("And delete word.", Text "dw")
      Enter
      Say "And voila! Applying commands to every line is a great trick."
      Finish ]

let loremIpsum = [
    "Lorem ipsum dolor "; "sit amet, "; "consectetur "; "adipiscing elit, "; "sed do eiusmod "
    "tempor incididunt "; "ut labore et dolore "; "magna aliqua. Ut "; "enim ad minim "
    "veniam, quis "; "nostrud "; "exercitation "; "ullamco laboris "; "nisi ut aliquip ex "
    "ea commodo "; "consequat. Duis "; "aute irure dolor in "; "reprehenderit in "
    "voluptate velit esse "; "cillum dolore eu "; "fugiat nulla "; "pariatur. Excepteur "
    "sint occaecat "; "cupidatat non "; "proident, sunt in "; "culpa qui officia "
    "deserunt mollit "; "anim id est "; "laborum. " ]

let basicMotions1 = // h j k l ␣ ⌫
    [ Launch
      Setup loremIpsum
      Pause 10000
      SetFileType "text"
      Start "Basic Motions 1"
      SayWhile ("In Vim, we can certainly move around with the arrow keys...", Compound (250, [
        Key ("↓", "down arrow", "{Down}")
        Key ("↓", "down arrow", "{Down}")
        Key ("↓", "down arrow", "{Down}")
        Key ("↓", "down arrow", "{Down}")
        Key ("↓", "down arrow", "{Down}")
        Key ("→", "right arrow", "{Right}")
        Key ("→", "right arrow", "{Right}")
        Key ("→", "right arrow", "{Right}")
        Key ("→", "right arrow", "{Right}")
        Key ("→", "right arrow", "{Right}")
        Key ("↑", "up arrow", "{Up}")
        Key ("↑", "up arrow", "{Up}")
        Key ("↑", "up arrow", "{Up}")
        Key ("↑", "up arrow", "{Up}")
        Key ("↑", "up arrow", "{Up}")
        Key ("←", "left arrow", "{Left}")
        Key ("←", "left arrow", "{Left}")
        Key ("←", "left arrow", "{Left}")
        Key ("←", "left arrow", "{Left}")
        Key ("←", "left arrow", "{Left}") ]))
      Say "But the Vim way of doing things is to use the home row keys."
      Pause 500
      SayWhile ("J to move down...", Compound (250, [Move Down; Move Down; Move Down; Move Down; Move Down]))
      Pause 1000
      SayWhile ("L to move right...", Compound (250, [Move Right; Move Right; Move Right; Move Right; Move Right]))
      Pause 1000
      SayWhile ("K to move up...", Compound (250, [Move Up; Move Up; Move Up; Move Up; Move Up]))
      Pause 500
      SayWhile ("and H to move left...", Compound (250, [Move Left; Move Left; Move Left; Move Left; Move Left]))
      Pause 1000
      SayWhile ("You can also move right with space...", Compound (250, [Key ("␣", "space", "l"); Key ("␣", "space", " "); Key ("␣", "space", " "); Key ("␣", "space", " "); Key ("␣", "space", " ")]))
      Pause 1000
      SayWhile ("and move left with backspace.", Compound (250, [Key ("⌫", "backspace", "h"); Key ("⌫", "backspace", "h"); Key ("⌫", "backspace", "h"); Key ("⌫", "backspace", "h"); Key ("⌫", "backspace", "h")]))
      Pause 500
      Say "These are the most basic movements."
      Finish ]

let basicMotions2 = // w b e ge
    [ Launch
      Setup loremIpsum
      Pause 10000
      SetFileType "text"
      Start "Basic Motions 2"
      SayWhile ("In Vim, we can move by words with W...", Compound (400, [Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word]))
      Pause 1000
      SayWhile ("And with B for back by words.", Compound (400, [Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord]))
      Pause 1000
      SayWhile ("Notice that it moves to the beginning of each word.", Compound (800, [Move Word; Move Word; Move Word; Move BackWord; Move BackWord; Move BackWord]))
      Pause 1000
      SayWhile ("Pressing E moves to the end of each word.", Compound (400, [Move WordEnd; Move WordEnd; Move WordEnd; Move WordEnd; Move WordEnd; Move WordEnd; Move WordEnd]))
      Pause 1000
      SayWhile ("And finally, G followed by E moves back to the end of each previous word.", Compound (400, [Move BackWordEnd; Move BackWordEnd; Move BackWordEnd; Move BackWordEnd; Move BackWordEnd; Move BackWordEnd]))
      Pause 500
      SayWhile ("With W...", Compound (400, [Move Word; Move Word]))
      SayWhile ("...B...", Move BackWord)
      SayWhile ("...E...", Move WordEnd)
      SayWhile ("...and G followed by E, we can quickly move by words forward and backward to the start and end of each.", Move BackWordEnd)
      Finish ]

let basicMotions3 = // W B E gE
    [ Launch
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
      Pause 10000
      SetFileType "python"
      Start "Basic Motions 3"
      Compound (0, [Move Down; Move Down; Move Down; Move Down; Move Down])
      SayWhile ("You may have noticed that navigating by words with lowercase W stops at punctuation.", Compound (400, [Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word]))
      Pause 1000
      SayWhile ("The same happens when moving back by words with B. It stops at each bit of punctuation.", Compound (400, [Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord; Move BackWord]))
      Pause 1000
      Say  "It may be quicker to navigate by so-called 'big words'. Here's how:"
      SayWhile ("Shift W moves forward by big words.", Compound (400, [Move BigWord; Move BigWord; Move BigWord; Move BigWord; Move BigWord; Move BigWord; Move BigWord; Move BigWord]))
      Pause 800
      Say "This treats words as consisting of any non-whitespace characters."
      Pause 800
      SayWhile ("Shift-B moves back by big words.", Compound (800, [Move BackBigWord; Move BackBigWord; Move BackBigWord; Move BackBigWord]))
      Pause 1000
      SayWhile ("Likewise, Shift-E moves to the end of big words.", Compound (800, [Move BigWordEnd; Move BigWordEnd; Move BigWordEnd]))
      Pause 1000
      SayWhile ("And finally G followed by Shift-E, moves to the end of each previous big word.", Compound (800, [Move BackBigWordEnd; Move BackBigWordEnd; Move BackBigWordEnd]))
      Pause 800
      SayWhile ("With Shift-W...", Compound (400, [Move BigWord; Move BigWord]))
      SayWhile ("Shift-B...", Move BackBigWord)
      SayWhile ("Shift-E...", Move BigWordEnd)
      SayWhile("...and G followed by Shift-E...", Move BackBigWordEnd)
      Say "...we can very quickly move by big words."
      Finish ]

let basicMotions4 = // $ ^ 0
    [ Launch
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
      Pause 10000
      SetFileType "python"
      Start "Basic Motions 4"
      Compound (0, [Move Down; Move Down])
      Say "Here are some more basic horizontal motions."
      SayWhile ("You can move to the end of a line with dollar.", Move EndOfLine)
      Pause 1000
      SayWhile ("And to the start of a line with carrot.", Move StartOfLine)
      Say "You may recognize dollar and carrot from regular expressions."
      Pause 1000
      SayWhile ("Notice that carrot actually moves to the first non-blank character of a line.", Move Down)
      SayWhile ("Carrot", Move StartOfLine)
      Pause 800
      SayWhile ("Dollar", Move EndOfLine)
      Pause 800
      SayWhile ("Carrot", Move StartOfLine)
      Pause 1000
      Say "To move to the first column even when it's blank..."
      SayWhile ("...press zero.", Move FirstColumn)
      Pause 1000
      Say "To recap..."
      SayWhile ("...dollar moves to the end...", Move EndOfLine)
      Pause 800
      SayWhile ("...carrot moves to the first non-blank character...", Move StartOfLine)
      Pause 800
      SayWhile ("...and zero moves to the first column.", Move FirstColumn)
      Finish ]

let basicMotions5 = // H L M gg G
    [ Launch
      Setup ["def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    fib(n-2)"; ""; "print(fib(7))"]
      Pause 10000
      SetFileType "python"
      Start "Basic Motions 5"
      Compound (0, [Move Down; Move Down])
      Say "Here are a few basic vertical motions."
      SayWhile ("You can move to the lowest line on the screen with Shift-L", Move LowestLine)
      Pause 1000
      SayWhile ("And back to the highest visible line with Shift-H.", Move HighestLine)
      Pause 1000
      SayWhile ("Or to the middle line with Shift-M", Move MiddleLine)
      Pause 1000
      SayWhile ("Notice that, if our cursor is somewhere within a line, the column is maintained.", Move WordEnd)
      Pause 800
      SayWhile ("Highest", Move HighestLine)
      Pause 500
      SayWhile ("Middle", Move MiddleLine)
      Pause 500
      SayWhile ("Lowest", Move LowestLine)
      Pause 600
      Say "These keys work with what's currently visible on the screen."
      SayWhile ("There's more text below...", Compound (400, [Move Down; Move Down; Move Down; Move Down; Move Down]))
      Pause 1000
      Say "We can move to the top of the whole document with..."
      SayWhile ("...GG", Move TopOfDocument)
      Pause 1000
      Say "And back to the bottom of the whole document with..."
      SayWhile ("...Shift-G", Move BottomOfDocument)
      Pause 1000
      Say "To recap..."
      SayWhile ("...Shift-H moves to the highest visible line.", Move HighestLine)
      Pause 800
      SayWhile ("...Shift-M for middle of the screen...", Move MiddleLine)
      Pause 800
      SayWhile ("...and Shift-L for the lowest visible line.", Move LowestLine)
      Pause 800
      SayWhile ("GG takes us to the top of the document...", Move TopOfDocument)
      Pause 800
      SayWhile ("... and Shift-G takes us to the bottom of the document...", Move BottomOfDocument)
      Pause 800
      Finish ]

let basicMotions6 = // ) ( } {
    [ Launch
      Setup ["# It's a sentence.  And again!          And another         one... How          about this? Indeed!"; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    (n-2)"; ""; "print(fib(7))"]
      Pause 10000
      SetFileType "python"
      Start "Basic Motions 6"
      Say "We can move back and forth by whole sentences with..."
      SayWhile ("...right parenthesis to move to each next sentence...", Compound (800, [Move Sentence; Move Sentence; Move Sentence; Move Sentence]))
      Pause 1000
      SayWhile ("... and left parenthesis to move back by sentences...", Compound (800, [Move BackSentence; Move BackSentence; Move BackSentence; Move BackSentence]))
      Pause 1000
      SayWhile ("Sentences are terminated by period, exclamation point or question mark, followed by whitespace.", Compound (800, [Move Sentence; Move Sentence; Move Sentence; Move Sentence; Move BackSentence; Move BackSentence; Move BackSentence; Move BackSentence]))
      Pause 1000
      Say "We can also move up an down by paragraphs with..."
      SayWhile ("...right curly brace to move down to each next paragraph...", Compound (800, [Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph]))
      Pause 1000
      SayWhile ("... and left curly brace to move back up by paragraphs", Compound (800, [Move BackParagraph; Move BackParagraph; Move BackParagraph; Move BackParagraph; Move BackParagraph]))
      Pause 1000
      Say "Paragraphs are separated by blank lines."
      Pause 1000
      SayWhile ("Using left and right parenthesis and left and right curly braces is a nice way to quickly navigate by sentences and paragraphs.", Compound (800, [Move Sentence; Move Sentence; Move Sentence; Move Sentence; Move BackSentence; Move BackSentence; Move BackSentence; Move BackSentence; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move BackParagraph; Move BackParagraph; Move BackParagraph; Move BackParagraph; Move BackParagraph]))
      Pause 800
      Finish ]

let basicMotions7 = // ]] [[ ][ []
    [ Launch
      Setup ["#include <stdio.h>"; ""; "int isEven(int n)"; "{"; "  return n % 2 == 0;"; "}"; ""; "void msg(char *m)"; "{"; "  printf(\"%s\\n\",m);"; "}"; ""; "int main()"; "{"; "  if (!isEven(42))"; "  {"; "    msg(\"Panic!\");"; "  }"; "  return 0;"; "}"; ""]
      Pause 10000
      Text ":set cursorline"
      Enter
      SetFileType "c"
      Start "Basic Motions 7"
      Say "In curly brace languages, it's nice to navigate by sections."
      Pause 800
      SayWhile ("Right bracket bracket moves down to the curly brace at the start of each section.", Compound (800, [Move SectionStart; Move SectionStart; Move SectionStart; Move SectionStart]))
      Say "Stopping at the bottom of the document."
      Pause 800
      SayWhile ("Left bracket bracket moves back up to the start of each section.", Compound (800, [Move BackSectionStart; Move BackSectionStart; Move BackSectionStart; Move BackSectionStart]))
      Say "Stopping at the top of the document."
      Pause 800
      Say "A section is a block of lines surrounded by curly braces in the first column."
      Pause 800
      SayWhile ("Notice that down here...", Compound (200, [Move SectionStart; Move SectionStart; Move SectionStart]))
      SayWhile ("Section navigation doesn't include the if statement because those curly braces are not in the first column.", Compound (800, [Move SectionStart; Move BackSectionStart; Move SectionStart; Move BackSectionStart]))
      Pause 800
      Say "We can also move up to the end, rather than the start, of each section with..."
      SayWhile (".. left-bracket right-bracket.", Compound (800, [Move BackSectionEnd; Move BackSectionEnd; Move BackSectionEnd]))
      Pause 800
      Say "Or move down to the end of each section with..."
      SayWhile (".. right-bracket left-bracket.", Compound (800, [Move SectionEnd; Move SectionEnd; Move SectionEnd]))
      Pause 800
      SayWhile ("Combinations of pairs of brackets make navigation pretty quick.", Compound (200, [Move BackSectionStart; Move BackSectionStart; Move BackSectionStart; Move BackSectionStart; Move SectionEnd; Move SectionEnd; Move SectionEnd; Move SectionEnd; Move BackSectionEnd; Move BackSectionEnd; Move BackSectionEnd; Move BackSectionEnd; Move BackSectionEnd; Move SectionEnd; Move SectionEnd; Move SectionEnd; Move SectionEnd; Move SectionEnd]))
      Finish ]

let basicMotions8 = // + - <CR>
    [ Launch
      Setup ["def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    fib(n-2)"; ""; "print(fib(7))"]
      Pause 10000
      SetFileType "python"
      Start "Basic Motions 8"
      SayWhile ("From anywhere in a line we can move to the start of the next line with plus.", Move BigWord)
      SayWhile ("This moves down a line and to the first non-blank character.", Compound (400, [Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; Move StartOfNextLine; ]))
      Pause 800
      SayWhile ("Pressing Enter also does this, and without needing to hold shift.", Compound (400, [Move StartOfNextLineCR; Move StartOfNextLineCR; Move StartOfNextLineCR; Move StartOfNextLineCR; ]))
      SayWhile ("The minus key moves up.", Compound (300, [Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; ]))
      Say "Easy enough!"
      Finish ]

let matchingPairs = // %
    [ 
      //Launch // launch opens nvim via Ubuntu and matching is broken for some reason (manually launch nvim directly instead)
      Pause 10000
      Setup ["{ x = true"; "  y = [1; 2; 3]"; "  z = ((4, 2),"; "       \"life\")"; "} |> test"; ""; ""; ""]
      Pause 10000
      SetFileType "ocaml"
      Start "Matching Pairs"
      Say "It can be quite handy to quickly jump between matching pairs of braces and brackets."
      Pause 300
      SayWhile ("We can jump between these curly braces by pressing percent.", Compound(500, [Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces]))
      Pause 500
      SayWhile ("It works with square brackets too.", Move Down)
      Say "Notice that we don't have to be on the first bracket for it to work."
      Pause 200
      Say "Pressing percent from here at the first column..."
      SayWhile ("...finds the first bracket and jumps to it's pair at the end of the line.", Move MatchingBraces)
      Pause 200
      SayWhile ("The same is true when the cursor is inside the brackets.", Compound (0, [Move Left; Move Left; Move Left; Move Left]))
      Pause 200
      SayWhile ("Pressing percent finds the closing bracket.", Move MatchingBraces);
      Pause 200
      SayWhile ("From there, pressing percent jumps between the pairs.", Compound (500, [Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces]))
      Pause 200
      SayWhile ("Of course, it works with parenthesis as well.", Move Down)
      Pause 200
      Compound(500, [Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces])
      Pause 200
      SayWhile ("And works with nesting.", Move Right)
      Compound(500, [Move MatchingBraces; Move MatchingBraces; Move MatchingBraces; Move MatchingBraces])
      Say "Pretty handy!"
      Finish ]

let uselessUnderscore = // _
    let underscore = Key ("⇧_", "", "_")
    [ Launch
      Setup ["{ first: \"Ash\","; "  last: \"Ford\","; "  height: 1.83,"; "  age: 50,"; "  eyes: \"blue\" }"]
      Pause 10000
      SetFileType "ocaml"
      Start "Useless Underscore"
      SayWhile ("The underscore key is virtually useless.", Compound (0, [Move WordEnd; Move Down]))
      Pause 600
      SayWhile ("When pressed, it does the same thing as the carrot key by moving to the first non-blank character of the current line.", Key ("⇧_", "start of line", "{^}"))
      Pause 600
      SayWhile ("One difference is that carrot doesn't use a count, but underscore does; moving down by n minus 1 lines.", Move BigWordEnd)
      SayWhile ("Three underscore, moves down two lines.", Key ("3⇧_", "start of line", "{+}{+}"))
      Pause 600
      SayWhile("But we already have similar behavior with the plus key", Compound (0, [Move Up; Move Up; Move BigWordEnd]))
      Pause 600
      SayWhile ("Two plus also moves down 2 lines.", Key ("2⇧+", "start of next line", "{+}{+}"))
      Pause 600
      Say "So I don't see a use for underscore that isn't already covered by carrot and plus."
      Pause 400
      Say "We can't let a key go unused though!"
      Pause 400
      SayWhile ("So I personally map it...", Text ":map _ ")
      Pause 400
      SayWhile ("...to insert a space...", Text "i ")
      SayWhile ("...and return to normal mode...", Text "<Esc>")
      Say "You'd be surprised how handy this is!"
      Pause 400
      Enter
      SayWhile ("For example, we can quickly align this while in normal mode.", Compound (100, [Move BigWord]))
      Pause 500
      Compound (200, [underscore; underscore; underscore])
      Pause 800
      Move Down
      Pause 500
      Compound (200, [underscore; underscore])
      Pause 800
      Compound (200, [Move Up; Move Up; Move Up])
      Pause 500
      Compound (200, [underscore; underscore])
      Pause 800
      Compound (200, [Move Up; Move Word])
      Pause 500
      underscore
      Say "Much more useful now!"
      Finish ]

let findCharacter = // f t F T ; ,
    [ Launch
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    fib(n-2)"; ""; "print(fib(7))"]
      Pause 10000
      SetFileType "python"
      Move Paragraph; Move Up
      Start "Find Character"
      Say "A quick way to move around a line is to find characters."
      Pause 400
      Say "To jump to the n variable, we can press F, for 'find', followed by N"
      SayWhile ("...and it finds the first N.", Move (Find 'n'))
      Pause 400
      Say "Oops, that's not the N we wanted."
      Pause 200
      Say "Pressing semicolon finds the next one."
      Move (NextChar 'n')
      Pause 600
      SayWhile ("And again to the next.", Move (NextChar 'n'))
      Pause 600
      Say "To go back, press comma."
      Move (PrevChar 'n')
      Pause 600
      Say "Another way is to jump to just before a character, with T, for 'find till'."
      SayWhile ("From the start of the line...", Move FirstColumn)
      Pause 300
      Say "Press T followed by star..."
      Move (Till '*')
      Pause 300
      Say "Taking us to just before the star, which is directly to the N we want."
      Pause 400
      Say "We can also find in the reverse direction with shift F."
      Pause 600
      SayWhile ("From the end of the line...", Move EndOfLine)
      Pause 600
      Say "We can find the previous N with shift F followed by N."
      Move (FindReverse 'n')
      Pause 600
      SayWhile ("And the one before that with semicolon.", Move (NextChar 'n'))
      Say "Semicolon and comma work relative to the original direction."
      Pause 600
      Say "Like shift F, shift T also works in the reverse direction."
      Say "This is a slick way to move around!"
      Finish ]

let search = // * # n N / ?  /<cr>  ?<cr>
    [ Launch
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    fib(n-2)"; ""; "print(fib(7))"]
      Pause 4000
      Move TopOfDocument
      Move Down
      Move Down
      Move Word
      Pause 1000
      SetFileType "python"
      Text ":set nohls"; Enter; Text ":"; Esc
      Start "Search"
      Say "When we want to find the word under the cursor, we can simply press star."
      Move SearchStar
      Say "We can move to the next one by pressing N."
      Move SearchNext
      Say "Or we can move back with shift N."
      Move SearchPrev
      Pause 800
      Move SearchPrev
      Pause 800
      Say "Let's try from the bottom of the document."
      Move BottomOfDocument
      Move Word; Move Word
      Say "We can search in reverse for the word under the cursor by pressing the hash key."
      Move SearchHash
      Pause 800
      Say "And again, pressing N takes us to the next ones."
      Move SearchNext
      Pause 800
      Move SearchNext
      Say "And shift N to traverse them in reverse."
      Move SearchPrev
      Pause 400
      Move SearchPrev
      Pause 400
      Move SearchPrev
      Say "That's quite useful!"
      Pause 1000
      Say "Back to the top of the document."
      Move TopOfDocument
      Say "We can also search for anything we like by pressing slash."
      Key ("/", "search", "/")
      Say "And entering a search pattern"
      Text "fib"
      Say "Pressing enter takes us there."
      Enter
      SayWhile ("Pressing N and shift N cycles through the matches.", Compound (500, [Move SearchNext; Move SearchNext; Move SearchNext; Move SearchPrev; Move SearchPrev; Move SearchPrev]) )
      Pause 1000
      Say "Finally, we can search in reverse by pressing question mark and a pattern"
      Key ("⇧?", "search", "?")
      Pause 100
      Text "fact"
      Pause 1000
      Enter
      Pause 1000
      SayWhile ("Slash enter or question enter, without a search term...", Key ("/", "search", "/"))
      SayWhile ("...re-executes the last search.", Enter)
      Pause 1000
      SayWhile ("This is a powerful way to find our way around!", Compound(800, [Move SearchNext; Move SearchNext; Move SearchNext; Move SearchPrev; Move SearchPrev; Move SearchPrev]))
      Finish ]

let joinLines = // J gJ
    [ Launch
      Pause 5000
      Setup [""; ""; "fruits = ["; "  'lime',"; "  'fig',"; "  'kiwi',"; "  'pear'"; "]";]
      SetFileType "python"
      Move Down; Move Down; Move Down; 
      Start "Join Lines"
      Say "Joining lines is pretty useful. Pressing shift J will join the current line with the one below."
      JoinLine
      Pause 1000
      Say "Notice that it leaves a single space under the cursor."
      Pause 1000
      Move Down
      JoinLine
      Pause 500
      Say "To bring up the final closing bracket, perhaps we don't want a space. For that we can press G followed by shift J"
      Key ("g⇧J", "join line no space", "gJ")
      Pause 1000
      Say "It's surprising how often the J key comes in handy!"
      Finish ]

let quitting = // :q :q! ZQ  :wq :x ZZ  ^z  fg
    [ Launch
      Pause 5000
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
      SetFileType "python"
      Pause 3000
      Text ":file fact.py"; Enter
      Text ":w!"; Enter
      Text "ZZ"; Pause 1000; Text "clear"; Enter; Text "vi fact.py"; Enter
      Start "Quitting"
      Say "It's a running joke that people have to power off their computers to exit Vim, but come on it's really not difficult."
      Pause 500
      Say "Simply pressing ZZ will save and quit."
      Key ("⇧ZZ", "save and quit", "ZZ")
      Pause 2000
      Text "vi fa"; Tab; Enter
      Pause 1000
      SayWhile ("Entering the command colon X does the same thing.", Text ":x")
      Text "\b"
      SayWhile ("Or the more verbose colon W Q also writes and quits.", Text "wq")
      Enter
      Pause 1000
      Text "!!"; Enter; Enter
      Pause 1000
      SayWhile ("If we make a change to the file...", Compound (150, [Move Down; Move Down; Move WordEnd; Move WordEnd; After; Text "orial"; Esc]))
      Say "Then we now have a choice. We can save and quit with ZZ, or we can abandon our changes with ZQ"
      Key ("⇧ZQ", "quit without saving", "ZQ")
      Pause 1000
      Text "!!"; Enter; Enter
      Pause 1000
      Say "When be come back, our changes have not been saved."
      SayWhile ("The command colon Q bang also quits without saving.", Text ":q!")
      SayWhile ("Without the bang quits too, but only when there are no changes to be saved.", Text "\b")
      Pause 500
      Esc
      Say "One more way to get out of Vim is to suspend it with control Z"
      Key ("⌃z", "suspend", "^z")
      Pause 1000
      Say "We can resume the process later with F G"
      Text "fg"; Enter
      Finish ]

let revertFile = // :e!
    [ Launch
      Pause 5000
      Setup [""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"; ""; "def fib(n):"; "  if n <= 1:"; "    return n"; "  return fib(n-1) +"; "    fib(n-2)"; ""; "print(fib(7))"]
      SetFileType "python"
      Text ":file fact.py"; Enter
      Text ":w!"; Enter
      Text "ZZ"; Pause 1000; Text "clear"; Enter; Text "vi fact.py"; Enter
      Text ":set nohls"; Enter; Text ":"; Esc
      Restart
      Start "Reverting"
      SayWhile ("If we make a bunch of changes to this file...", Compound (150, [
        Key ("/", "search", "/")
        Text "fact"
        Enter
        Change Word
        Text "factorial"
        Esc
        Pause 500
        Move SearchNext
        Dot
        Pause 500
        Move SearchNext
        Dot
        Pause 500
        Move Down
        ZoomTop
        Pause 500
        Delete BottomOfDocument
        Pause 1000
        Move TopOfDocument
        ]))
      Say "And we change our mind and want to revert everything... we could either press U a bunch of times..."
      SayWhile ("...or choose the nuclear option with colon E bang.", Text ":e!")
      Enter
      SayWhile ("And boom! We've reverted to the last saved version.", Compound (100, [Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Pause 500; Move TopOfDocument]))
      Finish ]

let scrolling = // ^e ^y zt zb zz ^f ^b ^d ^u
    [ Launch
      Pause 5000
      Setup ["# Grocery List"; ""; "## Fruits"; ""; "- Apples"; "- Bananas"; "- Citrus"; "  - Oranges"; "  - Lemons"; "- Berries"; "  - Strawberries"; "  - Blueberries"; ""; "## Vegetables"; ""; "- Leafy Greens"; "  - Spinach"; "  - Kale"; "- Root Vegetables"; "  - Carrots"; "  - Potatoes"; ""; "### Dairy"; ""; "- Milk"; "- Cheese"; "- Yogurt"; ""; "### Bakery"; ""; "- Bread"; "  - Wheat"; "  - Rye"; "- Pastries"; ""; "## Meat"; ""; "- Chicken"; "- Beef"; "- Pork"]
      SetFileType "markdown"
      Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down
      Restart
      Start "Scrolling and Jumping"
      Say "Sometimes we want to scroll the viewport without moving the cursor, and most importantly without reaching for the track pad or scroll wheel."
      SayWhile ("Control Y will scroll down, and control E will scroll up. Notice that the cursor stays in place within the document.", Compound (210, [ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollUp; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown; ScrollDown]))
      Pause 500
      Say "We can scroll to the top with Z T."
      ScrollTop
      Pause 1000
      Say "Or to the bottom with Z B."
      ScrollBottom
      Say "I often find it handy to scroll the cursor to the middle with Z Z."
      ScrollMiddle
      Pause 1000
      Say "If maintaining the cursor position isn't important..."
      SayWhile ("....then we can also jump forward by whole screens with control F", Compound (500, [JumpDown; JumpDown; JumpDown; JumpDown; JumpDown]))
      Pause 800
      SayWhile ("And jump backward with control B", Compound (500, [JumpUp; JumpUp; JumpUp; JumpUp; JumpUp]))
      Say "I find this disorienting though."
      SayWhile ("Instead I prefer to jump by half screens with control D do go down...", Compound (600, [JumpDownHalf; JumpDownHalf; JumpDownHalf; JumpDownHalf; JumpDownHalf; JumpDownHalf; JumpDownHalf; JumpDownHalf]))
      SayWhile ("...and control U to go up.", Compound (600, [JumpUpHalf; JumpUpHalf; JumpUpHalf; JumpUpHalf; JumpUpHalf; JumpUpHalf; JumpUpHalf; JumpUpHalf]))
      Finish ]

let changingCase = // ~ g~ gu gU  (combined with visual or motion)
   [ Launch
     Pause 5000
     Setup ["let add x y ="; "    x + y"; "let plus7 ="; "    add 7"; ""; "(* currying test *)"; "35 |> plus7 |>"; "printf \"Life: %i\""]
     SetFileType "ocaml"
     Move Paragraph; Move Down; Move Word
     Start "Changing Case"
     Say "We can quickly toggle the case of a character while in Normal mode, by pressing tilde."
     ToggleCase
     Say "Notice that it automatically advances the cursor."
     SayWhile ("So, we can press tilde several times and toggle the whole word.", Compound (300, [ToggleCase; ToggleCase; ToggleCase; ToggleCase; ToggleCase; ToggleCase; ToggleCase]))
     SayWhile ("But a better way...", Compound (180, [Undo; Undo; Undo; Undo; Undo; Undo; Undo; Undo]))
     Say "... is to use G followed by tilde, followed by a motion."
     SayWhile ("Such as G tilde W to toggle the word.", ToggelCaseMotion Word)
     Pause 1000
     Undo
     SayWhile ("Or another approach may be to select the word first with V E..", Compound (300, [Visual; Move WordEnd]))
     SayWhile ("...and then toggle the case with tilde.", ToggleCase)
     Say "It's the same number of key strokes."
     Pause 800
     Undo
     SayWhile ("One issue we might have is when the word is mixed case to begin with.", Compound (300, [ToggleCase; Move Left]))
     SayWhile ("Oops, toggling the case leaves the C lowercase.", ToggelCaseMotion Word)
     Undo
     SayWhile ("Instead of toggling, we can select the word again...", Compound (300, [Reselect]))
     SayWhile ("...and use G follow by Shift U for uppercase.", UpperCase)
     Pause 800
     Reselect
     SayWhile ("Or G followed by lowercase U to make it lowercase.", LowerCase)
     Finish ]

let marks = // m ' ` '' `
   [ Launch
     Text ":e animal.py"; Enter // from samples/animal
     Text ":set nowrap"; Enter
     SetFileType "python"
     Move Down; Move Down
     Start "Marks"
     Say "We're working on a little animal guessing game! We might want to come back to these animal questions..."
     SayWhile ("...so let's mark them as A for animal with M A.", Mark 'a')
     Say "Marks can be any letter."
     Compound (200, [Move Paragraph; Move Down; ZoomTop; Move Word])
     Pause 800
     SayWhile ("Let's mark this guess function with G for guess, with M G.", Mark 'g')
     SayWhile ("We can jump back to the animals with tick A.", Move (GoToMark 'a'))
     SayWhile ("And back down to the guess line with tick G.", Move (GoToMark 'g'))
     SayWhile ("If we use backtick G instead it takes us to the exact column.", Move (GoToMarkChar 'g'))
     SayWhile ("We can jump back and forth easily.", (Compound (1000, [Move (GoToMark 'a'); Move (GoToMark 'g')])))
     Pause 800
     SayWhile ("If we mark this with M Shift G, then the mark is global and works across files!", Mark 'G')
     SayWhile ("Maybe we want to leave this file...", Compound (300, [Move TopOfDocument; Move Word]))
     SayWhile ("... to look at the Node class.", GoToFile)
     Pause 500
     Say "We can go back to guess in the first file with tick Shift G."
     Move (GoToMark 'G')
     Pause 1000
     Say "Super convenient way to jump around a project!"
     Pause 30000
     Finish ]

let goToLineColumn = // #G #|
    [ Launch
      Pause 5000
      Setup ["# Grocery List"; ""; "## Fruits"; ""; "- Apples"; "- Bananas"; "- Citrus"; "  - Oranges"; "  - Lemons"; "- Berries"; "  - Strawberries"; "  - Blueberries"; ""; "## Vegetables"; ""; "- Leafy Greens"; "  - Spinach"; "  - Kale"; "- Root Vegetables"; "  - Carrots"; "  - Potatoes"; ""; "### Dairy"; ""; "- Milk"; "- Cheese"; "- Yogurt"; ""; "### Bakery"; ""; "- Bread"; "  - Wheat"; "  - Rye"; "- Pastries"; ""; "## Meat"; ""; "- Chicken"; "- Beef"; "- Pork"]
      SetFileType "markdown"
      Start "Go To Line/Column"
      Say "We can quickly jump to a particular line by entering the line number followed by shift G."
      SayWhile ("For example, line 12", Move (GoToLine 12))
      Pause 800
      SayWhile ("... or, line 18", Move (GoToLine 18))
      SayWhile ("The same can be done as a command, with colon eighteen, enter", Text ":18")
      Enter
      Say "But this is more keystrokes!"
      Pause 800
      Say "We can also go to a particular column with a number followed by pipe."
      Move (GoToColumn 7)
      Say "This makes it very easy to jump to particular points in a document."
      Finish ]

let indenting = // <{motion} >{motion} << >>  ={motion} == (
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set shiftwidth=2"; Enter
     Move Paragraph; Move Paragraph; Move Down; Move Down; Move Down; Move Down
     UnindentLine
     Move Down; IndentLine; IndentLine
     Move Down; IndentLine
     Move Down; Move Down; IndentLine
     Move TopOfDocument
     SetFileType "javascript" // not ocaml because of indenting rules
     Pause 5000
     Start "Indenting"
     SayWhile ("Looking at the list of unknown words in this Fallout solver, we notice that the indenting is crazy.", Compound (200, [Move Paragraph; Move Paragraph; Move Down; Move Down; ZoomTop]))
     SayWhile ("We can fix this by going to each line...", Compound (200, [Move Down; Move Down]))
     SayWhile ("And using double-right-angle-brackets to indent.", IndentLine)
     SayWhile ("Or double-left-angle-brackets to unindent.", Compound (200, [Move Down; UnindentLine; UnindentLine; Move Down; UnindentLine; Move Down; Move Down; UnindentLine]))
     Pause 1000
     SayWhile ("Undoing this, another way is to use double-equals to automatically adjust the indents.", Compound (150, [Undo; Undo; Undo; Undo]))
     AutoIndentLine
     Pause 500
     Compound (200, [Move Down; AutoIndentLine; Move Down; Move Down; AutoIndentLine])
     Pause 1000
     SayWhile ("Even better, we can do this in one shot with equals combined with a motion.", Compound (200, [Undo; Undo; Undo]))
     SayWhile ("Such as equals-right-curly-brace to apply to the end of the paragraph.", AutoIndent Paragraph)
     SayWhile ("Or we could have done it by first selecting in visual mode.", Compound (500, [Undo; Visual; Move Paragraph]))
     SayWhile ("And then pressing equals.", AutoIndent VisualSelection)
     Pause 500
     SayWhile ("We can also combine motions or visual selections with left and right angle brackets.", Compound (200, [Move Up; Move Up]))
     SayWhile ("Such as left-angle-bracket right-curly-brace to unindent the paragraph.", Unindent Paragraph)
     Pause 500
     SayWhile ("Or right-angle-bracket right-curly-brace to reindent it.", Indent Paragraph)
     Finish ]

let jumps = // '' ^o ^i
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set nohls"; Enter
     SetFileType "ocaml"
     Pause 5000
     Start "Jumps"
     Say "As we navigate around, a jump list is maintained."
     Key ("/", "search", "/")
     SayWhile ("Let's go to the known function.", Text "known")
     Compound (300, [Enter; Move Down; ZoomTop])
     Pause 800
     Key ("/", "search", "/")
     SayWhile ("Then to the unknown function.", Text "unknown")
     Compound (300, [Enter; Move Down; ZoomTop])
     Pause 500
     Say "These two points are now in the jump list. Only large scale jumps are included."
     SayWhile ("Moving around by words or a few lines is not a jump.", Compound (300, [Move Word; Move Word; Move Word; Move BackWord; Move BackWord; Move BackWord; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move Up; Move Up]))
     Say "We can quickly pop back to the line from which we came with double-tick or to the exact character with double-backtick."
     Move JumpBackChar
     Say "And return with double-tick or double-backtick again."
     Move JumpBack
     Pause 800
     SayWhile ("Bouncing between these two points all we like.", Compound (400, [Move JumpBack; Move JumpBack; Move JumpBack; Move JumpBack; Move JumpBack; Move JumpBack]))
     Say "Let's continue jumping around. Maybe to the bottom of the code."
     Move BottomOfDocument
     Say "We can retrace our steps with control-O."
     SayWhile ("Back to unknown.", Move JumpPrevious)
     SayWhile ("Back to known.", Move JumpPrevious)
     SayWhile ("And back to the start.", Move JumpPrevious)
     Say "We can traverse forward again with control-I."
     SayWhile ("To known again.", Move JumpNext)
     SayWhile ("To unknown.", Move JumpNext)
     SayWhile ("And to the end.", Move JumpNext)
     Finish ]

let deleteChar = // x X
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set nohls"; Enter
     SetFileType "ocaml"
     Pause 5000
     Start "Delete Character"
     SayWhile ("We can delete the character under the cursor with X.", Compound (200, [Move StartOfNextLine; Move Right]))
     DeleteChar
     Pause 500
     Compound (200, [DeleteChar; DeleteChar; DeleteChar; DeleteChar; DeleteChar; DeleteChar; DeleteChar])
     SayWhile ("And we can delete the character before the cursor with shift-X.", Move WordEnd)
     Compound (200, [DeletePrevChar; DeletePrevChar])
     Say "Pretty simple!"
     Finish ]

let undo = // u U ^r
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set nohls"; Enter
     SetFileType "ocaml"
     Pause 5000
     Start "Undo"
     SayWhile ("Let's make a few changes to this code.", Compound (300, [Move Down; Move Down; Move Down; Move Down; Move Down]))
     SayWhile ("Maybe delete a couple of lines", Compound (300, [DeleteLine; DeleteLine]))
     Pause 500
     SayWhile ("And change this string.", Compound (150, [Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move StartOfPreviousLine; Move Right]))
     Pause 500
     SayWhile ("Deleting the word Fallout.", Delete Word)
     Pause 500
     SayWhile ("And removing the newline.", Compound (300, [Move EndOfLine; DeletePrevChar; DeletePrevChar]))
     Pause 500
     Say "Now we can undo all the changes to this line with shift-U."
     UndoLine
     Pause 1000
     SayWhile ("Or we can undo just some of the changes with U.", Compound (400, [Undo; Undo; Undo]))
     Pause 500
     SayWhile ("Or continue pressing U to undo more.", Compound (400, [Undo; Undo; Undo]))
     Pause 500
     SayWhile ("Finally, we can redo these changes with Control-R.", Compound (400, [Redo; Redo; Redo; Redo; Redo]))
     Finish ]

let visual = // v V ^v
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set nohls"; Enter
     Key ("/", "search", "/")
     Text "PILE"
     Enter
     SetFileType "ocaml"
     Pause 5000
     Start "Visual Modes"
     Say "To select text, we can enter visual mode with V."
     Visual
     SayWhile ("Then as we move around, a selection is made from where we started to the cursor.", Compound (400, [Move Up; Move Up; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move WordEnd; Move WordEnd; Move Left; Move Left; Move Left; Move Left]))
     Pause 1000
     SayWhile ("To select by whole lines, we can use shift-V.", VisualLine)
     SayWhile ("And entire lines are selected as we move.", Compound (400, [Move Up; Move Up; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up]))
     Pause 1000
     Say "Pressing escape returns to Normal mode."
     Esc
     Pause 500
     SayWhile ("We can also select arbitrary blocks of text with control-V.", VisualBlock)
     SayWhile ("In visual block mode we can select columns of text.", Compound (400, [Move Down; Move Down]))
     Say "Some terminals intercept control-V. You may use control-Q instead."
     SayWhile ("Any rectangular areas can be selected.", Compound (400, [Move Left; Move Left; Move Left]))
     Pause 500
     Say "Operations can then be performed on selected text, such as deleting with X."
     DeleteWithX VisualSelection
     Finish ]

let visualAdvanced = // o gv '< '>
    [Launch
     Text ":e fallout.fs"; Enter // from samples/fallout
     Text ":set nowrap"; Enter
     Text ":set nohls"; Enter
     Key ("/", "search", "/")
     Text "PILE"
     Enter
     SetFileType "ocaml"
     Pause 5000
     Start "Advanced Selection"
     SayWhile ("Notice that, in visual mode, we still have a cursor in addition to the selection.", Compound (400, [Visual; Move Right; Move Right; Move Right]))
     SayWhile ("We can move the cursor between the ends of the selection with O.", Compound (400, [VisualCursorPosition; VisualCursorPosition; VisualCursorPosition; VisualCursorPosition; VisualCursorPosition; VisualCursorPosition; VisualCursorPosition]))
     SayWhile ("We can extend the selection to the left.", Move Left)
     SayWhile ("And we can then toggle the cursor to the other end...", VisualCursorPosition)
     SayWhile ("...And extend to the right.", Move Right)
     Pause 1000
     SayWhile ("Once back in Normal mode...", Esc)
     SayWhile ("We can get our previous selection back with G follow by V.", Reselect)
     Pause 500
     SayWhile ("Another trick back in Normal mode.", Esc)
     Say "Is that we can jump to the start of the previous selection with backtick left-angle-bracket."
     JumpSelectionStart
     Pause 1000
     Say "Or we can jump to the end of the previous selection with backtick right-angle-bracket."
     JumpSelectionEnd
     Say "Left and right angle brackets are special marks."
     SayWhile ("You may have noticed that when you have a selection.", Reselect)
     SayWhile ("Entering a command with colon, automatically uses the selection as a range between the angle bracket marks", Text ":")
     Finish ]

let replace = // r R
    [Launch
     Setup ["# ----------------"; ""; ""; "def fact(n):"; "  if n != 0: return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
     Pause 5000
     SetFileType "python"
     Text ":set shiftwidth=2"; Enter
     Pause 300
     Text ":set nowrap"; Enter
     Pause 300
     Move Down; Move Down; Move Down; Move Down
     SetFileType "python"
     Start "Replace"
     Say "Ah, there's a bug! That's supposed to be equals rather than not-equals."
     SayWhile ("We can go to the bang.", Move (Find '!'))
     Say "And replace it by pressing R, for replace, followed by equals."
     Replace '='
     Pause 500
     Say "We can move the return statement to the next line this way too..."
     SayWhile ("Go to the space before it.", Move (Till 'r'))
     Say "Then press R followed by Enter to replace it with a carriage return."
     Key ("r⏎", "replace with '⏎'", "r~")
     Pause 500
     Say "There's also a Replace mode that allows for continual over typing."
     SayWhile ("To illustrate Replace Mode, let's add a header comment.", Compound (200, [Move TopOfDocument; Move Word]))
     SayWhile ("To add a label..", Compound (200, [Move Right; Move Right]))
     SayWhile ("We can press shift-R to enter replace mode", ReplaceMode)
     SayWhile ("And type over some of the dashes without disturbing the rest of the line.", Compound (120, [Text " "; Text "F"; Text "A"; Text "C"; Text "T"; Text "O"; Text "R"; Text "I"; Text "A"; Text "L"; Text " "]))
     Say "Then Escape back to Normal mode."
     Esc
     Pause 1000
     Finish ]

let delete = // dd d D vd
    [Launch
     Setup [""; ""; ""; "def fact(n):"; "  if n != 0: return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
     Pause 5000
     SetFileType "python"
     Text ":set shiftwidth=2"; Enter
     Pause 300
     Text ":set nowrap"; Enter
     Pause 300
     Move Down; Move Down; Move Down; Move Down
     SetFileType "python"
     Start "Delete"
     Say "We can delete a line by pressing D D."
     DeleteLine
     Pause 1000
     SayWhile ("Or delete to the end of a line with shift-D.", Compound (200, [Move Word; Move Right]))
     Delete EndOfLine
     Pause 1000
     SayWhile ("We can combine delete with any motion or text object. For example delete word with D W.", Compound (200, [Move Down; Move Down; Move StartOfLine]))
     Delete Word
     Pause 1000
     SayWhile ("Or delete around parenthesis with D A parenthesis.", Move (Find '7'))
     Delete (Span AroundBlock)
     Pause 1000
     Delete (Span AroundBlock)
     SayWhile ("We can also first visually select things...", Compound (200, [Move BackParagraph; Move Down; Visual; Move WordEnd; Move WordEnd]))
     Say "And delete them with D."
     Delete VisualSelection
     Pause 2000
     VisualLine; Pause 200; Move Down
     Pause 500
     Delete VisualSelection
     Pause 1000
     Finish ]

let put = // p P (line behavior)
    [Launch
     Setup [""; ""; ""; "def fact(n):"; "  return n*fact(n-1)"; "  if n =! 0: return 1"; ""; "fact(print(7))"]
     Pause 5000
     SetFileType "python"
     Text ":set shiftwidth=2"; Enter
     Pause 300
     Text ":set nowrap"; Enter
     Pause 300
     Move Down; Move Down; Move Down; Move Down; Move Down; Move (Find '=')
     SetFileType "python"
     Start "Put"
     Say "When we delete a character with X..."
     DeleteChar
     Say "It's stored in a register similar to the clipboard in other editors."
     Say "We can put it back after the cursor with P."
     Put
     Say "In fact, we can think of X followed by P as a swap characters operator."
     SayWhile ("If instead we delete the bang...", Compound (200, [Undo; Undo; Move Right]))
     DeleteChar
     Pause 1000
     Say "Then we can put it to the left of the cursor with Shift-P.";
     Move Left; Pause 300; PutBefore
     Pause 1000
     SayWhile ("The same works with any spans of deleted text.", Compound (200, [Move Down; Move Down; Move BackWord]))
     SayWhile ("Deleting a word with D W.", Delete Word)
     SayWhile ("And putting it before the cursor with Shift-P", Compound (300, [Move StartOfLine; PutBefore]))
     SayWhile ("Or again deleting a word with D W.", Compound (200, [Move Right; Delete Word]))
     SayWhile ("And putting it after the cursor with P.", Put)
     Pause 1000
     SayWhile ("When we delete whole lines with D D...", Compound (200, [Move Up; Move Up; Move Up]))
     DeleteLine
     Say "The put behavior then works with lines."
     SayWhile ("Shift-P puts it back before the line the cursor is on.", PutBefore);
     Pause 1000
     SayWhile ("Or instead...", Compound (200, [DeleteLine; Move Word]))
     SayWhile ("P puts below the current line.", Put)
     Pause 1000
     Finish ]

let yank = // y yy Y vy  :map Y y$
    [Launch
     Setup [""; ""; ""; "def fact(n):"; "  if n != 0: return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
     Pause 5000
     SetFileType "python"
     Text ":set shiftwidth=2"; Enter
     Pause 300
     Text ":set nowrap"; Enter
     Pause 300
     Move Down; Move Down; Move Down; Move Down
     SetFileType "python"
     Start "Yank"
     Say "What other editors call copying, we call yanking. We can yank a line with Y Y or Shift-Y."
     YankLine
     Pause 1000
     SayWhile ("Notice that Shift-Y yanks the whole line, unlike Shift-D which deletes from the cursor to the end of the line.", Compound (200, [Move Word; Move Right; Yank EndOfLine]))
     Pause 1000
     SayWhile ("Personally, I find this inconsistent behavior, so I map Shift-Y to Y dollar.", Text ":map Y y$")
     Pause 1000
     SayWhile ("We can combine yanking with any motion or text object. For example yank a word with Y W.", Compound (200, [Esc; Move Down; Move Down; Move Down; Move StartOfLine; Yank Word]))
     Pause 1000
     SayWhile ("Or yank around parenthesis with Y A parenthesis.", Compound (200, [Move (Find '7'); Yank (Span AroundBlock)]))
     Pause 1000
     SayWhile ("We can also first visually select things...", Compound (200, [Move BackParagraph; Move Down; Visual; Move WordEnd; Move WordEnd]))
     Say "And yank them with Y."
     Yank VisualSelection
     Pause 1000
     Finish ]

let patterns = // xp deep ddp ddP yyp
    [Launch
     Setup ["# Teh Grocery List"; ""; "## Fruits"; ""; "- Apples"; "- Bananas"; "- Citrus"; "  - Oranges"; "  - Lemons"; "- Berries"; "  - Strawberries"; "  - Blueberries"; ""; "## Vegetables"; ""; "- Leafy Greens"; "  - Spinach"; "  - Kale"; "- Root Vegetables"; "  - Carrots"; "  - Potatoes"; ""; "### Dairy"; ""; "- Milk"; "- Cheese"; "- Yogurt"; ""; "### Bakery"; ""; "- Bread"; "  - Wheat"; "  - Rye"; "- Pastries"; ""; "## Meat"; ""; "- Chicken"; "- Beef"; "- Pork"]
     Pause 5000
     Text ":set shiftwidth=2"; Enter
     Pause 300
     Text ":set nowrap"; Enter
     Pause 300
     SetFileType "markdown"
     Start "Patterns"
     SayWhile ("Some patterns of usage with delete, yank and put are very common.", Move (Find 'e'))
     Say "For example, swapping characters with X P."
     Compound (500, [DeleteChar; Put])
     Pause 1000
     Move Right
     SayWhile ("Or swap words with D E E P.", Compound (800, [Delete WordEnd; Move WordEnd; Put]))
     Pause 1000
     SayWhile ("Another is to swap lines with D D P or Shift-D P.", Compound (200, [Move Paragraph; Move Paragraph; Move Down]))
     Compound (500, [DeleteLine; Put; DeleteLine; Put])
     Pause 1000
     SayWhile ("Or duplicate a line with Y Y P.", Compound (500, [YankLine; Put]))
     Say "So common that they can be thought of as operators of their own."
     Pause 1000
     Finish ]

let htmlSample = ["<html>"; "  <head>"; "    <title>Demo</title>"; "  </head>"; "  <body class=\"foo\">"; "    <h1>Demo</h1>"; "  </body>"; "  <script>"; "  function load() {"; "    foo[12] = \"bar\";"; "    alert('loaded');"; "  }"; "  </script>"; "</html>"; "<!--"; "We call ``load()``"; "upon document load."; "This is a sentence."; "And so is this."; "-->"]

let textObjects1 = // i/a " ' `
    [Launch
     Setup htmlSample
     Pause 5000
     Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up
     Text ":set nowrap"; Enter
     SetFileType "html"
     Start "Text Objects 1"
     Say "In addition to motions, we can use text objects to describe spans of text. For example inner quotes with I-quote."
     Visual; Move (Span InnerQuotes)
     Say "Notice that it moves to the first quote on the line and selects within."
     Pause 1000
     Say "Or we can include the quotes and white space by pressing A-quote."
     Move (Span AroundQuotes)
     Pause 1200
     SayWhile ("This also works with single quotes...", Compound (200, [Esc; Move Down; Move BackWord; Move BackWord]))
     SayWhile ("By pressing I-tick", Compound (200, [Visual; Move (Span InnerTicks)]))
     Pause 1000
     Say "Or again including the single quotes by pressing A-tick."
     Move (Span AroundTicks)
     Pause 1000
     Say "Besides visual selection, these text objects may be combined with operators that take motions. For example, delete inner single-quotes with D-I-Tick."
     Esc; Pause 200; Delete (Span InnerTicks)
     Pause 1300
     SayWhile ("Another kind of quote-like character, common in markdown, is the back-tick.", Compound (200, [Move Down; Move Down; Move Down; Move Down; Move Down; Pause 300]))
     SayWhile ("Inner back ticks and around back ticks work as well.", Compound (200, [Visual; Move (Span InnerBackticks)]))
     Pause 1000
     Move (Span AroundBackticks)
     Pause 1000
     Finish ]

let textObjects2 = // i/a <> [] ()b {}B
    [Launch
     Setup htmlSample
     Pause 5000
     Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move (Find '1')
     Text ":set nowrap"; Enter
     SetFileType "html"
     Start "Text Objects 2"
     SayWhile ("We can select inner square brackets with V-I-Square-bracket.", Compound (400, [Visual; Move (Span InnerBrackets)]))
     Say "Either left or right square bracket works."
     SayWhile ("Or around the brackets by pressing A-Square-bracket", Move (Span AroundBrackets))
     Pause 500
     Esc; Pause 200; Move Down
     SayWhile ("The same works for inner parenthesis with I-Parenthesis.", Compound (400, [Visual; Move (Span InnerBlock)]))
     Say "Again, either left or right parenthesis works and also B for block works, as in I-B for inner block."
     SayWhile ("And press A-parenthesis for around.", Move (Span AroundBlock))
     Pause 500
     Say "We can expand to inner curly brace with I-Curly-brace."
     Move (Span InnerBigBlock)
     Pause 500
     VisualCursorPosition
     Say "Or including the braces by pressing A-Curly-brace."
     Move (Span AroundBigBlock)
     Say "Shift-B works as well, as in I or A followed by Shift-B."
     Pause 800
     Esc; Pause 200
     Say "Combine these with operators such as D A-Curly-brace to delete the block."
     Delete (Span AroundBigBlock)
     Pause 1000
     Compound (200, [VisualCursorPosition; Esc; Move Up; Move BackWord; Visual])
     SayWhile ("Finally, inner angle brackets with I followed by left or right Angle-bracket", Move (Span InnerAngleBrackets))
     Pause 500
     SayWhile ("Or around by pressing A-angle-bracket.", Move (Span AroundAngleBrackets))
     Pause 1000
     Finish]

let textObjects3 = // i/a w W p s
    [Launch
     Setup htmlSample
     Pause 5000
     Move BottomOfDocument; Move Up; Move Up; ZoomBottom; Move Up; Move Up; Move Word; Move Word; Move Right; Move Right; Move Right
     Text ":set nowrap"; Enter
     SetFileType "html"
     Start "Text Objects 3"
     Say "To select a word from anywhere within it, we can press I-W for inner word."
     Visual; Pause 200; Move (Span InnerWord)
     Pause 800
     Say "Or we can specify big words with I-Shift-W"
     Esc; Pause 200; Visual; Pause 200; Move (Span InnerBigWord)
     Pause 800
     SayWhile ("To include surrounding white space we can press A-W or A-Shift-W.", Compound (200, [Esc; Move Down]))
     Visual; Pause 200; Move (Span AroundWord)
     Pause 1000
     Say "We can select sentences with I or A followed by S."
     Esc; Pause 200; Move Down; Visual; Pause 200; Move (Span InnerSentence)
     Pause 1000
     Say "Or paragraphs with I or A followed by P."
     Esc; Pause 200; Visual; Pause 200; Move (Span InnerParagraph)
     Pause 1000
     Finish ]

let textObjects4 = // i/a t
    [Launch
     Setup htmlSample
     Pause 5000
     Move Down; Move Down; Move Down; Move Down; Move Down
     Text ":set nowrap"; Enter
     SetFileType "html"
     Start "Text Objects 4"
     Say "We can select within HTML or XML tags with I-T, for inner tag."
     Visual; Pause 200; Move (Span InnerTag)
     Pause 1000
     Say "Or around them by pressing A-T, for around tag."
     Move (Span AroundTag)
     Pause 1000
     Say "Notice that this is different to angle bracket text objects."
     VisualCursorPosition; Esc; Pause 200; Move Right; Visual; Pause 200; Move (Span InnerAngleBrackets)
     Pause 1200
     Move (Span AroundAngleBrackets)
     Pause 500
     Say "It includes attributes and child elements and text."
     Esc; Pause 200; Move Up; Visual; Pause 200; Move (Span AroundTag)
     Pause 1000
     Finish ]

let rpn = ["open System"; ""; "let execute ="; "  Seq.fold (|>)"; ""; "let bin f = function"; "  | _::a::b::t ->"; "    f b a :: t"; ""; "let add = bin ( + )"; "let sub = bin ( - )"; "let mul = bin ( * )"; "let div = bin ( / )"; ""; "let dig v = function"; "  | x :: t ->"; "    10 * x + v :: t"; ""; "let ent s = 0 :: s"; ""; "let inst ="; "  Map.ofList ["; "    '0', dig 0"; "    '1', dig 1"; "    '2', dig 2"; "    '3', dig 3"; "    '4', dig 4"; "    '5', dig 5"; "    '6', dig 6"; "    '7', dig 7"; "    '8', dig 8"; "    '9', dig 9"; "    '+', add"; "    '-', sub"; "    '*', mul"; "    '/', div"; "    ' ', ent]"; ""; "let flip f a b ="; "  f b a"; ""; "let compile ="; "  flip Map.find inst"; "  |> Seq.map"; ""; "let eval ="; "  compile >>"; "  execute [0] >>"; "  Seq.head"; ""; "let rec repl () ="; "  Console.ReadLine()"; "  |> eval"; "  |> printf \"%i\\n>\""; "  |> repl"; ""; "printf \"TinyRPN\n>\""; "repl ()"]

let insert = // i a I A
    [Launch
     Setup rpn
     Pause 5000
     Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up 
     Delete Word; Delete Word; Delete Word; Move Right; Delete EndOfLine
     Pause 2000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Insert"
     Say "Normal mode is home. It's wonderful to have the entire keyboard at our disposal for commands. But sometimes we need to insert text by pressing I."
     Insert
     Say "This begins inserting before the cursor and we can type what we need."
     Compound (100, [Text "e"; Text "n"; Text "t"; Text " "; Text "s"; Text " "])
     SayWhile ("Pressing Escape returns to Normal mode.", Esc)
     Pause 1000
     SayWhile ("We can also insert after the cursor by pressing A.", Move Right)
     After
     Pause 1000
     SayWhile ("And type what we need; again pressing Escape when we're done.", Compound (100, [Text " "; Text "0"]))
     Esc
     Say "We can insert before the line, at the first non-whitespace, by pressing Shift-I."
     InsertBefore
     Pause 1000
     Compound (100, [Text "l"; Text "e"; Text "t"; Text " "])
     Say "Then Escape to Normal mode as usual."
     Esc
     Say "Finally, we can insert after the line with Shift-A"
     AfterLine
     Pause 1000
     Compound (100, [Text " "; Text ":"; Text ":"; Text " "; Text "s"])
     SayWhile ("And always escaping back to Normal mode as our home mode.", Esc)
     Pause 1000
     Finish ]

let insertAdvanced = // gI gi
    [Launch
     Setup rpn
     Pause 5000
     Move Paragraph; Move Paragraph; Move Paragraph; Move Up; Move EndOfLine; Move BackWord
     Pause 2000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Advanced Insert"
     Say "When we insert at the start of a line by pressing Shift-I, it starts before the first non-whitespace."
     InsertBefore
     Pause 1000
     SayWhile ("If instead we want to insert at the first column we can press G followed by Shift-I.", Esc)
     InsertFirstColumn
     Pause 2000
     SayWhile ("Of course we're now in insert mode and can type what we need.", Compound (100, [Text "/"; Text "/"]))
     Pause 800
     Esc
     Pause 200
     SayWhile ("Now, let's say we explore the code a bit; moving down to the bottom. We can return to inserting where we left off by pressing G followed by I.", Compound (150, [Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph; Move Paragraph]))
     InsertAtLast
     Pause 2000
     Compound (100, [Text " "; Text "f"; Text "o"; Text "o"; Esc])
     Pause 1000
     Finish ]

let openLine = // o O
    [Launch
     Setup rpn
     Pause 5000
     Move Paragraph; Move Paragraph; Move Paragraph
     DeleteLine; Move Down; DeleteLine
     ScrollUp; ScrollUp; Move Up
     Pause 2000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Open Line"
     Say "We can open a line below the cursor by pressing O."
     OpenBelow
     Say "This also takes us to insert mode and we can now type a line of code."
     Compound (100, [Text "l"; Text "e"; Text "t"; Text " "; Text "s"; Text "u"; Text "b"; Text " "; Text "="; Text " "; Text "b"; Text "i"; Text "n"; Text " "; Key ("⌨", "", "{(}"); Text " "; Text "-"; Text " "; Key ("⌨", "", "{)}")])
     Say "As usual, we press Escape to return to Normal mode."
     Esc
     Pause 1000
     SayWhile ("We can open a line above the cursor with Shift-O.", Move Up)
     OpenAbove
     Pause 1000
     Say "Again, we're now in insert mode an can type a comment."
     Compound (100, [Text "/"; Text "/"; Text " "; Text "b"; Text "i"; Text "n"; Text "a"; Text "r"; Text "y"; Text " "; Text "o"; Text "p"; Text "s"])
     Say "Escape to Normal mode."
     Esc
     Pause 1000
     SayWhile ("And maybe open another line above for extra space with Shift-O again.", OpenAbove)
     Esc; Pause 200; Delete BackWord; DeleteChar
     Pause 1000
     Finish ]

let change = // cc C c
    [Launch
     Setup (["";""] @ rpn)
     Pause 6000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Change"
     SayWhile ("It's very common to delete something and immediately insert something in its place. For that we can use Change commands.", Compound (100, [Move Down; Move Down; Move Down; Move Down; Move Word]))
     SayWhile ("Pressing C C, changes the whole line; deleting it an leaving us in Insert mode.", ChangeLine)
     Compound (100, [Text "l"; Text "e"; Text "t"; Text " "; Text "e"; Text "x"; Text "e"; Text "c"; Text " "; Text "="; Esc])
     Pause 300
     Move BackWord
     Pause 1000
     Say "Rather than retype the whole thing, we could change to the end of the line with Shift-C"
     ChangeToEnd
     Pause 1500
     Compound (100, [Text "r"; Text "u"; Text "n"; Text " "; Text "="; Esc])
     Pause 300
     Move BackWord
     Say "Better yet, we can used C combined with a motion to, for example, change a word with C W."
     Change Word
     Pause 1500
     Compound (100, [Text "g"; Text "o"; Esc])
     Pause 1000
     SayWhile ("Or we can use C combined with a text object such as C A B to change around a block.", Compound (100, [Move Down; Move (Find '|')]))
     Change (Span AroundBlock)
     Pause 1500
     Compound (100, [Text "f"; Text "o"; Text "o"; Esc])
     Pause 1000
     Finish ]

let substitute = // S s
    [Launch
     Setup (["";""] @ rpn)
     Pause 6000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Substitute"
     SayWhile ("Substituting is very similar to changing.", Compound (100, [Move Down; Move Down; Move Down; Move Down; Move Word]))
     SayWhile ("In fact Shift-S to substitute a line is a synonym for C C to change a line.", SubstituteLine)
     Compound (100, [Text "l"; Text "e"; Text "t"; Text " "; Text "g"; Text "o"; Text " "; Text "="; Esc])
     Pause 300
     Move BackWord
     Say "Pressing lowercase S substitutes a single character; deleting it an leaving us in Insert mode."
     Substitute
     Say "I find it useful when prepending to a camel cased name."
     Compound (100, [Text "a"; Text "p"; Text "p"; Text "l"; Text "y"; Text "A"; Text "n"; Text "d"; Text "G"; Esc])
     Pause 1000
     Finish ]

let jumpPercent = // {count}%
    [ Launch
      Pause 5000
      Setup ["# Grocery List"; ""; "## Fruits"; ""; "- Apples"; "- Bananas"; "- Citrus"; "  - Oranges"; "  - Lemons"; "- Berries"; "  - Strawberries"; "  - Blueberries"; ""; "## Vegetables"; ""; "- Leafy Greens"; "  - Spinach"; "  - Kale"; "- Root Vegetables"; "  - Carrots"; "  - Potatoes"; ""; "### Dairy"; ""; "- Milk"; "- Cheese"; "- Yogurt"; ""; "### Bakery"; ""; "- Bread"; "  - Wheat"; "  - Rye"; "- Pastries"; ""; "## Meat"; ""; "- Chicken"; "- Beef"; "- Pork"]
      SetFileType "markdown"
      Start "Jump Percent"
      Say "Normally, pressing percent jumps between matching braces and brackets."
      Say "But a number followed by percent has completely different behavior."
      Say "Instead, it jumps to a percentage of the document length."
      SayWhile ("For example, 50 percent jumps to the middle.", Move (PercentageOfDocument 50))
      SayWhile ("Or 10 percent jumps to near the top.", Move (PercentageOfDocument 10))
      SayWhile ("Or 90 percent jumps to near the bottom.", Move (PercentageOfDocument 90))
      SayWhile ("Of course 100 percent or more jumps to the bottom and is equivalent to Shift-G.", Move (PercentageOfDocument 100))
      Move BottomOfDocument
      Pause 1000
      Finish ]

let countedMotions = // #h #j #k #l #w #b #e #ge #W #B #E #gE #) #( #} #{
    [ Launch
      Setup [""; ""; "def fact(n):"; "  if n == 0:"; "    return 1"; "  return n*fact(n-1)"; ""; "print(fact(7))"]
      Pause 5000
      Move Down; Move Down
      Text ":set nohls"; Enter; Text ":"; Esc
      Pause 1000
      SetFileType "python"
      Start "Counted Motions"
      Say "All of the motions can be preceeded by a count. For example, 5 L to move right five."
      Move (RightNum 5)
      Pause 500
      Say "Or down five with 5 J."
      Move (DownNum 5)
      Pause 500
      Say "5 H, left."
      Move (LeftNum 5)
      Pause 500
      Say "5 K, up."
      Move (UpNum 5)
      Pause 500
      Say "We can move two words with 2 W."
      Move (WordNum 2)
      Pause 500
      Say "Or back two words with 2 B."
      Move (BackWordNum 2)
      Pause 500
      Say "This works with any motion. Searching is also a motion. Three slash to find the 3rd match.."
      Key ("3/", "search 3rd", "3/")
      Pause 500
      Type (50, "fac")
      Pause 500
      Enter
      Pause 500
      Move (UpNum 2)
      Say "Or 3 F N to find the 3rd N on the line."
      Move (FindNum (3, 'n'))
      Pause 500
      Say "This is just a sample of the motions that accept a count."
      Finish]

let numberedLines = // :set nu  :set rnu  #G  #j  #k
    [Launch
     Setup rpn
     Pause 6000
     Text ":set nowrap"; Enter
     SetFileType "javascript"
     Start "Numbered Lines"
     SayWhile ("Set number turns on line numbering.", Type (60, ":set number"))
     SayWhile ("Or N U for short.", Type (60, "\b\b\b\b"))
     Enter
     Say "A count followed by G jumps to a line."
     SayWhile ("6 G.", Move (GoToLine 6))
     Say "Pressing colon number works too."
     SayWhile ("Colon-51 enter.", Type (60, ":51"))
     Enter
     Say "But using G saves a key stroke."
     SayWhile ("57 G.", Move (GoToLine 57))
     Say "Now back to the top."
     Move TopOfDocument
     SayWhile ("Set N U bang toggles numbering.", Type (60, ":set nu!"))
     SayWhile ("Or No N U to turn off.", Type (60, "\b\b\bnonu"))
     Enter
     SayWhile ("Set relative number shows numbers relative to the cursor.", Type (60, ":set relativenumber"))
     SayWhile ("Or R N U for short.", Type (20, "\b\b\b\b\b\b\b\b\b\b\b\b\bnu"))
     Enter
     SayWhile ("We can see this as we move.", Compound (150, [Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up]))
     SayWhile ("Turning on absolute numbering...", Type (60, ":set nu"))
     Enter
     SayWhile ("...shows the absolute cursor line.", Compound (150, [Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Down; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up; Move Up]))
     Say "A count followed by K or J moves relative amounts."
     SayWhile ("2 J.", Move (DownNum 2))
     SayWhile ("3 J.", Move (DownNum 3))
     SayWhile ("5 K.", Move (UpNum 5))
     SayWhile ("50 J.", Move (DownNum 50))
     Pause 1000
     Finish ]

let countedInsert = // {count}i/a/I/A/o/O
    [ Launch
      Pause 5000
      SetFileType "text"
      Start "Counted Insert"
      Say "Entering a number before an insert command causes the insert to be repeated."
      SayWhile ("For example, 4 I", CountedInsert 4)
      SayWhile ("And then typing hi space.", Type (50, "hi "))
      SayWhile ("Causes hi to be repeated four times once we press escape.", Esc)
      Pause 800
      SayWhile ("It works for inserting before a line with 4 Shift-I.", CountedInsertBefore 4)
      SayWhile ("Typing a single dash.", Text "-")
      SayWhile ("Inserts four dashes.", Esc)
      Pause 800
      SayWhile ("Or 4 Shift-A inserts after the line.", CountedAfterLine 4)
      SayWhile ("One dash.", Text "-")
      SayWhile ("Makes four.", Esc)
      Pause 800
      Move BackWordEnd
      Say "Oddly enough, it works to repeat backspaces."
      SayWhile ("3 A", CountedAfter 3)
      SayWhile ("Followed by deleting one Hi.", Type (50, "\b\b\b"))
      SayWhile ("Deletes three of them.", Esc)
      Pause 800
      Say "It works with opening lines."
      SayWhile ("3 O", CountedOpenBelow 3)
      SayWhile ("Enter a line of text.", Type (50, "repeat"))
      SayWhile ("Repeats the line.", Esc)
      Pause 800
      SayWhile ("Or 3 Shift-O.", CountedOpenAbove 3)
      SayWhile ("Repeats above.", Type (50, "above"))
      Esc
      Pause 1000
      Finish ]

let verticalInsert = // visual block (^V/^Q) I/A (including ragged edge)
    [ Launch
      Pause 5000
      Setup ["Apples"; "Bananas"; "Oranges"; "Lemons"; "Strawberries"; "Blueberries"]
      SetFileType "markdown"
      Start "Vertical Insert"
      Say "Multi-line inserts are possible by first selecting blocks."
      SayWhile ("Press Control-V or Control-Q to enter visual block mode.", VisualBlock)
      SayWhile ("Then select a column.", Move (DownNum 6))
      SayWhile ("And press Shift-I to insert before each line.", InsertBefore)
      SayWhile ("It may appear that we're inserting on a single line.", Type (50, "- "))
      SayWhile ("But pressing Escape then applies our insert to all of them.", Esc)
      Pause 1000
      Move Word
      SayWhile ("The column may be anywhere in the lines.", Compound (100, [VisualBlock; Move (DownNum 6)]))
      SayWhile ("Let's make these bold.", InsertBefore)
      Type (50, "**")
      Esc
      Pause 1000
      SayWhile ("You may find it surprising that...", Reselect)
      SayWhile ("...if we extend the selection to the end of the lines with dollar.", Move EndOfLine)
      SayWhile ("We can insert after each line with Shift-A", AfterLine)
      Pause 200
      Type (50, "**")
      Pause 800
      Esc
      Pause 1000
      Finish]

let insertModeDelete = // <BS> ^h ^w ^u
    [ Launch
      Pause 5000
      SetFileType "text"
      Start "Delete in Insert Mode"
      Insert
      SayWhile ("When typing in insert mode, we can press backspace of course to correct mistakes.", Type (30, "\n\n\n\nWhen typing\nin insert moed"))
      Pause 800
      Backspace
      Say "Or we can press Control-H to do the same thing."
      BackspaceCtrlH
      Pause 1200
      Type (50, "de")
      Say "We can also delete whole words with Control-W without leaving Insert mode."
      DeleteWordCtrlW
      Say "Or delete to the start of the line with Control-U."
      DeleteLineCtrlU
      Pause 1000
      Finish ]

//  Basic Motions 1  h j k l ␣ ⌫
//  Basic Motions 2  w b e ge
//  Basic Motions 3  W B E gE
//  Basic Motions 4  $ ^ 0
//  Basic Motions 5  H L M gg G
//  Basic Motions 6  ) ( } {
//  Basic Motions 7  ]] [[ ][ []
//  Basic Motions 8  + - <CR>
//  Matching  %
//  Underscore  _  (Just like carrot except with count)
//  Find  f F t T ; ,
//  Search  * # n N / ?  /<cr>  ?<cr>
//  Join  J gJ
//  Quitting   :q :q! ZQ  :wq :x ZZ  ^z  fg
//  Reverting  :e!
//  Scrolling  ^e ^y zt zb zz  ^d ^u ^f ^b
//  Case  ~ g~ gu gU  (combined with visual or motion)
//  Go to line/column #G #|
//  Mark  m ' ` '' ``
//  Indenting  <{motion} >{motion} << >>  ={motion} == (:set shiftwidth not covered)
//  Jumps ^o ^i etc.
//  Delete char  x X
//  Undo  u U ^r
//  Visual  v V ^v
//  Advanced visual  o gv '< '>  (bad habit possibly)
//  Replace r R  (replace with <CR> to break lines -- removes trailing space)
//  Delete  d dd D vd
//  Put  p P  (line behavior)
//  Yank  y yy Y vy  :map Y y$
//  Patterns ddp Dp yyp Yp xp dwwP etc.
//  Text Objects 1  i/a " ' `
//  Text Objects 2  i/a <> [] ()b {}B
//  Text Objects 3  i/a w W p s
//  Text Objects 4  i/a t
//  Insert  i a I A
//  Advanced Insert  gi gI
//  Open Line  o O
//  Change  cc C c
//  Substitute  s S
//  Numbered Lines  :set nu  :set rnu  :set nu! #j  #k
//  Jump Percent  {count}%
//  Counted Insert  #i #a #I #A #o #O
//  Vertical Inserts (including ragged edge)

//  Insert mode  ^h  ^w  ^u

//  Counted High/Low  #H #L
//  Counted Text Objects  3ya(

//  Insert mode single normal command
//  Line Wrap  :set nowrap  :set number  gh gj gk gl g$ g^ (display vs. real lines)
//  Horizontal scroll zL zH
//  Auto indent  [p [P ]p ]P
//  Scroll plus first column z<CR> z. z-
//  Dot  .  #.
//  Macros  q @ @@
//  Indenting in Insert  ^t ^d
//  Commands  :
//  Registers  "
//  Leader  \
//  Search & Replace  :s/foo/bar & :%s/foo/bar  also n.n. trick
//  Advanced 1  !
//  Advanced 3  K
//  Advanced 4  Q
//  Pattern * cw foo <esc> n . n . n .
//  Surround?
//  :noremap ^ _  :nmap _ i <esc>
//  Unexpected motions: f{char} /foo
//  Interacting with the shell:  :w !{cmd}  :r !{cmd}  !  !!  ^z
//  Go to file/address gf gx
//  Special marks '< '> '. etc.
//  Traverse change list g; g,
//  Indenting in insert mode ^t ^d

(*
def hanoi(n, from_pole, to_pole, with_pole):
  if n == 1:
    print("Move disk 1 from", from_pole, "to", to_pole)
    return
  hanoi(n-1, from_pole, with_pole, to_pole)
  print("Move disk", n, "from", from_pole, "to", to_pole)
  hanoi(n-1, with_pole, to_pole, from_pole)
  *)
