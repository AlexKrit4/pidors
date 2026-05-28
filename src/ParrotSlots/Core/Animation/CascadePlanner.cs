using ParrotSlots.Core;

namespace ParrotSlots.Core.Animation;

public sealed class CascadePlan
{
    public required GameBoard AfterGravity { get; init; }
    public required int[,] FallRows { get; init; }
    public required GameBoard FinalBoard { get; init; }
    public required List<(int Row, int Col, Cell Cell)> NewCells { get; init; }
}

public static class CascadePlanner
{
    public static CascadePlan Plan(GameBoard board, ISymbolSet symbols, IRandomSource random)
    {
        var afterGravity = board.Clone();
        var fallRows = new int[board.Rows, board.Cols];

        for (var col = 0; col < board.Cols; col++)
        {
            var stack = new List<(int SourceRow, Cell Cell)>();
            for (var row = board.Rows - 1; row >= 0; row--)
            {
                var cell = board.Get(row, col);
                if (!cell.IsEmpty)
                {
                    stack.Add((row, cell));
                }
            }

            var writeRow = board.Rows - 1;
            foreach (var (sourceRow, cell) in stack)
            {
                afterGravity.Set(writeRow, col, cell);
                fallRows[writeRow, col] = writeRow - sourceRow;
                writeRow--;
            }

            for (var row = writeRow; row >= 0; row--)
            {
                afterGravity.Set(row, col, Cell.Empty);
                fallRows[row, col] = 0;
            }
        }

        var final = afterGravity.Clone();
        var newCells = new List<(int, int, Cell)>();

        for (var col = 0; col < final.Cols; col++)
        {
            for (var row = 0; row < final.Rows; row++)
            {
                if (!final.Get(row, col).IsEmpty)
                {
                    continue;
                }

                var color = ParrotColors.All[random.Next(ParrotColors.All.Count)];
                var cell = Cell.Crystal(color, 1, symbols.GetCrystalDisplay(color, 1));
                final.Set(row, col, cell);
                newCells.Add((row, col, cell));
            }
        }

        return new CascadePlan
        {
            AfterGravity = afterGravity,
            FallRows = fallRows,
            FinalBoard = final,
            NewCells = newCells
        };
    }

    public static void Apply(GameBoard board, CascadePlan plan)
    {
        for (var row = 0; row < board.Rows; row++)
        {
            for (var col = 0; col < board.Cols; col++)
            {
                board.Set(row, col, plan.FinalBoard.Get(row, col));
            }
        }
    }
}
