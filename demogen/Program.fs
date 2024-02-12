open Script
open System.IO

let del file = if File.Exists file then File.Delete file
del @"C:\Users\ashleyf\AppData\Local\nvim-data\swap\C%%Program Files%Neovim%bin%Fu.swo"
del @"C:\Users\ashleyf\AppData\Local\nvim-data\swap\C%%Program Files%Neovim%bin%Fu.swp"

KeyCast.start ()
//Lesson.tracey
//Lesson.dontRepeat
//Lesson.numbers
//Lesson.alignText
//Lesson.basicMotions1
//Lesson.basicMotions2
//|> go

//Lesson.nothing |> go

//Lesson.numbers |> go; pause 5000 // 01 JAN 2024
//Lesson.alignText |> go; pause 5000 // 02 JAN 2024
//Lesson.basicMotions1 |> go; pause 5000 // 03 JAN 2024
//Lesson.basicMotions2 |> go; pause 5000 // 04 JAN 2024
//Lesson.uselessUnderscore |> go; pause 5000 // 05 JAN 2024
//Lesson.basicMotions3 |> go; pause 5000 // 06 JAN 2024
//Lesson.matchingPairs |> go; pause 5000 // 07 JAN 2024
//Lesson.basicMotions4 |> go; pause 5000 // 08 JAN 2024
//Lesson.search |> go; pause 5000 // 09 JAN 2024
//Lesson.basicMotions5 |> go; pause 5000 // 10 JAN 2024
//Lesson.changingCase |> go; pause 5000 // 11 JAN 2024
//Lesson.basicMotions6 |> go; pause 5000 // 12 JAN 2024
//Lesson.findCharacter |> go; pause 5000 // 13 JAN 2024
//Lesson.basicMotions7 |> go; pause 5000 // 14 JAN 2024
//Lesson.joinLines |> go; pause 5000 // 15 JAN 2024
//Lesson.basicMotions8 |> go; pause 5000 // 16 JAN 2024
//Lesson.marks |> go; pause 5000 // 17 JAN 2024
//Lesson.goToLineColumn |> go; pause 5000 // 18 JAN 2024
//Lesson.scrolling |> go; pause 5000 // 19 JAN 2024
//Lesson.revertFile |> go; pause 5000 // 20 JAN 2024
//Lesson.quitting |> go; pause 5000 // 21 JAN 2024
//Lesson.indenting |> go; pause 5000 // 22 JAN 2024
//Lesson.jumps |> go; pause 5000 // 23 JAN 2024
//Lesson.deleteChar |> go; pause 5000 // 24 JAN 2024
//Lesson.undo |> go; pause 5000 // 25 JAN 2024
//Lesson.visual |> go; pause 5000 // 26 JAN 2024
//Lesson.visualAdvanced |> go; pause 5000 // 27 JAN 2024
//Lesson.replace |> go; pause 5000 // 28 JAN 2024
//Lesson.delete |> go; pause 5000 // 29 JAN 2024
//Lesson.put |> go; pause 5000 // 30 JAN 2024
//Lesson.yank |> go; pause 5000 // 31 JAN 2024
//Lesson.patterns |> go; pause 5000 // 01 FEB 2024
//Lesson.textObjects1 |> go; pause 5000 // 02 FEB 2024
//Lesson.textObjects2 |> go; pause 5000 // 03 FEB 2024
//Lesson.textObjects3 |> go; pause 5000 // 04 FEB 2024
//Lesson.textObjects4 |> go; pause 5000 // 05 FEB 2024
//Lesson.insert |> go; pause 5000 // 06 FEB 2024
//Lesson.insertAdvanced |> go; pause 5000 // 07 FEB 2024
//Lesson.openLine |> go; pause 5000 // 08 FEB 2024
//Lesson.change |> go; pause 5000 // 09 FEB 2024
//Lesson.substitute |> go; pause 5000 // 10 FEB 2024
//Lesson.jumpPercent |> go; pause 5000
Lesson.countedMotions |> go; pause 5000
//Lesson.numberedLines |> go; pause 5000
//Lesson.countedInsert |> go; pause 5000
//Lesson.insertModeDelete |> go; pause 5000
//Lesson.verticalInsert |> go; pause 5000

(*
- Run KeyClicker.py
- Capture: 30fps, 50000kbps, 100% quality, no mouse capture, audio speakers only, 1860x1860
- Encode: MP4 50000kbps 1080x1080
- Suspend voice!
*)
