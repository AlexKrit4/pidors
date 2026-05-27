namespace ParrotSlots.Assets;

using ParrotSlots.Core;

public sealed class ImageCatalog
{
    private readonly string _root;

    public ImageCatalog(string? rootDirectory = null)
    {
        _root = rootDirectory ?? Path.Combine(AppContext.BaseDirectory, "assets", "images");
    }

    public string AssetsRoot => _root;

    public string? GetBackgroundPath()
    {
        foreach (var name in new[] { "Pirots3_BaseBg.jpg", "Pirots3_BaseBg.png", "Pirots3_BaseBg.jpeg" })
        {
            var path = Path.Combine(_root, name);
            if (File.Exists(path))
            {
                return path;
            }
        }

        return null;
    }

    public string GetParrotPath(ParrotColor color) => Path.Combine(_root, color switch
    {
        ParrotColor.Red => "High1.png",
        ParrotColor.Purple => "High2.png",
        ParrotColor.Green => "High3.png",
        ParrotColor.Blue => "High4.png",
        _ => "High1.png"
    });

    public string GetCrystalPath(ParrotColor color, int level) =>
        Path.Combine(_root, $"Low{(int)color}_{level}.png");

    public IEnumerable<string> AllAssetPaths()
    {
        foreach (var color in ParrotColors.All)
        {
            yield return GetParrotPath(color);
            for (var level = 1; level <= 7; level++)
            {
                yield return GetCrystalPath(color, level);
            }
        }
    }
}
