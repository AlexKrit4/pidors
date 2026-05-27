using ParrotSlots.Assets;
using ParrotSlots.Core;

namespace ParrotSlots.Tests;

public class SpriteCacheTests
{
    [Fact]
    public void GetCellSprite_LoadsParrotAndCrystalSprites()
    {
        var catalog = new ImageCatalog(Path.Combine(AppContext.BaseDirectory, "assets", "images"));
        if (!File.Exists(catalog.GetParrotPath(ParrotColor.Red)))
        {
            return;
        }

        var cache = new SpriteCache(catalog);
        var parrot = cache.GetCellSprite(Cell.Parrot(ParrotColor.Red, "P"));
        var crystal = cache.GetCellSprite(Cell.Crystal(ParrotColor.Red, 1, "C"));

        Assert.True(parrot.Width > 0);
        Assert.True(parrot.Height > 0);
        Assert.True(parrot.HasVisiblePixels());
        Assert.True(crystal.HasVisiblePixels());
        Assert.True(parrot.Width <= CellSprite.MaxPixelSize);
        Assert.True(cache.LayoutSlotWidth <= CellSprite.MaxPixelSize + 2);
    }

    [Fact]
    public void ImageCatalog_MapsColorsToExpectedFiles()
    {
        var catalog = new ImageCatalog(@"C:\fake");
        Assert.EndsWith("High1.png", catalog.GetParrotPath(ParrotColor.Red));
        Assert.EndsWith("Low3_5.png", catalog.GetCrystalPath(ParrotColor.Green, 5));
    }
}
