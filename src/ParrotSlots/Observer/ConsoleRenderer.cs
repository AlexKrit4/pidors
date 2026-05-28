namespace ParrotSlots.Observer;

public sealed class ConsoleRenderer : IGameObserver
{
    private readonly TextWriter _output;

    public ConsoleRenderer(TextWriter? output = null) => _output = output ?? Console.Out;

    public void OnGameEvent(GameEvent gameEvent)
    {
        switch (gameEvent.Type)
        {
            case GameEventType.SpinStarted:
                _output.WriteLine($">> {gameEvent.Message}");
                break;
            case GameEventType.SpinFinished when gameEvent.SpinResult is not null:
                _output.WriteLine(gameEvent.SpinResult.Board.ToString());
                _output.WriteLine($">> Win: {gameEvent.SpinResult.WinAmount} | Net: {gameEvent.SpinResult.NetResult}");
                foreach (var message in gameEvent.SpinResult.Messages)
                {
                    _output.WriteLine($"   - {message}");
                }

                break;
            case GameEventType.BalanceChanged:
                _output.WriteLine($">> {gameEvent.Message}");
                break;
            case GameEventType.ModifierTriggered:
                _output.WriteLine($">> Modifier: {gameEvent.Message}");
                break;
            case GameEventType.CommandFailed:
                _output.WriteLine($">> ERROR: {gameEvent.Message}");
                break;
            case GameEventType.GameOver:
                _output.WriteLine($">> {gameEvent.Message}");
                break;
        }
    }
}
