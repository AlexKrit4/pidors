using ParrotSlots.Themes;

namespace ParrotSlots.Tests;

public class ThemeFactoryTests
{
    [Fact]
    public void PirateFactory_CreatesConsistentThemeFamily()
    {
        var factory = new PirateParrotThemeFactory();

        var symbols = factory.CreateSymbolSet();
        var payTable = factory.CreatePayTable();
        var boardGenerator = factory.CreateBoardGenerator();

        Assert.Equal(factory.ThemeName, symbols.ThemeName);
        Assert.Equal(factory.ThemeName, payTable.ThemeName);
        Assert.Equal(factory.ThemeName, boardGenerator.ThemeName);
    }

    [Fact]
    public void JungleFactory_CreatesConsistentThemeFamily()
    {
        var factory = new JungleParrotThemeFactory();
        Assert.Equal(factory.ThemeName, factory.CreateSymbolSet().ThemeName);
        Assert.Equal(factory.ThemeName, factory.CreatePayTable().ThemeName);
    }
}
