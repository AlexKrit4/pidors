using ParrotSlots.Assets;
using SixLabors.ImageSharp.PixelFormats;
using Terminal.Gui;
using TuiAttribute = Terminal.Gui.Attribute;
using TuiColor = Terminal.Gui.Color;

namespace ParrotSlots.Terminal;

public sealed class TerminalPixelArtWriter
{
    private const byte AlphaThreshold = 30;
    private static readonly TuiColor BackdropColor = TerminalColorMapper.FromRgb(0, 0, 170);

    public void DrawSprite(
        View view,
        Rect bounds,
        CellSprite sprite,
        float terminalColumn,
        float terminalLine,
        int slotWidth,
        int slotHeight,
        int displayScale,
        int originX,
        int originY,
        Rgba32 backdrop)
    {
        if (!sprite.HasVisiblePixels() || displayScale < 1)
        {
            return;
        }

        var slotPixelWidth = (slotWidth + TerminalDisplayConstants.CellGap) * displayScale;
        var slotPixelHeight = TerminalDisplayConstants.CellTerminalHeight(slotHeight) * displayScale;
        var slotX = originX + (int)(terminalColumn * slotPixelWidth);
        var slotY = originY + (int)Math.Round(terminalLine * displayScale);
        var slotTerminalRows = (slotHeight + 1) / 2;
        var spriteTerminalRows = (sprite.Height + 1) / 2;
        var drawX = slotX + Math.Max(0, (slotWidth - sprite.Width) / 2) * displayScale;
        var drawY = slotY + Math.Max(0, (slotTerminalRows - spriteTerminalRows) / 2) * displayScale;
        var backdropColor = TerminalColorMapper.FromRgba(backdrop, BackdropColor);

        var terminalRows = (sprite.Height + 1) / 2;
        for (var ty = 0; ty < terminalRows; ty++)
        {
            for (var sy = 0; sy < displayScale; sy++)
            {
                var y = drawY + ty * displayScale + sy;
                if (y < 0 || y >= bounds.Height)
                {
                    continue;
                }

                TuiColor? currentFg = null;
                TuiColor? currentBg = null;

                for (var tx = 0; tx < sprite.Width; tx++)
                {
                    var topRow = ty * 2;
                    var bottomRow = ty * 2 + 1;
                    var top = topRow < sprite.Height
                        ? ResolvePixel(sprite.GetPixel(tx, topRow), backdrop)
                        : backdrop;
                    var bottom = bottomRow < sprite.Height
                        ? ResolvePixel(sprite.GetPixel(tx, bottomRow), backdrop)
                        : backdrop;

                    char ch;
                    TuiColor fg;
                    TuiColor bg;

                    if (!IsVisible(top) && !IsVisible(bottom))
                    {
                        continue;
                    }

                    if (IsVisible(top) && IsVisible(bottom))
                    {
                        ch = '▀';
                        fg = TerminalColorMapper.FromRgba(top, backdropColor);
                        bg = TerminalColorMapper.FromRgba(bottom, backdropColor);
                    }
                    else if (IsVisible(top))
                    {
                        ch = '▀';
                        fg = TerminalColorMapper.FromRgba(top, backdropColor);
                        bg = backdropColor;
                    }
                    else
                    {
                        ch = '▄';
                        fg = TerminalColorMapper.FromRgba(bottom, backdropColor);
                        bg = backdropColor;
                    }

                    if (currentFg != fg || currentBg != bg)
                    {
                        Application.Driver.SetAttribute(new TuiAttribute(fg, bg));
                        currentFg = fg;
                        currentBg = bg;
                    }

                    for (var sx = 0; sx < displayScale; sx++)
                    {
                        var x = drawX + tx * displayScale + sx;
                        if (x < 0 || x >= bounds.Width)
                        {
                            continue;
                        }

                        view.Move(x, y);
                        Application.Driver.AddRune(new Rune(ch));
                    }
                }
            }
        }
    }

    private static Rgba32 ResolvePixel(Rgba32 pixel, Rgba32 backdrop) =>
        IsVisible(pixel) ? pixel : backdrop;

    private static bool IsVisible(Rgba32 pixel) => pixel.A >= AlphaThreshold;
}

internal static class TerminalDisplayConstants
{
    public const int CellGap = 0;
    public const float RaylibCellSize = 70f;

    public static int CellTerminalHeight(int slotPixelHeight) =>
        slotPixelHeight / 2 + CellGap;
}
