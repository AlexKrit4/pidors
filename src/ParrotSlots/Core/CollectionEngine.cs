namespace ParrotSlots.Core;

public sealed class CollectionEngine
{
    private static readonly (int Dr, int Dc)[] Directions = [(0, 1), (-1, 0), (0, -1), (1, 0)];

    public CollectionResult Run(GameBoard board, int bet, IPayTable payTable, ISymbolSet symbols, IRandomSource random)
    {
        var messages = new List<string>();
        var totalWin = 0;
        var owners = new ParrotColor?[board.Rows, board.Cols];

        while (true)
        {
            var collectedThisRound = 0;

            foreach (var color in ParrotColors.All)
            {
                var start = board.FindParrot(color);
                if (start is null)
                {
                    continue;
                }

                var roundWin = CollectForParrot(board, owners, start.Value, color, bet, payTable, messages);
                totalWin += roundWin;
                if (roundWin > 0)
                {
                    collectedThisRound++;
                }
            }

            if (collectedThisRound == 0)
            {
                break;
            }

            Cascade(board, symbols, random);
            messages.Add("Cascade: symbols fell down.");
        }

        return new CollectionResult(totalWin, messages, board);
    }

    internal static int CollectForParrot(
        GameBoard board,
        ParrotColor?[,] owners,
        (int Row, int Col) start,
        ParrotColor color,
        int bet,
        IPayTable payTable,
        List<string> messages)
    {
        var parrotDisplay = board.Get(start.Row, start.Col).Display;
        var totalWin = 0;
        var current = start;

        while (true)
        {
            var targets = GetReachableCrystals(board, owners, current, color);
            if (targets.Count == 0)
            {
                break;
            }

            var target = targets
                .OrderBy(pos => Math.Abs(pos.Row - current.Row) + Math.Abs(pos.Col - current.Col))
                .First();

            var path = FindPath(board, owners, current, target, color);
            if (path is null || path.Count < 2)
            {
                break;
            }

            var next = path[1];
            var crystal = board.Get(next.Row, next.Col);
            board.Set(current.Row, current.Col, Cell.Empty);
            owners[current.Row, current.Col] = color;
            board.Set(next.Row, next.Col, Cell.Parrot(color, parrotDisplay));

            if (crystal.IsCrystal && crystal.Color == color)
            {
                var win = payTable.GetCrystalPayout(color, crystal.Level, bet);
                totalWin += win;
                messages.Add($"{color} parrot collected level {crystal.Level} crystal (+{win}).");
            }

            current = next;
        }

        return totalWin;
    }

    public static List<(int Row, int Col)> GetReachableCrystals(
        GameBoard board,
        ParrotColor?[,] owners,
        (int Row, int Col) start,
        ParrotColor color)
    {
        var visited = new bool[board.Rows, board.Cols];
        var queue = new Queue<(int Row, int Col)>();
        var targets = new List<(int Row, int Col)>();

        queue.Enqueue(start);
        visited[start.Row, start.Col] = true;

        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            var cell = board.Get(current.Row, current.Col);

            if (cell.IsCrystal && cell.Color == color && current != start)
            {
                targets.Add(current);
            }

            foreach (var (dr, dc) in Directions)
            {
                var nr = current.Row + dr;
                var nc = current.Col + dc;
                if (nr < 0 || nr >= board.Rows || nc < 0 || nc >= board.Cols || visited[nr, nc])
                {
                    continue;
                }

                var nextCell = board.Get(nr, nc);
                var canEnter = nextCell.IsCrystal && nextCell.Color == color
                               || nextCell.IsEmpty && owners[nr, nc] == color
                               || (nr, nc) == start;

                if (!canEnter && !(nextCell.IsParrot && nextCell.Color == color))
                {
                    continue;
                }

                if (nextCell.IsParrot && nextCell.Color == color && (nr, nc) != start)
                {
                    continue;
                }

                visited[nr, nc] = true;
                queue.Enqueue((nr, nc));
            }
        }

        return targets;
    }

    public static List<(int Row, int Col)>? FindPath(
        GameBoard board,
        ParrotColor?[,] owners,
        (int Row, int Col) start,
        (int Row, int Col) goal,
        ParrotColor color)
    {
        if (start == goal)
        {
            return [start];
        }

        var queue = new Queue<((int Row, int Col) Pos, List<(int Row, int Col)> Path)>();
        var visited = new HashSet<(int Row, int Col)> { start };
        queue.Enqueue((start, [start]));

        while (queue.Count > 0)
        {
            var (current, path) = queue.Dequeue();

            foreach (var (dr, dc) in Directions)
            {
                var nr = current.Row + dr;
                var nc = current.Col + dc;
                var pos = (nr, nc);

                if (nr < 0 || nr >= board.Rows || nc < 0 || nc >= board.Cols || visited.Contains(pos))
                {
                    continue;
                }

                var cell = board.Get(nr, nc);
                var isGoal = pos == goal;
                var canStep = isGoal
                              || cell.IsCrystal && cell.Color == color
                              || cell.IsEmpty && owners[nr, nc] == color;

                if (!canStep)
                {
                    continue;
                }

                visited.Add(pos);
                var newPath = new List<(int Row, int Col)>(path) { pos };
                if (isGoal)
                {
                    return newPath;
                }

                queue.Enqueue((pos, newPath));
            }
        }

        return null;
    }

    internal static void Cascade(GameBoard board, ISymbolSet symbols, IRandomSource random)
    {
        for (var col = 0; col < board.Cols; col++)
        {
            var stack = new List<Cell>();

            for (var row = board.Rows - 1; row >= 0; row--)
            {
                var cell = board.Get(row, col);
                if (!cell.IsEmpty)
                {
                    stack.Add(cell);
                }
            }

            for (var row = board.Rows - 1; row >= 0; row--)
            {
                if (stack.Count > 0)
                {
                    board.Set(row, col, stack[0]);
                    stack.RemoveAt(0);
                    continue;
                }

                var color = ParrotColors.All[random.Next(ParrotColors.All.Count)];
                var level = CrystalLevelPicker.NextLevel(random);
                board.Set(row, col, Cell.Crystal(color, level, symbols.GetCrystalDisplay(color, level)));
            }
        }
    }
}

public sealed class CollectionResult
{
    public CollectionResult(int winAmount, IReadOnlyList<string> messages, GameBoard board)
    {
        WinAmount = winAmount;
        Messages = messages;
        Board = board;
    }

    public int WinAmount { get; }
    public IReadOnlyList<string> Messages { get; }
    public GameBoard Board { get; }
}
