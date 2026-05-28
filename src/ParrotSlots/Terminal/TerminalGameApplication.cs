using ParrotSlots.Assets;
using ParrotSlots.Builder;
using ParrotSlots.Core;
using ParrotSlots.Graphics;
using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Terminal.Chafa;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;
using Terminal.Gui;

namespace ParrotSlots.Terminal;

public sealed class TerminalGameApplication
{
    private const float FrameSeconds = 1f / 30f;

    private readonly ImageCatalog _catalog = new();
    private readonly bool _useChafa;
    private SpriteCache _sprites = null!;
    private readonly SpinPlaybackController _playback = new();

    public TerminalGameApplication(bool useChafa = false)
    {
        _useChafa = useChafa;
    }

    public void Run()
    {
        if (OperatingSystem.IsWindows())
        {
            ConsoleColorSupport.EnableWindowsVirtualTerminalProcessing();
        }

        Application.Init();
        try
        {
            var (termWidth, termHeight) = TerminalSizeReader.Read();
            var layout = TerminalLayoutPlan.Fit(termWidth, termHeight);
            _sprites = new SpriteCache(_catalog, layout.MaxSpritePixelSize);

            var state = new TerminalUiState();
            SlotMachine? game = null;

            Label statusLabel = null!;
            Label infoLabel = null!;
            IBoardView boardDisplay = null!;
            View boardView = null!;
            TextView logView = null!;
            Button spinButton = null!;
            Button betDownButton = null!;
            Button betUpButton = null!;

            void SetControlsEnabled(bool enabled)
            {
                spinButton.Enabled = enabled;
                betDownButton.Enabled = enabled;
                betUpButton.Enabled = enabled;
            }

            void RefreshUi()
            {
                var runInfo = game is null
                    ? string.Empty
                    : $"   Goal: {game.TargetBalance}   Spins: {game.SpinsLeft}";
                infoLabel.Text = $"Balance: {state.Balance}   Bet: {state.Bet}   Last win: {state.LastWin}{runInfo}";
                statusLabel.Text = state.Status;

                if (_playback.IsPlaying)
                {
                    boardDisplay.SetFrame(BuildFrameFromPlayback());
                }
                else
                {
                    boardDisplay.SetBoard(state.Board ?? game?.LastBoard);
                }

                if (state.Messages.Count > 0)
                {
                    logView.Text = string.Join(Environment.NewLine, state.Messages);
                }
            }

            void Refresh()
            {
                if (infoLabel is null || statusLabel is null || boardDisplay is null || logView is null)
                {
                    return;
                }

                RefreshUi();
            }

            void QueueAnimationFrame()
            {
                Application.MainLoop.AddTimeout(TimeSpan.FromMilliseconds(33), _ =>
                {
                    if (!_playback.IsPlaying)
                    {
                        SetControlsEnabled(game?.IsGameOver != true);
                        Refresh();
                        return false;
                    }

                    boardDisplay.SetFrame(BuildFrameFromPlayback());
                    boardView.SetNeedsDisplay();
                    statusLabel.Text = "Spinning...";
                    _playback.Update(FrameSeconds);
                    QueueAnimationFrame();
                    return false;
                });
            }

            var uiObserver = new TerminalUiObserver(state, Refresh);
            game = CreateGame(uiObserver);

            var top = Application.Top;
            var window = new Window("Pirate Parrots")
            {
                X = 0,
                Y = 0,
                Width = Dim.Fill(),
                Height = Dim.Fill()
            };

            infoLabel = new Label("")
            {
                X = 1,
                Y = 1,
                Width = Dim.Fill() - 2
            };

            if (_useChafa && !ChafaCli.IsAvailable())
            {
                state.Status = "Chafa not found — using pixel fallback. Install: scoop install chafa";
            }

            boardView = new GameBoardView(_sprites)
            {
                X = 1,
                Y = TerminalLayoutPlan.TopRows,
                Width = Dim.Fill() - 2,
                Height = Dim.Fill() - layout.BottomPanelRows - TerminalLayoutPlan.TopRows
            };

            boardDisplay = (IBoardView)boardView;

            logView = new TextView
            {
                X = 1,
                Y = Pos.Bottom(boardView),
                Width = Dim.Fill() - 2,
                Height = layout.LogHeight,
                ReadOnly = true,
                Text = "Spin log"
            };

            statusLabel = new Label(state.Status)
            {
                X = 1,
                Y = Pos.Bottom(logView),
                Width = Dim.Fill() - 2
            };

            spinButton = new Button("Spin")
            {
                X = 1,
                Y = Pos.Bottom(statusLabel)
            };
            spinButton.Clicked += () => ExecuteSpin(game, state, Refresh, SetControlsEnabled, QueueAnimationFrame);

            betDownButton = new Button("Bet -")
            {
                X = Pos.Right(spinButton) + 1,
                Y = Pos.Y(spinButton)
            };
            betDownButton.Clicked += () => ChangeBet(game, -5, state, Refresh, _playback.IsPlaying);

            betUpButton = new Button("Bet +")
            {
                X = Pos.Right(betDownButton) + 1,
                Y = Pos.Y(spinButton)
            };
            betUpButton.Clicked += () => ChangeBet(game, 5, state, Refresh, _playback.IsPlaying);

            var balanceButton = new Button("Balance")
            {
                X = Pos.Right(betUpButton) + 1,
                Y = Pos.Y(spinButton)
            };
            balanceButton.Clicked += () =>
            {
                if (_playback.IsPlaying)
                {
                    return;
                }

                state.Status = $"Balance: {game.Balance}, Bet: {game.CurrentBet}, Spins: {game.SpinsLeft}, Goal: {game.TargetBalance}";
                Refresh();
            };

            var rulesButton = new Button("Rules")
            {
                X = Pos.Right(balanceButton) + 1,
                Y = Pos.Y(spinButton)
            };
            rulesButton.Clicked += () => ShowRules(game);

            var quitButton = new Button("Quit")
            {
                X = Pos.Right(rulesButton) + 1,
                Y = Pos.Y(spinButton)
            };
            quitButton.Clicked += () => Application.RequestStop();

            window.Add(infoLabel, boardView, logView, statusLabel, spinButton, betDownButton, betUpButton, balanceButton, rulesButton, quitButton);
            top.Add(window);

            uiObserver.SyncFromGame(game);
            if (game.LastBoard is not null)
            {
                state.Board = game.LastBoard;
            }

            RefreshUi();
            Application.Run();
        }
        finally
        {
            Application.Shutdown();
        }
    }

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

