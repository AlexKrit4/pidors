using ParrotSlots.Assets;
using ParrotSlots.Graphics;

namespace ParrotSlots.Terminal;

public sealed record TerminalLayoutPlan(
    int MaxSpritePixelSize,
    int LogHeight,
    int BottomPanelRows)
{
    public const int TopRows = 2;
    public const int SideMargin = 2;
    private const int SlotPadding = 1;

    public static TerminalLayoutPlan Fit(int terminalWidth, int terminalHeight)
    {
        const int logHeight = 4;
        const int statusRows = 1;
        const int buttonRows = 1;
        const int spacingRows = 1;
        var bottomPanelRows = logHeight + statusRows + buttonRows + spacingRows;
        var boardAreaRows = Math.Max(10, terminalHeight - TopRows - bottomPanelRows);
        var boardAreaCols = Math.Max(42, terminalWidth - SideMargin);

        var maxPixelSize = ComputeMaxPixelSize(boardAreaCols, boardAreaRows);
        return new TerminalLayoutPlan(maxPixelSize, logHeight, bottomPanelRows);
    }

    public static int ComputeMaxPixelSize(int boardAreaCols, int boardAreaRows)
    {
        var maxFromWidth = boardAreaCols / GameConstants.GridCols - SlotPadding * 2;
        var terminalRowsPerCell = boardAreaRows / GameConstants.GridRows;
        var maxFromHeight = Math.Max(4, terminalRowsPerCell * 2 - SlotPadding * 2);

        return Math.Clamp(Math.Min(maxFromWidth, maxFromHeight), 8, CellSprite.MaxPixelSize);
    }

    public static (int Width, int Height) BoardViewSize(SpriteCache sprites, int displayScale = 1)
    {
        var rowStride = TerminalDisplayConstants.CellTerminalHeight(sprites.LayoutSlotHeight);
        var width = GameConstants.GridCols * (sprites.LayoutSlotWidth + TerminalDisplayConstants.CellGap) * displayScale;
        var height = GameConstants.GridRows * rowStride * displayScale;
        return (width, height);
    }

    public static int ComputeDisplayScale(SpriteCache sprites, int boundsWidth, int boundsHeight)
    {
        var rowStride = TerminalDisplayConstants.CellTerminalHeight(sprites.LayoutSlotHeight);
        var nativeWidth = GameConstants.GridCols * (sprites.LayoutSlotWidth + TerminalDisplayConstants.CellGap);
        var nativeHeight = GameConstants.GridRows * rowStride;

        if (nativeWidth <= 0 || nativeHeight <= 0)
        {
            return 1;
        }

        var scale = 1;
        while (scale < 4 &&
               nativeWidth * (scale + 1) <= boundsWidth &&
               nativeHeight * (scale + 1) <= boundsHeight)
        {
            scale++;
        }

        return scale;
    }
}

public static class TerminalSizeReader
{
    public static (int Width, int Height) Read()
    {
        try
        {
            var width = Console.WindowWidth;
            var height = Console.WindowHeight;
            if (width > 0 && height > 0)
            {
                return (width, height);
            }
        }
        catch (IOException)
        {
        }
        catch (PlatformNotSupportedException)
        {
        }

        return (120, 40);
    }
}
