module KeyCast

open System
open System.Threading
open System.Windows
open System.Windows.Controls
open System.Windows.Threading
open System.Windows.Media

let mutable keys = "CI\""
let mutable caption = "Change inside quotes"

let internalShow () =
    let keyCast =
        new Controls.Label(
            Content = "",
            Background = null,
            Foreground = new SolidColorBrush(Colors.White),
            FontFamily = new FontFamily("Consolas"),
            FontSize = 144.,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center)
    let keyCaption =
        new Controls.Label(
            Content = "",
            Background = null,
            Foreground = new SolidColorBrush(Colors.White),
            FontFamily = new FontFamily("Consolas"),
            FontSize = 36.,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center)
    let text =
        new Controls.StackPanel(
            Background = null)
    text.Children.Add(keyCast) |> ignore
    text.Children.Add(keyCaption) |> ignore
    let win =
        new Window (
            Topmost = true,
            Opacity = 0.8,
            Background = null,
            AllowsTransparency = true,
            WindowStyle = Windows.WindowStyle.None,
            Width = 5000.,
            Height = 250.)
    let border =
        new Border(
            CornerRadius = new CornerRadius(10.),
            Background = new SolidColorBrush(Colors.DarkRed),
            Height = 240.,
            HorizontalAlignment = HorizontalAlignment.Right,
            Padding = new Thickness(20., 0., 20., 0.),
            Child = text)
    border.MouseLeftButtonDown.Add(fun _ -> win.DragMove())
    win.Content <- border
    let dispatcherTimer = new DispatcherTimer()
    dispatcherTimer.Tick.Add(fun _ -> keyCast.Content <- keys; keyCaption.Content <- caption)
    dispatcherTimer.Interval <- TimeSpan.FromMilliseconds(10)
    dispatcherTimer.Start();
    win.Show()
    win.Left <- -660.
    win.Top <- 204. //(float)System.Windows.Forms.Screen.PrimaryScreen.Bounds.Height / 1. - 0.
    Forms.Application.Run()

let start () =
    let thread = new Thread(new ThreadStart(internalShow))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()

let set k c = keys <- k; caption <- c
