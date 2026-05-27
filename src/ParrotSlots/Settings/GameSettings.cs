namespace ParrotSlots.Settings;

public sealed class GameSettings
{
    private static readonly Lazy<GameSettings> LazyInstance = new(() => new GameSettings());

    private GameSettings()
    {
    }

    public static GameSettings Instance => LazyInstance.Value;

    public int ColCount => 6;
    public int RowCount => 7;
    public int ParrotCount => 4;
    public int MaxCrystalLevel => 7;
    public int StartingBalance => 1000;
    public int MinBet => 1;
    public int MaxBet => 100;
    public int DefaultBet => 10;
}
