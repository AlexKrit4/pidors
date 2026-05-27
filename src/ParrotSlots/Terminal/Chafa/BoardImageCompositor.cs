using ParrotSlots.Assets;
using ParrotSlots.Core;
using ParrotSlots.Graphics;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

namespace ParrotSlots.Terminal.Chafa;

public sealed class BoardImageCompositor
{
    public const int CellPixelSize = 48;
    private static readonly Rgba32 FallbackBackground = new(0, 0, 170, 255);

    private readonly ImageCatalog _catalog;
    private readonly Dictionary<string, Image<Rgba32>> _images = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, Image<Rgba32>> _backgroundCache = new(StringComparer.OrdinalIgnoreCase);

    public BoardImageCompositor(ImageCatalog catalog) => _catalog = catalog;

    public byte[] Render(BoardAnimationFrame frame)
    {
        if (frame.Board is null)
        {
            return RenderMessage("Press Spin to play.");
        }

        var width = GameConstants.GridCols * CellPixelSize;
        var height = GameConstants.GridRows * CellPixelSize;

        using var canvas = new Image<Rgba32>(width, height);
        DrawBackground(canvas);
        DrawGrid(canvas);

        var board = frame.Board;
        for (var row = 0; row < board.Rows; row++)
        {
            for (var col = 0; col < board.Cols; col++)
            {
                if (ShouldSkipCell(frame, row, col))
                {
                    continue;
                }

                var cell = board.Get(row, col);
                if (cell.IsEmpty)
                {
                    continue;
                }

                var offsetY = frame.CellOffsetY?[row, col] ?? 0f;
                DrawCell(canvas, cell, col, row, offsetY);
            }
        }

        if (frame.MovingParrotFrom is not null &&
            frame.MovingParrotTo is not null &&
            frame.MovingParrotColor is not null)
        {
            var from = frame.MovingParrotFrom.Value;
            var to = frame.MovingParrotTo.Value;
            var t = Math.Clamp(frame.MovingParrotT, 0f, 1f);
            var display = board.Get(to.Row, to.Col).Display;
            var parrot = Cell.Parrot(frame.MovingParrotColor.Value, display);
            var x = (from.Col + (to.Col - from.Col) * t) * CellPixelSize;
            var y = (from.Row + (to.Row - from.Row) * t) * CellPixelSize;
            DrawCellAt(canvas, parrot, x, y);
        }

        using var stream = new MemoryStream();
        canvas.SaveAsPng(stream);
        return stream.ToArray();
    }

    private void DrawBackground(Image<Rgba32> canvas)
    {
        var background = LoadBackground(canvas.Width, canvas.Height);
        if (background is null)
        {
            canvas.Mutate(ctx => ctx.BackgroundColor(FallbackBackground));
            return;
        }

        canvas.Mutate(ctx => ctx.DrawImage(background, new Point(0, 0), 1f));
    }

    private static void DrawGrid(Image<Rgba32> canvas)
    {
        var line = new Rgba32(255, 255, 255, 72);

        for (var col = 1; col < GameConstants.GridCols; col++)
        {
            var x = col * CellPixelSize;
            for (var y = 0; y < canvas.Height; y++)
            {
                canvas[x, y] = line;
            }
        }

        for (var row = 1; row < GameConstants.GridRows; row++)
        {
            var y = row * CellPixelSize;
            for (var x = 0; x < canvas.Width; x++)
            {
                canvas[x, y] = line;
            }
        }

        var border = new Rgba32(255, 255, 255, 120);
        for (var x = 0; x < canvas.Width; x++)
        {
            canvas[x, 0] = border;
            canvas[x, canvas.Height - 1] = border;
        }

        for (var y = 0; y < canvas.Height; y++)
        {
            canvas[0, y] = border;
            canvas[canvas.Width - 1, y] = border;
        }
    }

    private Image<Rgba32>? LoadBackground(int width, int height)
    {
        var path = _catalog.GetBackgroundPath();
        if (path is null)
        {
            return null;
        }

        var key = $"{path}|{width}x{height}";
        if (_backgroundCache.TryGetValue(key, out var cached))
        {
            return cached;
        }

        using var source = Image.Load<Rgba32>(path);
        var resized = source.Clone(ctx => ctx.Resize(new ResizeOptions
        {
            Size = new Size(width, height),
            Mode = ResizeMode.Crop,
            Position = AnchorPositionMode.Center,
            Sampler = KnownResamplers.Bicubic
        }));

        _backgroundCache[key] = resized;
        return resized;
    }

    private static bool ShouldSkipCell(BoardAnimationFrame frame, int row, int col)
    {
        if (frame.MovingParrotFrom is null ||
            frame.MovingParrotTo is null ||
            frame.MovingParrotColor is null)
        {
            return false;
        }

        var from = frame.MovingParrotFrom.Value;
        if (row == from.Row && col == from.Col)
        {
            return true;
        }

        var to = frame.MovingParrotTo.Value;
        return row == to.Row && col == to.Col;
    }

    private void DrawCell(Image<Rgba32> canvas, Cell cell, int col, int row, float offsetY)
    {
        var x = col * CellPixelSize;
        var y = row * CellPixelSize + offsetY;
        DrawCellAt(canvas, cell, x, y);
    }

    private void DrawCellAt(Image<Rgba32> canvas, Cell cell, float x, float y)
    {
        var sprite = LoadImage(cell);
        if (sprite is null)
        {
            return;
        }

        var point = new Point((int)Math.Round(x), (int)Math.Round(y));
        canvas.Mutate(ctx => ctx.DrawImage(sprite, point, 1f));
    }

    private Image<Rgba32>? LoadImage(Cell cell)
    {
        var path = cell.IsParrot
            ? _catalog.GetParrotPath(cell.Color)
            : _catalog.GetCrystalPath(cell.Color, cell.Level);

        if (_images.TryGetValue(path, out var cached))
        {
            return cached;
        }

        if (!File.Exists(path))
        {
            return null;
        }

        var image = AssetImagePreparer.LoadCroppedCellImage(path, CellPixelSize);
        _images[path] = image;
        return image;
    }

    private byte[] RenderMessage(string message)
    {
        using var image = new Image<Rgba32>(320, 80);
        DrawBackground(image);
        using var stream = new MemoryStream();
        image.SaveAsPng(stream);
        return stream.ToArray();
    }
}