    private static SlotMachine CreateGame(TerminalUiObserver uiObserver) =>
        TerminalGameBootstrap.CreateGame(uiObserver);

    private void ExecuteSpin(
        SlotMachine game,
        TerminalUiState state,
        Action refresh,
        Action<bool> setControlsEnabled,
        Action queueAnimationFrame)
    {
        if (_playback.IsPlaying)
        {
            return;
        }

        if (!game.CanSpin())
        {
            state.Status = game.IsGameOver ? game.RunMessage : "Cannot spin: check balance and bet.";
            refresh();
            return;
        }

        var previous = game.LastBoard;
        var session = game.BeginAnimatedSpin();
        if (session is null)
        {
            state.Status = "Spin failed.";
            refresh();
            return;
        }

        state.Messages = session.Messages;
        state.Status = "Spinning...";
        setControlsEnabled(false);
        refresh();

        _playback.Start(session, previous, fallOutPrevious: previous is not null);
        queueAnimationFrame();
    }

    private static void ChangeBet(SlotMachine game, int delta, TerminalUiState state, Action refresh, bool isAnimating)
    {
        if (isAnimating)
        {
            return;
        }

        if (game.IsGameOver)
        {
            state.Status = game.RunMessage;
            refresh();
            return;
        }

        var settings = GameSettings.Instance;
        var next = Math.Clamp(game.CurrentBet + delta, settings.MinBet, settings.MaxBet);
        game.SetBet(next);
        refresh();
    }

    private static void ShowRules(SlotMachine game)
    {
        MessageBox.Query(50, 15, "Rules", game.GetRulesText(), "OK");
    }
}
