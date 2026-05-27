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
    private int _lastColumns = -1;
    private int _lastRows = -1;

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
        Clear();

        if (bounds.Width <= 0 || bounds.Height <= 0)
        {
            return;
        }

        try
        {
            if (bounds.Width != _lastColumns || bounds.Height != _lastRows)
            {
                _lastColumns = bounds.Width;
                _lastRows = bounds.Height;
                _renderedText = string.Empty;
            }

            if (string.IsNullOrEmpty(_renderedText))
            {
                var png = _compositor.Render(_frame);
                _renderedText = ChafaCli.RenderPng(png, bounds.Width, bounds.Height);
            }

            AnsiTerminalWriter.Draw(this, bounds, _renderedText, Color.White, Color.Blue);
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
}
