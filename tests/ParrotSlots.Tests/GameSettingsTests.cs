using ParrotSlots.Settings;

namespace ParrotSlots.Tests;

public class GameSettingsTests
{
    [Fact]
    public void Instance_AlwaysReturnsSameObject()
    {
        var first = GameSettings.Instance;
        var second = GameSettings.Instance;

        Assert.Same(first, second);
        Assert.Equal(6, first.ColCount);
        Assert.Equal(7, first.RowCount);
        Assert.Equal(4, first.ParrotCount);
        Assert.Equal(1000, first.StartingBalance);
    }
}
