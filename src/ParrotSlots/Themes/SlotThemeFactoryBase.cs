using ParrotSlots.Core;

namespace ParrotSlots.Themes;

public abstract class SlotThemeFactoryBase : ISlotThemeFactory
{
    public abstract string ThemeName { get; }

    public abstract ISymbolSet CreateSymbolSet();
    public abstract IPayTable CreatePayTable();
    public abstract IBoardGenerator CreateBoardGenerator();

    protected static Dictionary<(ParrotColor Color, int Level), double> CreateDefaultCrystalMultipliers() => new()
    {
        [(ParrotColor.Red, 1)] = 0.665,
        [(ParrotColor.Red, 2)] = 1.6625,
        [(ParrotColor.Red, 3)] = 3.325,
        [(ParrotColor.Red, 4)] = 4.9875,
        [(ParrotColor.Red, 5)] = 16.625,
        [(ParrotColor.Red, 6)] = 49.875,
        [(ParrotColor.Red, 7)] = 199.5,
        [(ParrotColor.Purple, 1)] = 0.665,
        [(ParrotColor.Purple, 2)] = 1.33,
        [(ParrotColor.Purple, 3)] = 2.66,
        [(ParrotColor.Purple, 4)] = 3.99,
        [(ParrotColor.Purple, 5)] = 10.64,
        [(ParrotColor.Purple, 6)] = 33.25,
        [(ParrotColor.Purple, 7)] = 99.75,
        [(ParrotColor.Green, 1)] = 0.3325,
        [(ParrotColor.Green, 2)] = 0.9975,
        [(ParrotColor.Green, 3)] = 1.995,
        [(ParrotColor.Green, 4)] = 2.9925,
        [(ParrotColor.Green, 5)] = 7.98,
        [(ParrotColor.Green, 6)] = 23.94,
        [(ParrotColor.Green, 7)] = 66.5,
        [(ParrotColor.Blue, 1)] = 0.3325,
        [(ParrotColor.Blue, 2)] = 0.665,
        [(ParrotColor.Blue, 3)] = 1.33,
        [(ParrotColor.Blue, 4)] = 1.995,
        [(ParrotColor.Blue, 5)] = 5.32,
        [(ParrotColor.Blue, 6)] = 16.625,
        [(ParrotColor.Blue, 7)] = 49.875
    };

    protected static SymbolSet CreateDefaultSymbolSet(string themeName)
    {
        var parrots = new Dictionary<ParrotColor, string>
        {
            [ParrotColor.Red] = "🦜R",
            [ParrotColor.Purple] = "🦜P",
            [ParrotColor.Green] = "🦜G",
            [ParrotColor.Blue] = "🦜B"
        };

        var crystals = new Dictionary<(ParrotColor, int), string>
        {
            [(ParrotColor.Red, 1)] = "🔴1",
            [(ParrotColor.Red, 2)] = "🔴2",
            [(ParrotColor.Red, 3)] = "🔴3",
            [(ParrotColor.Purple, 1)] = "🟣1",
            [(ParrotColor.Purple, 2)] = "🟣2",
            [(ParrotColor.Purple, 3)] = "🟣3",
            [(ParrotColor.Green, 1)] = "🟢1",
            [(ParrotColor.Green, 2)] = "🟢2",
            [(ParrotColor.Green, 3)] = "🟢3",
            [(ParrotColor.Blue, 1)] = "🔵1",
            [(ParrotColor.Blue, 2)] = "🔵2",
            [(ParrotColor.Blue, 3)] = "🔵3"
        };

        for (var level = 4; level <= 7; level++)
        {
            crystals[(ParrotColor.Red, level)] = $"🔴{level}";
            crystals[(ParrotColor.Purple, level)] = $"🟣{level}";
            crystals[(ParrotColor.Green, level)] = $"🟢{level}";
            crystals[(ParrotColor.Blue, level)] = $"🔵{level}";
        }

        return new SymbolSet(themeName, parrots, crystals);
    }
}
