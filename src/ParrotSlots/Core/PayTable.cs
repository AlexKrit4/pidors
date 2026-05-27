namespace ParrotSlots.Core;

public sealed class PayTable : IPayTable
{
    private readonly Dictionary<(ParrotColor Color, int Level), double> _multipliers;

    public PayTable(string themeName, Dictionary<(ParrotColor, int), double> multipliers)
    {
        ThemeName = themeName;
        _multipliers = multipliers;
    }

    public string ThemeName { get; }

    public int GetCrystalPayout(ParrotColor color, int level, int bet)
    {
        if (!_multipliers.TryGetValue((color, level), out var multiplier))
        {
            return 0;
        }

        return Math.Max(1, (int)Math.Round(multiplier * bet));
    }
}
