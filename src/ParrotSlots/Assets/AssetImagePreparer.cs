using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

namespace ParrotSlots.Assets;

internal static class AssetImagePreparer
{
    public const byte AlphaThreshold = 30;

    public static Image<Rgba32> LoadCroppedCellImage(string path, int cellSize)
    {
        var image = Image.Load<Rgba32>(path);
        CropToContent(image);
        image.Mutate(ctx => ctx.Resize(new ResizeOptions
        {
            Size = new Size(cellSize, cellSize),
            Mode = ResizeMode.Stretch,
            Sampler = KnownResamplers.NearestNeighbor
        }));
        return image;
    }

    public static void CropToContent(Image<Rgba32> image)
    {
        var bounds = FindContentBounds(image);
        if (bounds.Width <= 0 || bounds.Height <= 0)
        {
            return;
        }

        image.Mutate(ctx => ctx.Crop(bounds));
    }

    public static Rectangle FindContentBounds(Image<Rgba32> source)
    {
        var minX = source.Width;
        var minY = source.Height;
        var maxX = -1;
        var maxY = -1;

        for (var y = 0; y < source.Height; y++)
        {
            for (var x = 0; x < source.Width; x++)
            {
                if (source[x, y].A < AlphaThreshold)
                {
                    continue;
                }

                minX = Math.Min(minX, x);
                minY = Math.Min(minY, y);
                maxX = Math.Max(maxX, x);
                maxY = Math.Max(maxY, y);
            }
        }

        if (maxX < minX || maxY < minY)
        {
            return new Rectangle(0, 0, 0, 0);
        }

        return Rectangle.FromLTRB(minX, minY, maxX + 1, maxY + 1);
    }
}
