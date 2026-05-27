using ParrotSlots.Core;
using ParrotSlots.Core.Animation;
using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots;

public sealed class SlotMachine
{
    private readonly IWallet _wallet;
    private readonly IBoardGenerator _boardGenerator;
    private readonly IPayTable _payTable;
    private readonly ISymbolSet _symbols;
    private readonly IPayoutRule _payoutRules;
    private readonly IGameObservable _observable;
    private readonly IRandomSource _random;
    private readonly string _themeName;

    internal SlotMachine(
        IWallet wallet,
        IBoardGenerator boardGenerator,
        IPayTable payTable,
        ISymbolSet symbols,
        IPayoutRule payoutRules,
        IGameObservable observable,
        IRandomSource random,
        string themeName)
    {
        _wallet = wallet;
        _boardGenerator = boardGenerator;
        _payTable = payTable;
        _symbols = symbols;
        _payoutRules = payoutRules;
        _observable = observable;
        _random = random;
        _themeName = themeName;
    }

    public int Balance => _wallet.Balance;
    public int CurrentBet => _wallet.CurrentBet;
    public string ThemeName => _themeName;
    public CommandInterpreter Interpreter { get; private set; } = new();

    public void AttachInterpreter(CommandInterpreter interpreter) => Interpreter = interpreter;

    public bool CanSpin() => _wallet.Balance >= _wallet.CurrentBet && _wallet.CurrentBet > 0;

    public void SetBet(int amount)
    {
        if (!_wallet.TrySetBet(amount, out _))
        {
            return;
        }
    }

    public SpinResult? Spin()
    {
        if (!_wallet.TryDeductBet(out _))
        {
            return null;
        }

        _observable.NotifySpinStarted(_wallet.CurrentBet);

        var board = _boardGenerator.CreateBoard(_random);
        var context = new PayoutContext(board, _wallet.CurrentBet, _payTable, _symbols, _random);
        var payout = _payoutRules.Evaluate(context);

        if (payout.WinAmount > 0)
        {
            _wallet.AddWin(payout.WinAmount);
        }

        var result = new SpinResult(context.Board, _wallet.CurrentBet, payout.WinAmount, payout.Messages);
        LastBoard = result.Board;
        _observable.NotifySpinFinished(result);
        return result;
    }

    public GameBoard? LastBoard { get; private set; }

    public AnimatedSpinSession? BeginAnimatedSpin()
    {
        if (!_wallet.TryDeductBet(out _))
        {
            return null;
        }

        _observable.NotifySpinStarted(_wallet.CurrentBet);
        var board = _boardGenerator.CreateBoard(_random);
        var plan = SpinPlanner.Build(board, _wallet.CurrentBet, _payTable, _symbols, _random);
        return new AnimatedSpinSession(this, plan, _wallet.CurrentBet);
    }

    internal void CompleteAnimatedSpin(AnimatedSpinSession session)
    {
        if (session.TotalWin > 0)
        {
            _wallet.AddWin(session.TotalWin);
        }

        LastBoard = session.FinalBoard;
        var result = new SpinResult(session.FinalBoard, session.Bet, session.TotalWin, session.Messages);
        _observable.NotifySpinFinished(result);
    }

    public SpinResult EvaluateBoard(GameBoard board, int bet)
    {
        var context = new PayoutContext(board.Clone(), bet, _payTable, _symbols, _random);
        var payout = _payoutRules.Evaluate(context);
        return new SpinResult(context.Board, bet, payout.WinAmount, payout.Messages);
    }

    public string GetRulesText()
    {
        var settings = GameSettings.Instance;
        return $"""
                Pirate Parrots ({_themeName})
                Grid: {settings.RowCount}x{settings.ColCount}, parrots: {settings.ParrotCount}
                Commands: spin | bet N | auto N | balance | rules | quit
                Chain commands with ';', e.g. bet 20; spin; spin

                Spin fills the board with crystals and places 4 parrots (not adjacent).
                Each parrot walks to reachable crystals of its color and collects them.
                Empty cells left behind become paths; after a round symbols cascade down.
                Bet range: {settings.MinBet}-{settings.MaxBet}
                """;
    }
}
