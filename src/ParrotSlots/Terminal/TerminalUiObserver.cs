using ParrotSlots.Core;
using ParrotSlots.Observer;

namespace ParrotSlots.Terminal;

public sealed class TerminalUiState
{
    public GameBoard? Board { get; set; }
    public int Balance { get; set; }
    public int Bet { get; set; }
    public int LastWin { get; set; }
    public IReadOnlyList<string> Messages { get; set; } = [];
    public string Status { get; set; } = "Press Spin to play.";
}

public sealed class TerminalUiObserver : IGameObserver
{
    private readonly TerminalUiState _state;
    private readonly Action _refresh;

    public TerminalUiObserver(TerminalUiState state, Action refresh)
    {
        _state = state;
        _refresh = refresh;
    }

    public void OnGameEvent(GameEvent gameEvent)
    {
        switch (gameEvent.Type)
        {
            case GameEventType.SpinStarted:
                _state.Status = gameEvent.Message;
                break;
            case GameEventType.SpinFinished when gameEvent.SpinResult is not null:
                _state.Board = gameEvent.SpinResult.Board;
                _state.LastWin = gameEvent.SpinResult.WinAmount;
                _state.Messages = gameEvent.SpinResult.Messages;
                _state.Status = $"Win: {gameEvent.SpinResult.WinAmount} | Net: {gameEvent.SpinResult.NetResult}";
                break;
            case GameEventType.BalanceChanged:
                _state.Balance = gameEvent.Balance;
                _state.Bet = gameEvent.Bet;
                _state.Status = gameEvent.Message;
                break;
            case GameEventType.CommandFailed:
                _state.Status = $"ERROR: {gameEvent.Message}";
                break;
        }

        _refresh();
    }

    public void SyncFromGame(SlotMachine game)
    {
        _state.Balance = game.Balance;
        _state.Bet = game.CurrentBet;
        _refresh();
    }
}
