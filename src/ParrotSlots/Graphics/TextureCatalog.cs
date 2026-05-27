using ParrotSlots.Assets;
using ParrotSlots.Core;
using Raylib_cs;

namespace ParrotSlots.Graphics;

public sealed class TextureCatalog : IDisposable
{
    private readonly ImageCatalog _paths = new();
    private readonly Dictionary<string, Texture2D> _textures = new(StringComparer.OrdinalIgnoreCase);

    public Texture2D Background { get; private set; }

    public void LoadAll()
    {
        var bgPath = Path.Combine(_paths.AssetsRoot, "Pirots3_BaseBg.jpg");
        Background = File.Exists(bgPath) ? Raylib.LoadTexture(bgPath) : default;

        foreach (var color in ParrotColors.All)
        {
            LoadPath(_paths.GetParrotPath(color));
            for (var level = 1; level <= 7; level++)
            {
                LoadPath(_paths.GetCrystalPath(color, level));
            }
        }
    }

    public Texture2D Get(Cell cell)
    {
        if (cell.IsEmpty)
        {
            return default;
        }

        var path = cell.IsParrot
            ? _paths.GetParrotPath(cell.Color)
            : _paths.GetCrystalPath(cell.Color, cell.Level);

        return _textures.TryGetValue(path, out var texture) ? texture : default;
    }

    private void LoadPath(string path)
    {
        if (_textures.ContainsKey(path) || !File.Exists(path))
        {
            return;
        }

        _textures[path] = Raylib.LoadTexture(path);
    }

    public void Dispose()
    {
        foreach (var texture in _textures.Values)
        {
            if (texture.Id != 0)
            {
                Raylib.UnloadTexture(texture);
            }
        }

        if (Background.Id != 0)
        {
            Raylib.UnloadTexture(Background);
        }
    }
}
