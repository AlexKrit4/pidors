using ParrotSlots.Core;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

namespace ParrotSlots.Assets;

public sealed class SpriteCache
{
    public static readonly Rgba32 Backdrop = new(0, 0, 170, 255);
    private const int SlotPadding = 1;

    private readonly ImageCatalog _catalog;
    private readonly Dictionary<string, CellSprite> _cache = new(StringComparer.OrdinalIgnoreCase);
    private int _maxPixelSize;

    public SpriteCache(ImageCatalog catalog, int maxPixelSize = CellSprite.MaxPixelSize)
    {
        _catalog = catalog;
        _maxPixelSize = Math.Clamp(maxPixelSize, 10, CellSprite.MaxPixelSize);
        WarmLayout();
    }

    public int LayoutSlotWidth { get; private set; } = CellSprite.MaxPixelSize;
    public int LayoutSlotHeight { get; private set; } = CellSprite.MaxPixelSize;

    public void SetMaxPixelSize(int maxPixelSize)
    {
        var target = Math.Clamp(maxPixelSize, 8, CellSprite.MaxPixelSize);
        if (target == _maxPixelSize)
        {
            return;
        }

        _maxPixelSize = target;
        _cache.Clear();
        WarmLayout();
    }

    public CellSprite GetCellSprite(Cell cell)
    {
        if (cell.IsEmpty)
        {
            return CellSprite.Empty();
        }

        if (cell.IsParrot)
        {
            return Load(_catalog.GetParrotPath(cell.Color));
        }

        return Load(_catalog.GetCrystalPath(cell.Color, cell.Level));
    }

    private void WarmLayout()
    {
        var maxWidth = 0;
        var maxHeight = 0;

        foreach (var path in _catalog.AllAssetPaths())
        {
            if (!File.Exists(path))
            {
                continue;
            }

            var sprite = Load(path);
            maxWidth = Math.Max(maxWidth, sprite.Width);
            maxHeight = Math.Max(maxHeight, sprite.Height);
        }

        if (maxWidth > 0)
        {
            LayoutSlotWidth = maxWidth + SlotPadding * 2;
            LayoutSlotHeight = maxHeight + SlotPadding * 2;
        }
    }

    private CellSprite Load(string path)
    {
        if (_cache.TryGetValue(path, out var cached))
        {
            return cached;
        }

        if (!File.Exists(path))
        {
            var fallback = CreateLabelSprite(Path.GetFileNameWithoutExtension(path));
            _cache[path] = fallback;
            return fallback;
        }

        using var image = Image.Load<Rgba32>(path);
        var sprite = Rasterize(image, _maxPixelSize);
        _cache[path] = sprite;
        return sprite;
    }

    private CellSprite CreateLabelSprite(string label)
    {
        var width = Math.Min(label.Length + 2, _maxPixelSize);
        var height = 8;
        var pixels = new Rgba32[width * height];
        var text = label.Length > width - 2 ? label[..(width - 2)] : label;
        var startX = (width - text.Length) / 2;
        var y = height / 2;

        for (var i = 0; i < text.Length; i++)
        {
            pixels[(y * width) + startX + i] = new Rgba32(255, 255, 85, 255);
        }

        return new CellSprite { Pixels = pixels, Width = width, Height = height };
    }

    private static CellSprite Rasterize(Image<Rgba32> source, int maxPixelSize)
    {
        var bounds = AssetImagePreparer.FindContentBounds(source);
        if (bounds.Width == 0 || bounds.Height == 0)
        {
            return CellSprite.Empty();
        }

        source.Mutate(ctx => ctx.Crop(bounds));

        var width = bounds.Width;
        var height = bounds.Height;

        if (width > maxPixelSize || height > maxPixelSize)
        {
            var scale = Math.Min(
                maxPixelSize / (double)width,
                maxPixelSize / (double)height);

            width = Math.Max(1, (int)Math.Round(width * scale));
            height = Math.Max(1, (int)Math.Round(height * scale));

            source.Mutate(ctx => ctx.Resize(new ResizeOptions
            {
                Size = new Size(width, height),
                Mode = ResizeMode.Stretch,
                Sampler = KnownResamplers.NearestNeighbor
            }));
        }

        var pixels = new Rgba32[width * height];
        for (var y = 0; y < height; y++)
        {
            for (var x = 0; x < width; x++)
            {
                pixels[(y * width) + x] = source[x, y];
            }
        }

        return new CellSprite { Pixels = pixels, Width = width, Height = height };
    }
}
