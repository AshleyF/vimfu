module Script

open System
open System.Threading
open System.Windows.Forms
open System.Runtime.InteropServices
open NeuralVoice // or SpeechSynth
//open SpeechSynth // or NeuralVoice

let both f0 f1 =
    let t0 = new Thread(new ThreadStart(f0))
    let t1 = new Thread(new ThreadStart(f1))
    t0.Start()
    t1.Start()
    t0.Join()
    t1.Join()

let pause ms = (new Random()).Next(50) + ms |> Thread.Sleep

let key k = SendKeys.SendWait(k)

let typing text =
    for k in text do
        string k |> key
        pause 50

type TextObject =
    | InnerQuotes
    | InnerTicks
    | InnerBackticks
    | InnerAngleBrackets
    | InnerBrackets
    | InnerBlock
    | InnerBigBlock
    | InnerWord
    | InnerBigWord
    | InnerParagraph
    | InnerSentence
    | InnerTag
    | AroundQuotes
    | AroundTicks
    | AroundBackticks
    | AroundAngleBrackets
    | AroundBrackets
    | AroundBlock
    | AroundBigBlock
    | AroundWord
    | AroundBigWord
    | AroundParagraph
    | AroundSentence
    | AroundTag

type Motion =
    | Up
    | UpNum of int
    | Down
    | DownNum of int
    | Right
    | Left
    | Word
    | BigWord
    | BackWord
    | BackBigWord
    | WordEnd
    | BigWordEnd
    | BackWordEnd
    | BackBigWordEnd
    | EndOfLine
    | StartOfLine
    | FirstColumn
    | LowestLine
    | HighestLine
    | MiddleLine
    | TopOfDocument
    | BottomOfDocument
    | PercentageOfDocument of int
    | Sentence
    | BackSentence
    | Paragraph
    | BackParagraph
    | SectionStart
    | BackSectionStart
    | SectionEnd
    | BackSectionEnd
    | StartOfNextLine | StartOfNextLineCR
    | StartOfPreviousLine
    | MatchingBraces
    | Find of char
    | Till of char
    | FindReverse of char
    | TillReverse of char
    | NextChar of char
    | PrevChar of char
    | GoToMark of char
    | GoToMarkChar of char
    | GoToLine of int
    | GoToColumn of int
    | JumpBack
    | JumpBackChar
    | JumpPrevious
    | JumpNext
    | SearchStar
    | SearchHash
    | SearchNext
    | SearchPrev
    | VisualSelection // not really a motion, but used in place of motions
    | Span of TextObject

type Action =
    | Launch
    | Restart
    | Start of string
    | Finish
    | Setup of string seq
    | Esc
    | Text of string
    | Type of int * string
    | Normal of string * string
    | Pause of int
    | Insert
    | InsertBefore
    | CountedInsert of int
    | CountedInsertBefore of int
    | InsertFirstColumn
    | InsertAtLast
    | Enter
    | Tab
    | Backspace
    | BackspaceCtrlH
    | DeleteWordCtrlW
    | DeleteLineCtrlU
    | After
    | AfterLine
    | CountedAfter of int
    | CountedAfterLine of int
    | Repeat
    | Undo
    | UndoLine
    | Redo
    | ToggleCase
    | ToggelCaseMotion of Motion
    | UpperCase
    | LowerCase
    | Visual
    | VisualLine
    | VisualBlock
    | VisualCursorPosition
    | JumpSelectionStart
    | JumpSelectionEnd
    | OpenBelow
    | OpenAbove
    | CountedOpenBelow of int
    | CountedOpenAbove of int
    | ZoomTop
    | ZoomMiddle
    | ZoomBottom
    | DeleteLine
    | YankLine
    | YankToLastLine
    | Put
    | PutBefore
    | Record of char
    | StopRecording
    | Macro of char
    | Mark of char
    | RepeatLastMacro
    | RepeatMacro of char * int
    | SelectBlock
    | Reselect
    | Increment
    | IncrementOrdinals
    | Say of string
    | SayWhile of string * Action
    | Compound of int * Action seq
    | QuitWithoutSaving
    | SetFileType of string
    | JoinLine
    | SubstituteLine
    | Substitute
    | ChangeLine
    | ChangeToEnd
    | Change of Motion
    | Delete of Motion
    | Yank of Motion
    | DeleteWithX of Motion
    | Dot
    | ScrollDown
    | ScrollUp
    | ScrollTop
    | ScrollMiddle
    | ScrollBottom
    | JumpDown
    | JumpUp
    | JumpDownHalf
    | JumpUpHalf
    | GoToFile
    | IndentLine
    | UnindentLine
    | Indent of Motion
    | Unindent of Motion
    | AutoIndentLine
    | AutoIndent of Motion
    | DeleteChar
    | DeletePrevChar
    | Replace of char
    | ReplaceMode
    | Key of string * string * string
    | Move of Motion

