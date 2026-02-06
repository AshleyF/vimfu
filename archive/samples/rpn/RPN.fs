open System

let execute =
  Seq.fold (|>)

let bin f = function
  | _::a::b::t ->
    f b a :: t

let add = bin (+)
let sub = bin (-)
let mul = bin (*)
let div = bin (/)

let dig v = function
  | x :: t ->
    10 * x + v :: t

let ent s = 0 :: s

let inst =
  Map.ofList [
    '0', dig 0
    '1', dig 1
    '2', dig 2
    '3', dig 3
    '4', dig 4
    '5', dig 5
    '6', dig 6
    '7', dig 7
    '8', dig 8
    '9', dig 9
    '+', add
    '-', sub
    '*', mul
    '/', div
    ' ', ent]

let flip f a b =
  f b a

let compile =
  flip Map.find inst
  |> Seq.map

let eval =
  compile >>
  execute [0] >>
  Seq.head

let rec repl () =
  Console.ReadLine()
  |> eval
  |> printf "%i\n>"
  |> repl

printf "TinyRPN\n>"
repl ()