using ParrotSlots.Builder;
using ParrotSlots.Interpreter;
using ParrotSlots.Graphics;
using ParrotSlots.Terminal;
using ParrotSlots.Terminal.Chafa;

namespace ParrotSlots;

public static class Program
{
    public static void Main(string[] args)
    {
        if (args.Contains("--text", StringComparer.OrdinalIgnoreCase))
        {
            var game = new DefaultGameDirector().CreateStandardGame();
            RunGameLoop(game, Console.In, Console.Out);
            return;
        }

        if (args.Contains("--terminal", StringComparer.OrdinalIgnoreCase))
        {
            var useChafa = args.Contains("--chafa", StringComparer.OrdinalIgnoreCase);
            if (useChafa && ChafaCli.IsAvailable())
            {
                new ChafaConsoleApplication().Run();
            }
            else
            {
                new TerminalGameApplication(useChafa).Run();
            }

            return;
        }

        using var app = new RaylibGameApplication();
        app.Run();
    }

    internal static void RunGameLoop(SlotMachine game, TextReader input, TextWriter output)
    {
        output.WriteLine("=== Pirate Parrots ===");
        output.WriteLine(game.GetRulesText());
        output.WriteLine($"Balance: {game.Balance} | Bet: {game.CurrentBet}");
        output.WriteLine("Enter command:");

        while (true)
        {
            output.Write("> ");
            var line = input.ReadLine();
            if (line is null)
            {
                break;
            }

            try
            {
                var result = game.Interpreter.Execute(line, game);
                switch (result.Type)
                {
                    case CommandResultType.ShowBalance:
                    case CommandResultType.Continue when result.Message is not null:
                        output.WriteLine(result.Message);
                        break;
                    case CommandResultType.ShowRules:
                        output.WriteLine(result.Message);
                        break;
                    case CommandResultType.Quit:
                        output.WriteLine("Thanks for playing!");
                        return;
                }
            }
            catch (InvalidOperationException ex)
            {
                output.WriteLine($">> ERROR: {ex.Message}");
            }
        }
    }
}