let shift c = if Char.IsUpper(c) then $"⇧{c}" else c.ToString()

let glob c = if Char.IsUpper(c) then "global " else ""

[<DllImport("user32.dll", EntryPoint = "SetCursorPos")>]
extern bool SetCursorPos(int X, int Y)

[<DllImport("user32.dll", EntryPoint = "mouse_event")>]
extern void MouseEvent(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo)

let focusHack() =
    let MOUSEEVENTF_LEFTDOWN = 0x0002u
    let MOUSEEVENTF_LEFTUP = 0x0004u
    SetCursorPos(10, 1000) |> ignore
    MouseEvent(MOUSEEVENTF_LEFTDOWN, 0u, 0u, 0u, 0)
    MouseEvent(MOUSEEVENTF_LEFTUP, 0u, 0u, 0u, 0)

let rec edit = function
    //| Launch -> KeyCast.set "Starting" "One moment..."; key "^({ESC}e)"; pause 5000; key "cmd"; pause 5000; key "{enter}"; pause 5000; key "^+{5}"; pause 5000; key "alias vi=nvim{enter}clear{enter}"
    | Launch -> KeyCast.set "Starting" "One moment..."; focusHack(); key "^+{5}"; pause 5000; focusHack(); key "alias vi=nvim{enter}rm -rf {~}/.local/share/nvim/swap/{enter}clear{enter}vi{enter}:file Fu{ENTER}:{ESC}"
    | Restart -> KeyCast.set "Restarting" "One moment..."; pause 3000
    | Start message -> KeyCast.set "VimFu" message; pause 800
    | Finish -> pause 800; KeyCast.set "Finished" "Cut!"; key "{ESC}:q!{ENTER}"
    | Setup lines -> key ":set noautoindent{ENTER}"; pause 300; key "{ESC}i"; lines |> Seq.iter (fun line -> key (line.Replace("{", "__LEFT_CURLY__").Replace("}", "__RIGHT_CURLY__").Replace("+", "{+}").Replace("^", "{^}").Replace("%", "{%}").Replace("(", "{(}").Replace(")", "{)}").Replace("`", "{`}").Replace("__LEFT_CURLY__", "{{}").Replace("__RIGHT_CURLY__", "{}}")); key "{ENTER}"); pause 3000; key "{ESC}"; pause 1000; key "ddgg0:set autoindent{ENTER}:{ESC}"
    | Esc -> KeyCast.set "⎋" "normal mode"; key "{ESC}"
    | Text text -> KeyCast.set "⌨" ""; typing text
    | Type (delay, text) -> KeyCast.set "⌨" ""; text |> Seq.iter (fun k -> typing $"{k}"; pause delay)
    | Normal (text, caption) -> KeyCast.set text caption; typing text
    | Pause ms -> pause ms
    | Insert -> KeyCast.set "i" "insert"; key "i"
    | InsertBefore -> KeyCast.set "⇧I" "insert before line"; key "I"
    | CountedInsert n -> KeyCast.set $"{n}i" $"insert {n}"; key $"{n}i"
    | CountedInsertBefore n -> KeyCast.set $"{n}⇧I" $"insert {n} before line"; key $"{n}I"
    | InsertFirstColumn -> KeyCast.set "g⇧I" "insert first column"; key "gI"
    | InsertAtLast -> KeyCast.set "gi" "insert at last"; key "gi"
    | After -> KeyCast.set "a" "after"; key "a"
    | AfterLine -> KeyCast.set "⇧A" "after line"; key "A"
    | CountedAfter n -> KeyCast.set $"{n}a" $"{n} after"; key $"{n}a"
    | CountedAfterLine n -> KeyCast.set $"{n}⇧A" $"{n} after line"; key $"{n}A"
    | Enter -> KeyCast.set "⌨" ""; key "{ENTER}"
    | Tab -> KeyCast.set "⌨" ""; key "{TAB}"
    | Backspace -> KeyCast.set "⌫" "backspace"; key "\b"
    | BackspaceCtrlH -> KeyCast.set "⌃h" "backspace"; key "^h"
    | DeleteWordCtrlW -> KeyCast.set "⌃w" "delete word"; key "^w"
    | DeleteLineCtrlU -> KeyCast.set "⌃u" "delete line"; key "^u"
    | Move Up -> KeyCast.set "k" "up"; key "k"
    | Move (UpNum n) -> KeyCast.set $"{n}k" $"up {n}"; key $"{n}k"
    | Move Down -> KeyCast.set "j" "down"; key "j"
    | Move (DownNum n) -> KeyCast.set $"{n}j" $"down {n}"; key $"{n}j"
    | Move Right -> KeyCast.set "l" "right"; key "l"
    | Move Left -> KeyCast.set "h" "left"; key "h"
    | Move Word -> KeyCast.set "w" "forward word"; key "w"
    | Move BigWord -> KeyCast.set "⇧W" "forward WORD"; key "W"
    | Move BackWord -> KeyCast.set "b" "back word"; key "b"
    | Move BackBigWord -> KeyCast.set "⇧B" "back WORD"; key "B"
    | Move WordEnd -> KeyCast.set "e" "end of word"; key "e"
    | Move BigWordEnd -> KeyCast.set "⇧E" "end of WORD"; key "E"
    | Move BackWordEnd -> KeyCast.set "ge" "prev end of word"; key "ge"
    | Move BackBigWordEnd -> KeyCast.set "g⇧E" "prev end of WORD"; key "gE"
    | Move EndOfLine -> KeyCast.set "⇧$" "end of line"; key "$"
    | Move StartOfLine -> KeyCast.set "⇧^" "start of line"; key "{^}"
    | Move FirstColumn -> KeyCast.set "0" "column zero"; key "0"
    | Move LowestLine -> KeyCast.set "⇧L" "lowest line"; key "L"
    | Move HighestLine -> KeyCast.set "⇧H" "highest line"; key "H"
    | Move MiddleLine -> KeyCast.set "⇧M" "middle line"; key "M"
    | Move TopOfDocument -> KeyCast.set "gg" "go top"; key "gg"
    | Move BottomOfDocument -> KeyCast.set "⇧G" "go bottom"; key "G"
    | Move (PercentageOfDocument n) -> KeyCast.set $"{n}⇧%%" $"go {n}%%"; key $"{n}"; key "{%}"
    | Move Sentence -> KeyCast.set "⇧)" "next sentence"; key "{)}"
    | Move BackSentence -> KeyCast.set "⇧(" "prev sentence"; key "{(}"
    | Move Paragraph -> KeyCast.set "⇧}" "next paragraph"; key "{}}"
    | Move BackParagraph -> KeyCast.set "⇧{" "prev paragraph"; key "{{}"
    | Move SectionStart -> KeyCast.set "]]" "next section start"; key "{]}{]}"
    | Move BackSectionStart -> KeyCast.set "[[" "prev section start"; key "{[}{[}"
    | Move SectionEnd -> KeyCast.set "][" "next section end"; key "{]}{[}"
    | Move BackSectionEnd -> KeyCast.set "[]" "prev section end"; key "{[}{]}"
    | Move StartOfNextLine -> KeyCast.set "⇧+" "start of next line"; key "{+}"
    | Move StartOfNextLineCR -> KeyCast.set "⏎" "start of next line"; key "{+}"
    | Move StartOfPreviousLine -> KeyCast.set "-" "start of prev line"; key "-"
    | Move MatchingBraces -> KeyCast.set "%" "matching"; key "{%}"
    | Repeat -> KeyCast.set "." "repeat"; key ".";
    | Undo -> KeyCast.set "u" "undo"; key "u"
    | UndoLine -> KeyCast.set "⇧U" "undo line"; key "U"
    | Redo -> KeyCast.set "⌃r" "redo"; key "^r"
    | ToggleCase -> KeyCast.set "⇧~" "toggle case"; key "{~}"
    | ToggelCaseMotion m ->
        match m with
        | Word -> KeyCast.set "g⇧~w" "toggle case of word"; key "g{~}w"
        | _ -> failwith $"Toggle case motion not implemented ({m})."
    | UpperCase -> KeyCast.set "g⇧U" "uppercase"; key "gU"
    | LowerCase -> KeyCast.set "gu" "uppercase"; key "gu"
    | Visual -> KeyCast.set "v" "visual mode"; key "v"
    | VisualLine -> KeyCast.set "⇧V" "visual line mode"; key "V"
    | VisualBlock -> KeyCast.set "⌃v" "visual block mode"; key "^q" // CTRL-Q because terminal intercepts
    | VisualCursorPosition -> KeyCast.set "o" "cursor position"; key "o"
    | JumpSelectionStart -> KeyCast.set "`⇧<" "jump selection start"; key "`<"
    | JumpSelectionEnd -> KeyCast.set "`⇧>" "jump selection end"; key "`>"
    | OpenBelow -> KeyCast.set "o" "open below"; key "o"
    | OpenAbove -> KeyCast.set "⇧O" "open above"; key "O"
    | CountedOpenBelow n -> KeyCast.set $"{n}o" $"open {n} below"; key $"{n}o"
    | CountedOpenAbove n -> KeyCast.set $"{n}⇧O" $"open {n} above"; key $"{n}O"
    | ZoomTop -> KeyCast.set "zt" "zoom top"; key "zt"
    | ZoomMiddle -> KeyCast.set "zz" "zoom middle"; key "zz"
    | ZoomBottom -> KeyCast.set "zb" "zoom bottom"; key "zb"
    | DeleteLine -> KeyCast.set "dd" "delete line"; key "dd"
    | YankLine -> KeyCast.set "yy" "yank line"; key "yy"
    | YankToLastLine -> KeyCast.set "y⇧G" "yank to last line"; key "yG"
    | Put -> KeyCast.set "p" "put"; key "p"
    | PutBefore -> KeyCast.set "⇧P" "put before"; key "P"
    | Record register -> KeyCast.set $"q{shift register}" $"record into {register}"; key $"q{register}"
    | StopRecording  -> KeyCast.set $"q" "stop recording"; key "q"
    | Macro register -> KeyCast.set $"⇧@{shift register}" $"play macro {register}"; key $"@{register}"
    | Mark c -> KeyCast.set $"m{shift c}" $"mark {glob c}'{c}'"; key $"m{c}"
    | RepeatLastMacro -> KeyCast.set "⇧@@" "repeat last macro"; key "@@"
    | RepeatMacro (register, n) -> KeyCast.set $"{n}⇧@{shift register}" $"repeat macro {register} {n} times"; key $"{n}@{register}"
    | SelectBlock -> KeyCast.set "⌃v" "select block"; key "^q" // CTRL-Q because CTRL-V is mapped to paste
    | Reselect -> KeyCast.set "gv" "reselect visual"; key "gv"
    | Increment -> KeyCast.set "⌃A" "increment"; key "^a"
    | IncrementOrdinals -> KeyCast.set "g⌃a" "increment ordinals"; key "g^a"
    | Say text -> say text
    | SayWhile (text, action) -> both (fun () -> say text) (fun () -> edit action)
    | Compound (wait, actions) -> Seq.iter (fun a -> pause wait; edit a) actions
    | QuitWithoutSaving -> KeyCast.set ":q!⏎" "quit without saving"; key ":q!{ENTER}"
    | SetFileType kind -> key $":set filetype={kind}"; pause 300; key "{ENTER}"; pause 200; key ":{ESC}"; pause 2000
    | Move (Find c) -> KeyCast.set $"f{shift c}" $"find '{c}'"; key $"f{c}"
    | Move (Till c) -> KeyCast.set $"t{shift c}" $"till '{c}'"; key $"t{c}"
    | Move (FindReverse c) -> KeyCast.set $"⇧F{shift c}" $"reverse find '{c}'"; key $"F{c}"
    | Move (TillReverse c) -> KeyCast.set $"⇧T{shift c}" $"reverse till '{c}'"; key $"T{c}"
    | Move (NextChar c) -> KeyCast.set ";" $"next '{c}'"; key ";"
    | Move (PrevChar c) -> KeyCast.set "," $"prev '{c}'"; key ","
    | Move (GoToMark c) -> KeyCast.set $"'{shift c}" $"go to mark '{c}'"; key $"'{c}"
    | Move (GoToMarkChar c) -> KeyCast.set $"`{shift c}" $"go to mark '{c}'"; key ("{`}" + $"{c}")
    | Move (GoToLine n) -> KeyCast.set $"{n}⇧G" $"go to line {n}"; typing $"{n}G"
    | Move (GoToColumn n) -> KeyCast.set $"{n}⇧|" $"go to column {n}"; typing $"{n}|"
    | Move JumpBack -> KeyCast.set "''" "jump back"; key "''"
    | Move JumpBackChar -> KeyCast.set "``" "jump back char"; key "{`}{`}"
    | Move JumpPrevious -> KeyCast.set "⌃o" "jump previous"; key "^o"
    | Move JumpNext -> KeyCast.set "⌃i" "jump next"; key "^i"
    | Move SearchStar -> KeyCast.set "⇧*" "search"; key "*"
    | Move SearchHash -> KeyCast.set "⇧#" "reverse search"; key "#"
    | Move SearchNext -> KeyCast.set "n" "search next"; key "n"
    | Move SearchPrev -> KeyCast.set "⇧N" "search prev"; key "N"
    | Move (Span InnerQuotes) -> KeyCast.set "i⇧\"" "inner \"...\""; key "i\""
    | Move (Span InnerTicks) -> KeyCast.set "i'" "inner '...'"; key "i'"
    | Move (Span InnerBackticks) -> KeyCast.set "i`" "inner `...`"; key "\\i" // :map \i i`  because of sendkey insanity
    | Move (Span InnerBrackets) -> KeyCast.set "i[" "inner [...]"; key "i["
    | Move (Span InnerAngleBrackets) -> KeyCast.set "i⇧<" "inner <...>"; key "i<"
    | Move (Span InnerBlock) -> KeyCast.set "i⇧(" "inner (...)"; key "i{(}"
    | Move (Span InnerBigBlock) -> KeyCast.set "i⇧{" "inner {...}"; key "i{{}"
    | Move (Span InnerWord) -> KeyCast.set "iw" "inner word"; key "iw"
    | Move (Span InnerBigWord) -> KeyCast.set "i⇧W" "inner WORD"; key "iW"
    | Move (Span InnerParagraph) -> KeyCast.set "ip" "inner paragraph"; key "ip"
    | Move (Span InnerSentence) -> KeyCast.set "is" "inner sentence"; key "is"
    | Move (Span InnerTag) -> KeyCast.set "it" "inner tag"; key "it"
    | Move (Span AroundQuotes) -> KeyCast.set "a⇧\"" "around \"...\""; key "a\""
    | Move (Span AroundTicks) -> KeyCast.set "a'" "around '...'"; key "a'"
    | Move (Span AroundBackticks) -> KeyCast.set "a`" "around `...`"; key "\\a" // :map \a a`  because of sendkey insanity
    | Move (Span AroundBrackets) -> KeyCast.set "a[" "around [...]"; key "a["
    | Move (Span AroundAngleBrackets) -> KeyCast.set "a⇧<" "around <...>"; key "a<"
    | Move (Span AroundBlock) -> KeyCast.set "a⇧(" "around (...)"; key "a{(}"
    | Move (Span AroundBigBlock) -> KeyCast.set "a⇧{" "around {...}"; key "a{{}"
    | Move (Span AroundWord) -> KeyCast.set "aw" "around word"; key "aw"
    | Move (Span AroundBigWord) -> KeyCast.set "a⇧W" "around WORD"; key "aW"
    | Move (Span AroundParagraph) -> KeyCast.set "ap" "around paragraph"; key "ap"
    | Move (Span AroundSentence) -> KeyCast.set "as" "around sentence"; key "as"
    | Move (Span AroundTag) -> KeyCast.set "at" "around tag"; key "at"
    | JoinLine -> KeyCast.set "⇧J" "join line"; key "J"
    | SubstituteLine -> KeyCast.set "⇧S" "substitute line"; key "S"
    | Substitute -> KeyCast.set "s" "substitute"; key "s"
    | ChangeLine -> KeyCast.set "cc" "change line"; key "cc"
    | ChangeToEnd -> KeyCast.set "⇧C" "change to end of line"; key "C"
    | Change m ->
        match m with
        | Word -> KeyCast.set "cw" "change word"; key "cw"
        | Span AroundBlock -> KeyCast.set "cab" "change around block"; key "cab"
        | _ -> failwith $"Change motion not implemented ({m})"
    | Delete m ->
        match m with
        | Word -> KeyCast.set "dw" "delete word"; key "dw"
        | WordEnd -> KeyCast.set "de" "delete to end of word"; key "de"
        | BackWord -> KeyCast.set "db" "delete back word"; key "db"
        | BigWord -> KeyCast.set "dW" "delete WORD"; key "dW"
        | BottomOfDocument -> KeyCast.set "dG" "delete to bottom of doc"; key "dG"
        | EndOfLine -> KeyCast.set "⇧D" "delete to end of line"; key "D"
        | VisualSelection -> KeyCast.set "d" "delete selection"; key "d"
        | Span AroundBlock -> KeyCast.set "da⇧(" "delete around block"; key "da{(}"
        | Span InnerTicks -> KeyCast.set "di'" "delete inner ticks"; key "di'"
        | Span AroundBigBlock -> KeyCast.set "da⇧{" "delete around BLOCK"; key "daB"
        | _ -> failwith $"Delete motion not implemented ({m})"
    | Yank m ->
        match m with
        | Word -> KeyCast.set "yw" "yank word"; key "yw"
        | BigWord -> KeyCast.set "yW" "yank WORD"; key "yW"
        | BottomOfDocument -> KeyCast.set "yG" "yank to bottom of doc"; key "yG"
        | EndOfLine -> KeyCast.set "⇧Y" "yank line"; key "Y"
        | VisualSelection -> KeyCast.set "y" "yank selection"; key "y"
        | Span AroundBlock -> KeyCast.set "ya⇧(" "yank around block"; key "ya{(}"
        | _ -> failwith $"Yank motion not implemented ({m})"
    | DeleteWithX m ->
        match m with
        | VisualSelection -> KeyCast.set "x" "delete selection"; key "x"
        | _ -> failwith $"Delete with X motion not implemented ({m})"
    | Dot -> KeyCast.set "." "repeat action"; key "."
    | ScrollDown -> KeyCast.set "⌃y" "scroll down"; key "^y"
    | ScrollUp -> KeyCast.set "⌃e" "scroll up"; key "^e"
    | ScrollTop -> KeyCast.set "zt" "scroll top"; key "zt"
    | ScrollMiddle -> KeyCast.set "zz" "scroll middle"; key "zz"
    | ScrollBottom -> KeyCast.set "zb" "scroll bottom"; key "zb"
    | JumpDown -> KeyCast.set "⌃f" "jump forward"; key "^f"
    | JumpUp -> KeyCast.set "⌃b" "jump back"; key "^b"
    | JumpDownHalf -> KeyCast.set "⌃d" "jump down"; key "^d"
    | JumpUpHalf -> KeyCast.set "⌃u" "jump up"; key "^u"
    | GoToFile -> KeyCast.set "gf" "go to file"; key "gf"
    | IndentLine -> KeyCast.set "⇧>>" "indent"; key ">>"
    | UnindentLine -> KeyCast.set "⇧<<" "unindent"; key "<<"
    | Indent m ->
        match m with
        | Paragraph -> KeyCast.set "⇧>}" "indent paragraph"; key ">{}}"
        | _ -> failwith $"Indent motion not implemented ({m})"
    | Unindent m ->
        match m with
        | Paragraph -> KeyCast.set "⇧<}" "unindent paragraph"; key "<{}}"
        | _ -> failwith $"Unindent motion not implemented ({m})"
    | AutoIndentLine -> KeyCast.set "==" "autoindent"; key "=="
    | AutoIndent m ->
        match m with
        | Paragraph -> KeyCast.set "=⇧}" "autoindent paragraph"; key "={}}"
        | VisualSelection -> KeyCast.set "=" "autoindent selection"; key "="
        | _ -> failwith $"Autoindent motion not implemented ({m})"
    | DeleteChar -> KeyCast.set "x" "delete char"; key "x"
    | DeletePrevChar -> KeyCast.set "⇧X" "delete prev char"; key "X"
    | Replace c -> KeyCast.set $"r{shift c}" $"replace with '{c}'"; key $"r{c}"
    | ReplaceMode -> KeyCast.set "⇧R" "replace mode"; key "R"
    | Key (cast, desc, k) -> KeyCast.set cast desc; key k
    | _ -> failwith "Unknown action"


let rec go = function
    | action :: tail -> edit action; go tail
    | [] -> ()
