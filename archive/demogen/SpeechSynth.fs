module SpeechSynth

open System.Speech.Synthesis

let synch = new SpeechSynthesizer()
let say (text : string) = synch.Speak text |> ignore
