using ParrotSlots.Core;

namespace ParrotSlots.Themes;

public sealed class PirateParrotThemeFactory : SlotThemeFactoryBase
{
    public override string ThemeName => "Pirate Parrots";

    public override ISymbolSet CreateSymbolSet() => CreateDefaultSymbolSet(ThemeName);

    public override IPayTable CreatePayTable() =>
        new PayTable(ThemeName, CreateDefaultCrystalMultipliers());

    public override IBoardGenerator CreateBoardGenerator()
    {
        var symbols = CreateSymbolSet();
        return new BoardGenerator(ThemeName, symbols);
    }
}
