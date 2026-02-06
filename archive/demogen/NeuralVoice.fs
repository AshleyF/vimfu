module NeuralVoice

open System
open System.IO
open Microsoft.CognitiveServices.Speech
open Microsoft.CognitiveServices.Speech.Audio

let mutable config : SpeechConfig = null

let player = new Media.SoundPlayer();

let say text =
    let dir = @"C:\data\Speech"
    let file = $"{dir}\AshleyF.{text.GetHashCode()}.wav"
    if not (File.Exists file) then
        if config = null then
            config <- SpeechConfig.FromSubscription(
                Environment.GetEnvironmentVariable("VOICE_API_KEY"),
                "westus",
                EndpointId = "da2b2079-97aa-46e4-b020-345677fe1167",
                SpeechSynthesisVoiceName = "AshleyF-NeutralNeural")
            config.SetSpeechSynthesisOutputFormat(SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)
        use fileOutput = AudioConfig.FromWavFileOutput(file)
        use synthesizer = new SpeechSynthesizer(config, fileOutput)
        use result = synthesizer.SpeakTextAsync(text).Result // TODO: async
        if result.Reason = ResultReason.SynthesizingAudioCompleted then
            printfn $"Speech synthesized for text [{text}], and the audio was saved"
            File.WriteAllText(Path.ChangeExtension(file, "txt"), text)
        elif result.Reason = ResultReason.Canceled then
            File.Delete(file)
            let cancellation = SpeechSynthesisCancellationDetails.FromResult(result)
            printfn $"CANCELED: Reason={cancellation.Reason}"
            if cancellation.Reason = CancellationReason.Error then
                printfn $"CANCELED: ErrorCode={cancellation.ErrorCode}"
                printfn $"CANCELED: ErrorDetails=[{cancellation.ErrorDetails}]"
                printfn $"CANCELED: Did you update the subscription info?"
    player.SoundLocation <- file
    player.PlaySync()
