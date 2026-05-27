using ParrotSlots.Assets;
using ParrotSlots.Terminal.Chafa;
using Terminal.Gui;
using TuiAttribute = Terminal.Gui.Attribute;

namespace ParrotSlots.Terminal;

public sealed class ChafaBoardView : View, IBoardView
{
    private readonly BoardImageCompositor _compositor;
    private BoardAnimationFrame _frame = new();
    private string _renderedText = string.Empty;
    private string _renderedBackground = string.Empty;
    private int _lastRenderColumns = -1;
    private int _lastRenderRows = -1;
    private int _lastBackgroundColumns = -1;
    private int _lastBackgroundRows = -1;
    private int _lastBoundsWidth = -1;
    private int _lastBoundsHeight = -1;
    private int _lastClearX = -1;
    private int _lastClearY = -1;
    private int _lastClearWidth;
    private int _lastClearHeight;
    private bool _backgroundDrawn;

    public ChafaBoardView(ImageCatalog catalog)
    {
        _compositor = new BoardImageCompositor(catalog);
        CanFocus = false;
        ColorScheme = new ColorScheme
        {
            Normal = new TuiAttribute(Color.White, Color.Blue)
        };
    }

    public void SetFrame(BoardAnimationFrame frame)
    {
        _frame = frame;
        _renderedText = string.Empty;
        SetNeedsDisplay();
    }

    public void SetBoard(Core.GameBoard? board) => SetFrame(new BoardAnimationFrame { Board = board });

    public override void Redraw(Rect bounds)
    {
        Driver.SetAttribute(ColorScheme.Normal);

        if (bounds.Width <= 0 || bounds.Height <= 0)
        {
            return;
        }

        if (bounds.Width != _lastBoundsWidth || bounds.Height != _lastBoundsHeight)
        {
            _lastBoundsWidth = bounds.Width;
            _lastBoundsHeight = bounds.Height;
            ClearArea(bounds, 0, 0, bounds.Width, bounds.Height);
            _renderedBackground = string.Empty;
            _backgroundDrawn = false;
        }

        try
        {
            var (renderColumns, renderRows) = ChafaConsoleLayout.MeasureBoardSize(bounds.Width, bounds.Height);
            var originX = Math.Max(0, (bounds.Width - renderColumns) / 2);
            var originY = Math.Max(0, (bounds.Height - renderRows) / 2);
            DrawBackgroundIfNeeded(bounds);
            ClearRenderArea(bounds, originX, originY, renderColumns, renderRows);

            if (renderColumns != _lastRenderColumns || renderRows != _lastRenderRows)
            {
                _lastRenderColumns = renderColumns;
                _lastRenderRows = renderRows;
                _renderedText = string.Empty;
            }

            if (string.IsNullOrEmpty(_renderedText))
            {
                var png = _compositor.Render(_frame);
                _renderedText = ChafaCli.RenderPng(png, renderColumns, renderRows);
            }

            AnsiTerminalWriter.Draw(this, bounds, _renderedText, Color.White, Color.Blue, originX, originY);
        }
        catch (Exception ex)
        {
            Move(0, 0);
            Driver.SetAttribute(ColorScheme.Normal);
            var message = ex.Message;
            if (message.Length > bounds.Width - 2)
            {
                message = message[..Math.Max(0, bounds.Width - 5)] + "...";
            }

            Driver.AddStr($"Chafa error: {message}");
        }
    }

    private void DrawBackgroundIfNeeded(Rect bounds)
    {
        if (_backgroundDrawn)
        {
            return;
        }

        if (string.IsNullOrEmpty(_renderedBackground) ||
            _lastBackgroundColumns != bounds.Width ||
            _lastBackgroundRows != bounds.Height)
        {
            var png = _compositor.RenderBackground(bounds.Width, bounds.Height);
            _renderedBackground = ChafaCli.RenderPng(png, bounds.Width, bounds.Height, "block+space");
            _lastBackgroundColumns = bounds.Width;
            _lastBackgroundRows = bounds.Height;
        }

        AnsiTerminalWriter.Draw(this, bounds, _renderedBackground, Color.White, Color.Blue);
        _backgroundDrawn = true;
    }

    private void ClearRenderArea(Rect bounds, int left, int top, int width, int height)
    {
        ClearArea(bounds, _lastClearX, _lastClearY, _lastClearWidth, _lastClearHeight);
        ClearArea(bounds, left, top, width, height);

        _lastClearX = left;
        _lastClearY = top;
        _lastClearWidth = width;
        _lastClearHeight = height;
    }

    private void ClearArea(Rect bounds, int left, int top, int width, int height)
    {
        if (left < 0 || top < 0 || width <= 0 || height <= 0)
        {
            return;
        }

        var x0 = Math.Clamp(left, 0, bounds.Width);
        var y0 = Math.Clamp(top, 0, bounds.Height);
        var x1 = Math.Clamp(left + width, 0, bounds.Width);
        var y1 = Math.Clamp(top + height, 0, bounds.Height);
        var clearWidth = x1 - x0;
        if (clearWidth <= 0 || y1 <= y0)
        {
            return;
        }

        Driver.SetAttribute(ColorScheme.Normal);
        var blank = new string(' ', clearWidth);
        for (var y = y0; y < y1; y++)
        {
            Move(x0, y);
            Driver.AddStr(blank);
        }
    }
}
