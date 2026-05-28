using ParrotSlots.Builder;
using ParrotSlots.Core;
using ParrotSlots.Settings;
using ParrotSlots.Wallet;
using Raylib_cs;

namespace ParrotSlots.Graphics;

public sealed class RaylibGameApplication : IDisposable
{
    private readonly TextureCatalog _textures = new();
    private readonly BoardRenderer _boardRenderer;
    private readonly HudRenderer _hud = new();
    private readonly SpinPlaybackController _playback = new();
    private SlotMachine? _game;
    private readonly List<string> _log = [];
    private string _status = "Click SPIN to play.";
    private bool _wasPlaying;
    private int _lastSpinWin;

    public RaylibGameApplication()
    {
        _boardRenderer = new BoardRenderer(_textures);
    }

    public void Run()
    {
        Raylib.InitWindow(GameConstants.WindowWidth, GameConstants.WindowHeight, "Pirate Parrots");
        Raylib.SetTargetFPS(60);

        _textures.LoadAll();
        _game = new DefaultGameDirector().CreateStandardGame(output: TextWriter.Null);

        while (!Raylib.WindowShouldClose())
        {
            if (!_playback.IsPlaying)
            {
                HandleInput();
            }

            if (_wasPlaying && !_playback.IsPlaying && _game is not null)
            {
                _status = _game.IsGameOver
                    ? _game.RunMessage
                    : _lastSpinWin > 0
                        ? $"Win: {_lastSpinWin}. Balance: {_game.Balance}, Bet: {_game.CurrentBet}"
                        : $"No win. Balance: {_game.Balance}, Bet: {_game.CurrentBet}";
            }

            _wasPlaying = _playback.IsPlaying;

            Raylib.BeginDrawing();
            Raylib.ClearBackground(new Color(20, 24, 40, 255));

            if (_textures.Background.Id != 0)
            {
                Raylib.DrawTexturePro(
                    _textures.Background,
                    new Rectangle(0, 0, _textures.Background.Width, _textures.Background.Height),
                    new Rectangle(0, 0, GameConstants.WindowWidth, GameConstants.WindowHeight),
                    System.Numerics.Vector2.Zero,
                    0f,
                    Color.White);
            }

            _boardRenderer.Draw(
                _playback.DisplayBoard,
                _playback.CellOffsetY,
                _playback.MovingParrotFrom,
                _playback.MovingParrotTo,
                _playback.MovingParrotT,
                _playback.MovingParrotColor);

            if (_game is not null)
            {
                _hud.Draw(_game, _status, _log);
            }

            Raylib.EndDrawing();

            if (_playback.IsPlaying)
            {
                _playback.Update(Raylib.GetFrameTime());
            }
        }

        Raylib.CloseWindow();
    }

    private void HandleInput()
    {
        if (_game is null)
        {
            return;
        }

        if (_hud.IsQuitClicked())
        {
            Raylib.CloseWindow();
            return;
        }

        if (_hud.IsBetDownClicked())
        {
            if (_game.IsGameOver)
            {
                _status = _game.RunMessage;
                return;
            }

            var next = Math.Clamp(_game.CurrentBet - 5, GameSettings.Instance.MinBet, GameSettings.Instance.MaxBet);
            _game.SetBet(next);
            _status = $"Bet set to {_game.CurrentBet}.";
        }

        if (_hud.IsBetUpClicked())
        {
            if (_game.IsGameOver)
            {
                _status = _game.RunMessage;
                return;
            }

            var next = Math.Clamp(_game.CurrentBet + 5, GameSettings.Instance.MinBet, GameSettings.Instance.MaxBet);
            _game.SetBet(next);
            _status = $"Bet set to {_game.CurrentBet}.";
        }

        if (_hud.IsSpinClicked())
        {
            if (!_game.CanSpin())
            {
                _status = _game.IsGameOver ? _game.RunMessage : "Cannot spin: check balance and bet.";
                return;
            }

            var previous = _game.LastBoard;
            var session = _game.BeginAnimatedSpin();
            if (session is null)
            {
                _status = "Spin failed.";
                return;
            }

            _log.Clear();
            _log.AddRange(session.Messages);
            _lastSpinWin = session.Plan.TotalWin;
            _status = "Spinning...";
            _playback.Start(session, previous, fallOutPrevious: previous is not null);
        }
    }

    public void Dispose() => _textures.Dispose();
}
