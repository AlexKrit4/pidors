using ParrotSlots.Core;

namespace ParrotSlots.Core.Animation;

public abstract record SpinPhase;

public sealed record FallOutPhase(GameBoard Board) : SpinPhase;

public sealed record DropInPhase(GameBoard Board) : SpinPhase;

public sealed record ParrotStepPhase(
    GameBoard Board,
    ParrotColor Color,
    (int Row, int Col) From,
    (int Row, int Col) To,
    int WinAmount,
    string Message) : SpinPhase;

public sealed record CascadePhase(GameBoard BoardBefore, CascadePlan Plan) : SpinPhase;

public sealed class SpinPlan
{
    public SpinPlan(IReadOnlyList<SpinPhase> phases, int totalWin, GameBoard finalBoard, IReadOnlyList<string> messages)
    {
        Phases = phases;
        TotalWin = totalWin;
        FinalBoard = finalBoard;
        Messages = messages;
    }

    public IReadOnlyList<SpinPhase> Phases { get; }
    public int TotalWin { get; }
    public GameBoard FinalBoard { get; }
    public IReadOnlyList<string> Messages { get; }
}

public static class SpinPlanner
{
    public static SpinPlan Build(GameBoard board, int bet, IPayTable payTable, ISymbolSet symbols, IRandomSource random)
    {
        var working = board.Clone();
        var owners = new ParrotColor?[working.Rows, working.Cols];
        var phases = new List<SpinPhase> { new DropInPhase(working.Clone()) };
        var messages = new List<string>();
        var totalWin = 0;

        while (true)
        {
            var roundMoves = 0;

            foreach (var color in ParrotColors.All)
            {
                var start = working.FindParrot(color);
                if (start is null)
                {
                    continue;
                }

                var parrotDisplay = working.Get(start.Value.Row, start.Value.Col).Display;
                var current = start.Value;

                while (true)
                {
                    var targets = CollectionEngine.GetReachableCrystals(working, owners, current, color);
                    if (targets.Count == 0)
                    {
                        break;
                    }

                    var target = targets
                        .OrderBy(pos => Math.Abs(pos.Row - current.Row) + Math.Abs(pos.Col - current.Col))
                        .First();

                    var path = CollectionEngine.FindPath(working, owners, current, target, color);
                    if (path is null || path.Count < 2)
                    {
                        break;
                    }

                    var next = path[1];
                    var from = current;
                    var crystal = working.Get(next.Row, next.Col);
                    working.Set(from.Row, from.Col, Cell.Empty);
                    owners[from.Row, from.Col] = color;
                    working.Set(next.Row, next.Col, Cell.Parrot(color, parrotDisplay));

                    var win = 0;
                    var message = string.Empty;
                    if (crystal.IsCrystal && crystal.Color == color)
                    {
                        win = payTable.GetCrystalPayout(color, crystal.Level, bet);
                        totalWin += win;
                        message = $"{color} parrot collected level {crystal.Level} crystal (+{win}).";
                        messages.Add(message);
                    }

                    phases.Add(new ParrotStepPhase(working.Clone(), color, from, next, win, message));
                    current = next;
                    roundMoves++;
                }
            }

            if (roundMoves == 0)
            {
                break;
            }

            var cascade = CascadePlanner.Plan(working, symbols, random);
            phases.Add(new CascadePhase(working.Clone(), cascade));
            CascadePlanner.Apply(working, cascade);
            messages.Add("Cascade: symbols fell down.");
        }

        return new SpinPlan(phases, totalWin, working, messages);
    }
}
