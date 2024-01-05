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
      Setup ["var foo = 1"; "var bar = 'a'"; "var foobar = foo {+} bar"]
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
      Setup ["{{} first: \"Ash\","; "  last: \"Ford\","; "  height: 1.83,"; "  age: 50,"; "  eyes: \"blue\" {}}"]
      SetFileType "javascript"
      Start "Align Text"
      Pause 2000
      Say "The property names here are nicely aligned on the left, but the values aren't."
      SayWhile ("It looks like the height is furthest over.", Compound (150, [Move Down; Move Down; Find '1']))
      Say "We can see that it's at column eleven."
      Say  "Here's the trick."
      SayWhile ("We select the block.", Compound (150, [SelectBlock; AroundBlock]))
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
      SayWhile ("In Vim, you can certainly move around with the arrow keys...", Compound (250, [
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
      SayWhile ("In Vim, you can move by words with W...", Compound (400, [Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word; Move Word]))
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
      SayWhile ("...and G followed by E, you can quickly move by words forward and backward to the start and end of each.", Move BackWordEnd)
      Finish ]

let basicMotions3 = // W B E gE
    [ Launch
      Setup [""; ""; "def fact{(}n{)}:"; "  if n == 0:"; "    return 1"; "  return n*fact{(}n-1{)}"; ""; "print{(}fact{(}7{)}{)}"]
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
      Say "...you can very quickly move by big words."
      Finish ]

let basicMotions4 = // $ ^ 0
    [ Launch
      Setup [""; ""; "def fact{(}n{)}:"; "  if n == 0:"; "    return 1"; "  return n*fact{(}n-1{)}"; ""; "print{(}fact{(}7{)}{)}"]
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
      Setup ["def fact{(}n{)}:"; "  if n == 0:"; "    return 1"; "  return n*fact{(}n-1{)}"; ""; "print{(}fact{(}7{)}{)}"; ""; "def fib{(}n{)}:"; "  if n <= 1:"; "    return n"; "  return fib{(}n-1{)} + fib{(}n-2{)}"; ""; "print{(}fib{(}7{)}{)}"]
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
      SayWhile ("Notice that, if your cursor is somewhere within a line, the column is maintained.", Move WordEnd)
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
      SayWhile ("GG takes you to the top of the document...", Move TopOfDocument)
      Pause 800
      SayWhile ("... and Shift-G takes you to the bottom of the document...", Move BottomOfDocument)
      Pause 800
      Finish ]

let basicMotions6 = // ) ( } {
    [ Launch
      Setup ["# It's a sentence.  And again!          And another         one... How          about this? Indeed!"; ""; "def fact{(}n{)}:"; "  if n == 0:"; "    return 1"; "  return n*fact{(}n-1{)}"; ""; "print{(}fact{(}7{)}{)}"; ""; "def fib{(}n{)}:"; "  if n <= 1:"; "    return n"; "  return fib{(}n-1{)} + fib{(}n-2{)}"; ""; "print{(}fib{(}7{)}{)}"]
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
      Setup ["#include <stdio.h>"; ""; "int isEven{(}int n{)}"; "{{}"; "  return n {%} 2 == 0;"; "{}}"; ""; "void msg{(}char *m{)}"; "{{}"; "  printf{(}\"{%}s\\n\",m{)};"; "{}}"; ""; "int main{(}{)}"; "{{}"; "  if {(}!isEven{(}42{)}{)}"; "  {{}"; "    msg{(}\"Panic!\"{)};"; "  {}}"; "  return 0;"; "{}}"; ""]
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

//    -=  \   ~!@  % &   _+  O"<> :" 
//  a cd    i     opqrs u  xyz
//  A CD    IJK   OPQRS U  XYZ
//  
//  Basic Motions 1  h j k l ␣ ⌫
//  Basic Motions 2  w b e ge
//  Basic Motions 3  W B E gE
//  Basic Motions 4  $ ^ 0
//  Basic Motions 5  H L M gg G
//  Basic Motions 6  ) ( } {
//  Basic Motions 7  ]] [[ ][ []
//  Mark m ' ` '' ``
//  Find f F t T ; ,
//  Search * # n N / ?
//  Visual v V ^v
//  Dot .
