using System.Diagnostics;
using System.Text;
using ParrotSlots.Assets;
using ParrotSlots.Core;
using ParrotSlots.Graphics;
using ParrotSlots.Settings;
using ParrotSlots.Terminal.Chafa;
using ParrotSlots.Terminal.Toilet;
namespace ParrotSlots.Terminal;

/// <summary>
/// Full-screen console mode: writes raw Chafa ANSI directly to stdout.
/// </summary>
public sealed class ChafaConsoleApplication
{
    private const float FrameSeconds = 1f / 60f;
    private const int TargetFrameMs = 16;

    private readonly ImageCatalog _catalog = new();
    private readonly BoardImageCompositor _compositor;
    private readonly SpinPlaybackController _playback = new();
    private readonly Stopwatch _frameClock = new();
    private ChafaConsoleLayout _layout;
    private string _renderedBoardBackground = string.Empty;
    private int _backgroundColumns = -1;
    private int _backgroundRows = -1;

    public ChafaConsoleApplication()
    {
        _compositor = new BoardImageCompositor(_catalog);
        var (width, height) = TerminalSizeReader.Read();
        _layout = ChafaConsoleLayout.Measure(width, height);
    }

    public void Run()
    {
        if (OperatingSystem.IsWindows())
        {
            ConsoleColorSupport.EnableWindowsVirtualTerminalProcessing();
        }

        Console.OutputEncoding = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
        Console.CursorVisible = false;

        var state = new TerminalUiState();
        var uiObserver = new TerminalUiObserver(state, () => { });
        var game = TerminalGameBootstrap.CreateGame(uiObserver);

        state.Balance = game.Balance;
        state.Bet = game.CurrentBet;
        if (game.LastBoard is not null)
        {
            state.Board = game.LastBoard;
        }

        try
        {
            RedrawFull(state, BuildIdleFrame(state));
            RunLoop(state, game);
        }
        finally
        {
            Console.CursorVisible = true;
            Console.Write("\x1b[0m\x1b[?25h\x1b[2J\x1b[H");
        }
    }

    private void RunLoop(TerminalUiState state, SlotMachine game)
    {
        while (true)
        {
            if (_playback.IsPlaying)
            {
                PlaySpinAnimation(state);
                state.Board = game.LastBoard;
                RedrawFull(state, BuildIdleFrame(state));
                continue;
            }

            if (TryRefreshLayout(state, BuildIdleFrame(state)))
            {
                continue;
            }

            if (!Console.KeyAvailable)
            {
                Thread.Sleep(50);
                continue;
            }

            var key = Console.ReadKey(intercept: true);
            switch (char.ToLowerInvariant(key.KeyChar))
            {
                case 's':
                    ExecuteSpin(state, game);
                    break;
                case '-':
                case '_':
                    ChangeBet(game, state, -5);
                    RedrawFull(state, BuildIdleFrame(state));
                    break;
                case '+':
                case '=':
                    ChangeBet(game, state, 5);
                    RedrawFull(state, BuildIdleFrame(state));
                    break;
                case 'b':
                    state.Status = $"Balance: {game.Balance}, Bet: {game.CurrentBet}";
                    RedrawFull(state, BuildIdleFrame(state));
                    break;
                case 'r':
                    ShowRules(game);
                    RedrawFull(state, BuildIdleFrame(state));
                    break;
                case 'q':
                case 'x':
                    return;
            }
        }
    }

    private void PlaySpinAnimation(TerminalUiState state)
    {
        state.Status = "Spinning...";
        RedrawFull(state, BuildFrameFromPlayback());

        while (_playback.IsPlaying)
        {
            _frameClock.Restart();
            if (RefreshLayoutIfNeeded())
            {
                RedrawFull(state, BuildFrameFromPlayback());
            }
            else
            {
                RedrawBoardOnly(BuildFrameFromPlayback());
            }

            _playback.Update(FrameSeconds);

            var waitMs = TargetFrameMs - (int)_frameClock.ElapsedMilliseconds;
            if (waitMs > 0)
            {
                Thread.Sleep(waitMs);
            }
        }
    }

    private void ExecuteSpin(TerminalUiState state, SlotMachine game)
    {
        if (_playback.IsPlaying || !game.CanSpin())
        {
            state.Status = _playback.IsPlaying ? "Already spinning." : "Cannot spin: check balance and bet.";
            RedrawFull(state, BuildIdleFrame(state));
            return;
        }

        var previous = game.LastBoard;
        var session = game.BeginAnimatedSpin();
        if (session is null)
        {
            state.Status = "Spin failed.";
            RedrawFull(state, BuildIdleFrame(state));
            return;
        }

        state.Messages = session.Messages;
        _playback.Start(session, previous, fallOutPrevious: previous is not null);
    }

    private static void ChangeBet(SlotMachine game, TerminalUiState state, int delta)
    {
        var settings = GameSettings.Instance;
        var next = Math.Clamp(game.CurrentBet + delta, settings.MinBet, settings.MaxBet);
        game.SetBet(next);
    }

    private static void ShowRules(SlotMachine game)
    {
        Console.Write("\x1b[2J\x1b[H\x1b[0m");
        Console.WriteLine("=== Rules ===");
        Console.WriteLine(game.GetRulesText());
        Console.WriteLine();
        Console.WriteLine("Press any key to return...");
        Console.ReadKey(intercept: true);
    }

    private BoardAnimationFrame BuildIdleFrame(TerminalUiState state) =>
        new() { Board = state.Board };

    private BoardAnimationFrame BuildFrameFromPlayback() =>
        new()
        {
            Board = _playback.DisplayBoard,
            CellOffsetY = _playback.CellOffsetY,
            MovingParrotFrom = _playback.MovingParrotFrom,
            MovingParrotTo = _playback.MovingParrotTo,
            MovingParrotT = _playback.MovingParrotT,
            MovingParrotColor = _playback.MovingParrotColor
        };

