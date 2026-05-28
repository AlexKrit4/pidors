using SixLabors.ImageSharp.PixelFormats;

namespace ParrotSlots.Assets;

public sealed class CellSprite
{
    public const int MaxPixelSize = 48;

    public required Rgba32[] Pixels { get; init; }
    public required int Width { get; init; }
    public required int Height { get; init; }

    public static CellSprite Empty() =>
        new()
        {
            Pixels = [],
            Width = 0,
            Height = 0
        };

    public Rgba32 GetPixel(int x, int y) => Pixels[(y * Width) + x];

    public bool HasVisiblePixels(byte alphaThreshold = 30)
    {
        foreach (var pixel in Pixels)
        {
            if (pixel.A >= alphaThreshold)
            {
                return true;
            }
        }

        return false;
    }
}
