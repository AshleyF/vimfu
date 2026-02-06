printfn
  "Fallout Solver\n"

// known words
let known = [
  "PILE", 0
  "MOST", 1
  "FACT", 1]

// unknown words
let unknown = [
  "PUSH"
  "TASK"
  "EVEN"
  "MAZE"
  "LAST"
  "TELL"]

let uncurry f (x,y)=
  f x y

let similarity a b =
  Seq.zip a b
  |> Seq.filter
     (uncurry (=))
  |> Seq.length

let matches (w, c) =
  unknown
  |> Seq.filter
     ((similarity w)
      >> ((=) c))

known
|> Seq.map matches
|> Seq.map
   Set.ofSeq
|> Seq.reduce
   Set.intersect
|> printfn
   "Solutions:\n%A"
