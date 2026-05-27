namespace ParrotSlots.Core;

public sealed class SymbolSet : ISymbolSet
{
    private readonly Dictionary<ParrotColor, string> _parrots;
    private readonly Dictionary<(ParrotColor Color, int Level), string> _crystals;

    public SymbolSet(
        string themeName,
        Dictionary<ParrotColor, string> parrots,
        Dictionary<(ParrotColor, int), string> crystals)
    {
        ThemeName = themeName;
        _parrots = parrots;
        _crystals = crystals;
    }

    public string ThemeName { get; }

    public string GetParrotDisplay(ParrotColor color) => _parrots[color];

    public string GetCrystalDisplay(ParrotColor color, int level) =>
        _crystals.TryGetValue((color, level), out var display)
            ? display
            : level.ToString();
}
