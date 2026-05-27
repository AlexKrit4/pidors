using SixLabors.ImageSharp.PixelFormats;
using TuiColor = Terminal.Gui.Color;

namespace ParrotSlots.Assets;

internal static class TerminalColorMapper
{
    private static readonly (TuiColor Color, byte R, byte G, byte B)[] Palette =
    [
        (TuiColor.Black, 0, 0, 0),
        (TuiColor.Blue, 0, 0, 170),
        (TuiColor.Green, 0, 170, 0),
        (TuiColor.Cyan, 0, 170, 170),
        (TuiColor.Red, 170, 0, 0),
        (TuiColor.Magenta, 170, 0, 170),
        (TuiColor.Brown, 170, 85, 0),
        (TuiColor.Gray, 170, 170, 170),
        (TuiColor.DarkGray, 85, 85, 85),
        (TuiColor.BrightBlue, 85, 85, 255),
        (TuiColor.BrightGreen, 85, 255, 85),
        (TuiColor.BrightCyan, 85, 255, 255),
        (TuiColor.BrightRed, 255, 85, 85),
        (TuiColor.BrightMagenta, 255, 85, 255),
        (TuiColor.White, 255, 255, 255),
        (TuiColor.BrightYellow, 255, 255, 85)
    ];

    public static TuiColor FromRgb(byte r, byte g, byte b)
    {
        var best = TuiColor.White;
        var bestDistance = int.MaxValue;

        foreach (var (color, pr, pg, pb) in Palette)
        {
            var distance = (r - pr) * (r - pr) + (g - pg) * (g - pg) + (b - pb) * (b - pb);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = color;
            }
        }

        return best;
    }

    public static TuiColor FromRgba(Rgba32 pixel, TuiColor fallback) =>
        pixel.A >= 30 ? FromRgb(pixel.R, pixel.G, pixel.B) : fallback;
}