    private bool RefreshLayoutIfNeeded()
    {
        var (width, height) = TerminalSizeReader.Read();
        var next = ChafaConsoleLayout.Measure(width, height);
        if (_layout.Matches(next))
        {
            return false;
        }

        _layout = next;
        _renderedBoardBackground = string.Empty;
        return true;
    }

    private bool TryRefreshLayout(TerminalUiState state, BoardAnimationFrame frame)
    {
        if (!RefreshLayoutIfNeeded())
        {
            return false;
        }

        RedrawFull(state, frame);
        return true;
    }

    private void RedrawFull(TerminalUiState state, BoardAnimationFrame frame)
    {
        RefreshLayoutIfNeeded();
        Console.Write("\x1b[?25l\x1b[2J\x1b[H\x1b[0m");
        WriteBoardBackground();
        WriteBoard(frame);
        WriteBottomPanel(state);
        Console.Out.Flush();
    }

    private void RedrawBoardOnly(BoardAnimationFrame frame)
    {
        WriteBoard(frame);
        Console.Out.Flush();
    }

    private void WriteBoardBackground()
    {
        try
        {
            if (string.IsNullOrEmpty(_renderedBoardBackground) ||
                _backgroundColumns != _layout.Width ||
                _backgroundRows != _layout.Height)
            {
                var png = _compositor.RenderBackground(_layout.Width, _layout.Height);
                _renderedBoardBackground = ChafaCli.RenderPng(png, _layout.Width, _layout.Height, "block+space");
                _backgroundColumns = _layout.Width;
                _backgroundRows = _layout.Height;
            }

            WriteAnsiBlock(0, 0, _layout.Height, _renderedBoardBackground);
        }
        catch (Exception ex)
        {
            WritePanelLine(
                _layout.BoardTop,
                $"Chafa background error: {ConsoleTextLayout.Fit(ex.Message, _layout.Width)}",
                dim: false,
                highlight: true);
        }
    }

    private void WriteBoard(BoardAnimationFrame frame)
    {
        try
        {
            var png = _compositor.Render(frame, _layout);
            var output = ChafaCli.RenderPng(png, _layout.BoardWidth, _layout.BoardHeight);
            WriteAnsiBlock(_layout.BoardLeft, _layout.BoardTop, _layout.BoardHeight, output);
        }
        catch (Exception ex)
        {
            WritePanelLine(
                _layout.BoardTop,
                $"Chafa error: {ConsoleTextLayout.Fit(ex.Message, _layout.Width)}",
                dim: false,
                highlight: true);
        }
    }

    private static void WriteAnsiBlock(int left, int top, int maxRows, string output)
    {
        var row = 0;
        var start = 0;

        while (row < maxRows && start <= output.Length)
        {
            var newline = output.IndexOf('\n', start);
            var end = newline >= 0 ? newline : output.Length;
            if (end > start && output[end - 1] == '\r')
            {
                end--;
            }

            Console.SetCursorPosition(left, top + row);
            Console.Out.Write(output.AsSpan(start, end - start));

            if (newline < 0)
            {
                break;
            }

            start = newline + 1;
            row++;
        }
    }

    private void ClearPanelGap()
    {
        var gapStart = _layout.BoardTop + _layout.BoardHeight;
        var gapEnd = _layout.LogTop;
        for (var row = gapStart; row < gapEnd && row < _layout.Height; row++)
        {
            Console.SetCursorPosition(0, row);
            Console.Write("\x1b[2K");
        }
    }

    private void WriteHeader(TerminalUiState state)
    {
        var controls = "S Spin  -/+ Bet  B Balance  R Rules  Q Quit";
        var stats = $"Balance {state.Balance}  Bet {state.Bet}  Win {state.LastWin}";

        if (_layout.HeaderRows >= 2)
        {
            WritePlainLine(0, "=== Pirate Parrots ===", bright: true);
            WritePlainLine(1, ConsoleTextLayout.Fit($"{stats}  |  {controls}", _layout.Width), bright: false);
            return;
        }

        WritePlainLine(0, ConsoleTextLayout.Fit($"{stats}  |  {controls}", _layout.Width), bright: true);
    }

    private void WriteBottomPanel(TerminalUiState state)
    {
        var stats = $"Bal {state.Balance} Bet {state.Bet} Win {state.LastWin}";
        ToiletPanelWriter.WriteBlock(_layout, _layout.StatsTop, _layout.StatsRows, stats, ToiletBlockKind.Stats);
    }

    private void WritePlainLine(int row, string text, bool bright)
    {
        Console.SetCursorPosition(0, row);
        Console.Write("\x1b[2K");
        Console.Write(bright ? "\x1b[1;97m" : "\x1b[37m");
        Console.Write(ConsoleTextLayout.Fit(text, _layout.Width).PadRight(_layout.Width));
        Console.Write("\x1b[0m");
    }

    private void WritePanelLine(int row, string text, bool dim, bool highlight = false)
    {
        if (row < 0 || row >= _layout.Height)
        {
            return;
        }

        var line = ConsoleTextLayout.Fit(text ?? string.Empty, _layout.Width);

        Console.SetCursorPosition(0, row);
        Console.Write("\x1b[2K");
        Console.Write("\x1b[48;5;236m");
        if (highlight)
        {
            Console.Write("\x1b[1;97m");
        }
        else if (dim)
        {
            Console.Write("\x1b[90m");
        }
        else
        {
            Console.Write("\x1b[37m");
        }

        Console.Write(line.PadRight(_layout.Width));
        Console.Write("\x1b[0m");
    }
}
