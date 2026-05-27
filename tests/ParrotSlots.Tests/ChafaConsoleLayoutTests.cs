using ParrotSlots.Graphics;
using ParrotSlots.Terminal;

namespace ParrotSlots.Tests;

public class ChafaConsoleLayoutTests
{
    [Fact]
    public void Measure_KeepsBoardWidthStableWhenOnlyTerminalWidthGrows()
    {
        var normal = ChafaConsoleLayout.Measure(120, 40);
        var wide = ChafaConsoleLayout.Measure(200, 40);

        Assert.Equal(normal.BoardWidth, wide.BoardWidth);
        Assert.Equal(normal.BoardHeight, wide.BoardHeight);
        Assert.True(wide.BoardLeft > normal.BoardLeft);
    }

    [Fact]
    public void Measure_CentersBoardWhenTerminalIsWiderThanBoard()
    {
        var layout = ChafaConsoleLayout.Measure(160, 40);

        Assert.Equal((layout.Width - layout.BoardWidth) / 2, layout.BoardLeft);
        Assert.True(layout.BoardLeft > 0);
    }

    [Fact]
    public void MeasureBoardSize_UsesSquareCellTerminalRatio()
    {
        var (width, height) = ChafaConsoleLayout.MeasureBoardSize(160, 40);
        var expectedWidth = height * GameConstants.GridCols * 3 / GameConstants.GridRows;

        Assert.Equal(expectedWidth, width);
        Assert.Equal(0, width % (GameConstants.GridCols * 3));
        Assert.Equal(0, height % GameConstants.GridRows);
        Assert.Equal(width / (GameConstants.GridCols * 3), height / GameConstants.GridRows);
        Assert.True(width <= 160);
        Assert.True(height <= 40);
    }

    [Fact]
    public void MeasureBoardSize_ShrinksHeightWhenWidthIsTheLimitingAxis()
    {
        var (width, height) = ChafaConsoleLayout.MeasureBoardSize(40, 80);

        Assert.True(width <= 40);
        Assert.True(height < 80);
        Assert.Equal(height * GameConstants.GridCols * 3 / GameConstants.GridRows, width);
    }
}
