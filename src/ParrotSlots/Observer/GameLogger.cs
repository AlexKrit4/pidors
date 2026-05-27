namespace ParrotSlots.Observer;

public sealed class GameLogger : IGameObserver
{
    private readonly List<string> _entries = [];
    private readonly TextWriter? _output;

    public GameLogger(TextWriter? output = null) => _output = output;

    public IReadOnlyList<string> Entries => _entries;

    public void OnGameEvent(GameEvent gameEvent)
    {
        var entry = $"[{DateTime.Now:HH:mm:ss}] {gameEvent.Type}: {gameEvent.Message}";
        _entries.Add(entry);
        _output?.WriteLine(entry);
    }
}
