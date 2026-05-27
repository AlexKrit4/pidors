namespace ParrotSlots.Core;

public sealed class GameBoard
{
    private readonly Cell[,] _cells;

    public GameBoard(Cell[,] cells)
    {
        _cells = cells;
        Rows = cells.GetLength(0);
        Cols = cells.GetLength(1);
    }

    public int Rows { get; }
    public int Cols { get; }

    public Cell Get(int row, int col) => _cells[row, col];

    public void Set(int row, int col, Cell cell) => _cells[row, col] = cell;

    public (int Row, int Col)? FindParrot(ParrotColor color)
    {
        for (var row = 0; row < Rows; row++)
        {
            for (var col = 0; col < Cols; col++)
            {
                var cell = _cells[row, col];
                if (cell.IsParrot && cell.Color == color)
                {
                    return (row, col);
                }
            }
        }

        return null;
    }

    public GameBoard Clone()
    {
        var copy = new Cell[Rows, Cols];
        Array.Copy(_cells, copy, _cells.Length);
        return new GameBoard(copy);
    }

    public override string ToString()
    {
        var lines = new List<string>();
        for (var row = 0; row < Rows; row++)
        {
            var cells = new List<string>();
            for (var col = 0; col < Cols; col++)
            {
                cells.Add(_cells[row, col].Display.PadRight(3));
            }

            lines.Add(string.Join(" | ", cells));
        }

        return string.Join(Environment.NewLine, lines);
    }
}
