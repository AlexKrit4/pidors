namespace ParrotSlots.Observer;

public sealed class StatisticsTracker : IGameObserver
{
    public int SpinCount { get; private set; }
    public int TotalWagered { get; private set; }
    public int TotalWon { get; private set; }
    public int ModifierCount { get; private set; }
    public int FailedCommands { get; private set; }

    public void OnGameEvent(GameEvent gameEvent)
    {
        switch (gameEvent.Type)
        {
            case GameEventType.SpinFinished when gameEvent.SpinResult is not null:
                SpinCount++;
                TotalWagered += gameEvent.SpinResult.Bet;
                TotalWon += gameEvent.SpinResult.WinAmount;
                break;
            case GameEventType.ModifierTriggered:
                ModifierCount++;
                break;
            case GameEventType.CommandFailed:
                FailedCommands++;
                break;
        }
    }

    public string Summary =>
        $"Spins: {SpinCount}, Wagered: {TotalWagered}, Won: {TotalWon}, Modifiers: {ModifierCount}, Errors: {FailedCommands}";
}
