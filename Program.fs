﻿open Script
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

//Lesson.numbers |> go; pause 5000
//Lesson.alignText |> go; pause 5000
//Lesson.basicMotions1 |> go; pause 5000
//Lesson.basicMotions2 |> go; pause 5000
//Lesson.basicMotions3 |> go; pause 5000

Lesson.basicMotions4 |> go; pause 5000
Lesson.basicMotions5 |> go; pause 5000
Lesson.basicMotions6 |> go; pause 5000
Lesson.basicMotions7 |> go; pause 5000

(*
- Run KeyClicker.py
- Capture: 30fps, 50000kbps, 100% quality, no mouse capture, audio speakers only, 1860x1860
- Encode: MP4 50000kbps 1080x1080
*)