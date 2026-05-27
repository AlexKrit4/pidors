using ParrotSlots.Assets;
using ParrotSlots.Core;
using Terminal.Gui;
using TuiAttribute = Terminal.Gui.Attribute;

namespace ParrotSlots.Terminal;

public sealed class GameBoardView : View, IBoardView
{
    private readonly SpriteCache _sprites;
    private readonly TerminalPixelArtWriter _writer = new();
    private BoardAnimationFrame _frame = new();
    private int _displayScale = 1;
    private int _originX;
    private int _originY;
    private int _lastBoundsWidth = -1;
    private int _lastBoundsHeight = -1;
    private int _lastClearX = -1;
    private int _lastClearY = -1;
    private int _lastClearWidth;
    private int _lastClearHeight;

    public GameBoardView(SpriteCache sprites)
    {
        _sprites = sprites;
        CanFocus = false;
        ColorScheme = new ColorScheme
        {
            Normal = new TuiAttribute(Color.White, Color.Blue)
        };
    }

    private int SlotWidth => _sprites.LayoutSlotWidth;
    private int SlotHeight => _sprites.LayoutSlotHeight;
    private int RowStride => TerminalDisplayConstants.CellTerminalHeight(SlotHeight);

    public void SetFrame(BoardAnimationFrame frame)
    {
        _frame = frame;
        SetNeedsDisplay();
    }

    public void SetBoard(GameBoard? board) => SetFrame(new BoardAnimationFrame { Board = board });

    public override void Redraw(Rect bounds)
    {
        Driver.SetAttribute(ColorScheme.Normal);
        var resized = UpdateScaleForBounds(bounds);
        if (resized)
        {
            ClearArea(bounds, 0, 0, bounds.Width, bounds.Height);
        }

        ClearRenderArea(bounds);

        if (_frame.Board is null)
        {
            Move(_originX, _originY);
            Driver.AddStr("Press Spin to play.");
            return;
        }

        DrawGrid(bounds);

        var board = _frame.Board;

        for (var row = 0; row < board.Rows; row++)
        {
            for (var col = 0; col < board.Cols; col++)
            {
                if (ShouldSkipCell(row, col))
                {
                    continue;
                }

                var cell = board.Get(row, col);
                if (cell.IsEmpty)
                {
                    continue;
                }

                DrawCellSprite(cell, col, row, GetOffsetLines(row, col), bounds);
            }
        }

        if (_frame.MovingParrotFrom is not null &&
            _frame.MovingParrotTo is not null &&
            _frame.MovingParrotColor is not null)
        {
            var from = _frame.MovingParrotFrom.Value;
            var to = _frame.MovingParrotTo.Value;
            var t = Math.Clamp(_frame.MovingParrotT, 0f, 1f);
            var display = board.Get(to.Row, to.Col).Display;
            var parrot = Cell.Parrot(_frame.MovingParrotColor.Value, display);
            var visualRow = from.Row + (to.Row - from.Row) * t;
            var visualCol = from.Col + (to.Col - from.Col) * t;
            DrawCellSprite(parrot, visualCol, visualRow, 0f, bounds);
        }
    }

    private bool UpdateScaleForBounds(Rect bounds)
    {
        if (bounds.Width == _lastBoundsWidth && bounds.Height == _lastBoundsHeight)
        {
            return false;
        }

        _lastBoundsWidth = bounds.Width;
        _lastBoundsHeight = bounds.Height;

        _sprites.SetMaxPixelSize(TerminalLayoutPlan.ComputeMaxPixelSize(bounds.Width, bounds.Height));
        _displayScale = TerminalLayoutPlan.ComputeDisplayScale(_sprites, bounds.Width, bounds.Height);

        var (nativeWidth, nativeHeight) = TerminalLayoutPlan.BoardViewSize(_sprites, displayScale: 1);
        var scaledWidth = nativeWidth * _displayScale;
        var scaledHeight = nativeHeight * _displayScale;
        _originX = Math.Max(0, (bounds.Width - scaledWidth) / 2);
        _originY = Math.Max(0, (bounds.Height - scaledHeight) / 2);
        return true;
    }

    private void ClearRenderArea(Rect bounds)
    {
        var (width, height) = TerminalLayoutPlan.BoardViewSize(_sprites, _displayScale);
        width++;
        height++;

        ClearArea(bounds, _lastClearX, _lastClearY, _lastClearWidth, _lastClearHeight);
        ClearArea(bounds, _originX, _originY, width, height);

        _lastClearX = _originX;
        _lastClearY = _originY;
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

    private void DrawGrid(Rect bounds)
    {
        if (_frame.Board is null)
        {
            return;
        }

        var board = _frame.Board;
        var slotWidth = SlotWidth * _displayScale;
        var slotHeight = SlotHeight * _displayScale;
        var rowStride = RowStride * _displayScale;
        var gridColor = Application.Driver.MakeAttribute(Color.DarkGray, Color.Blue);

        for (var col = 0; col <= board.Cols; col++)
        {
            var x = _originX + col * slotWidth;
            if (x < 0 || x >= bounds.Width)
            {
                continue;
            }

            for (var y = _originY; y < _originY + board.Rows * rowStride && y < bounds.Height; y++)
            {
                Move(x, y);
                Driver.SetAttribute(gridColor);
                Driver.AddRune(new Rune('│'));
            }
        }

        for (var row = 0; row <= board.Rows; row++)
        {
            var y = _originY + row * rowStride;
            if (y < 0 || y >= bounds.Height)
            {
                continue;
            }

            for (var x = _originX; x < _originX + board.Cols * slotWidth && x < bounds.Width; x++)
            {
                Move(x, y);
                Driver.SetAttribute(gridColor);
                Driver.AddRune(new Rune('─'));
            }
        }
    }

    private bool ShouldSkipCell(int row, int col)
    {
        if (_frame.MovingParrotFrom is null ||
            _frame.MovingParrotTo is null ||
            _frame.MovingParrotColor is null)
        {
            return false;
        }

        var from = _frame.MovingParrotFrom.Value;
        if (row == from.Row && col == from.Col)
        {
            return true;
        }

        var to = _frame.MovingParrotTo.Value;
        return row == to.Row && col == to.Col;
    }

    private float GetOffsetLines(int row, int col)
    {
        var offsetY = _frame.CellOffsetY?[row, col] ?? 0f;
        return offsetY / TerminalDisplayConstants.RaylibCellSize * (SlotHeight / 2f);
    }

    private void DrawCellSprite(
        Cell cell,
        float gridCol,
        float gridRow,
        float extraOffsetLines,
        Rect bounds)
    {
        var sprite = _sprites.GetCellSprite(cell);
        if (!sprite.HasVisiblePixels())
        {
            return;
        }

        var terminalLine = gridRow * RowStride + extraOffsetLines;
        _writer.DrawSprite(
            this,
            bounds,
            sprite,
            gridCol,
            terminalLine,
            SlotWidth,
            SlotHeight,
            _displayScale,
            _originX,
            _originY,
            SpriteCache.Backdrop);
    }
}
