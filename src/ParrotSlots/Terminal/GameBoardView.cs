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
        Clear();

        UpdateScaleForBounds(bounds);

        if (_frame.Board is null)
        {
            Move(0, 0);
            Driver.AddStr("Press Spin to play.");
            return;
        }

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

    private void UpdateScaleForBounds(Rect bounds)
    {
        if (bounds.Width == _lastBoundsWidth && bounds.Height == _lastBoundsHeight)
        {
            return;
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
