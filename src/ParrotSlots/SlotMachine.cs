using ParrotSlots.Core;
using ParrotSlots.Core.Animation;
using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots;

public enum GameRunState
{
    Playing,
    Won,
    Lost
}

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
    public int SpinsLeft { get; private set; } = GameSettings.Instance.SpinLimit;
    public int TargetBalance => GameSettings.Instance.TargetBalance;
    public GameRunState RunState { get; private set; } = GameRunState.Playing;
    public bool IsGameOver => RunState != GameRunState.Playing;
    public string RunMessage { get; private set; } = $"Reach {GameSettings.Instance.TargetBalance} before {GameSettings.Instance.SpinLimit} spins run out.";
    public CommandInterpreter Interpreter { get; private set; } = new();

    public void AttachInterpreter(CommandInterpreter interpreter) => Interpreter = interpreter;

    public bool CanSpin() =>
        RunState == GameRunState.Playing &&
        SpinsLeft > 0 &&
        _wallet.Balance >= _wallet.CurrentBet &&
        _wallet.CurrentBet > 0;

    public void SetBet(int amount)
    {
        if (IsGameOver)
        {
            _observable.NotifyCommandFailed(RunMessage);
            return;
        }

        if (!_wallet.TrySetBet(amount, out _))
        {
            return;
        }
    }

    public SpinResult? Spin()
    {
        if (!BeginSpinTurn())
        {
            return null;
        }

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
        UpdateRunStateAfterSpin();
        return result;
    }

    public GameBoard? LastBoard { get; private set; }

    public AnimatedSpinSession? BeginAnimatedSpin()
    {
        if (!BeginSpinTurn())
        {
            return null;
        }

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
        UpdateRunStateAfterSpin();
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
                Goal: reach balance {settings.TargetBalance} in {settings.SpinLimit} spins.
                Commands: spin | bet N | auto N | balance | rules | quit
                Chain commands with ';', e.g. bet 20; spin; spin

                Spin fills the board with crystals and places 4 parrots (not adjacent).
                Each parrot walks to reachable crystals of its color and collects them.
                Empty cells left behind become paths; after a round symbols cascade down.
                Weak collections can pay less than the bet, so a spin can be negative.
                You lose if spins run out before the goal or the balance drops below the minimum bet.
                Bet range: {settings.MinBet}-{settings.MaxBet}
                """;
    }

    private bool BeginSpinTurn()
    {
        if (RunState != GameRunState.Playing)
        {
            _observable.NotifyCommandFailed(RunMessage);
            return false;
        }

        if (SpinsLeft <= 0)
        {
            FinishRun(GameRunState.Lost, $"Game over: no spins left. Target was {TargetBalance}.");
            return false;
        }

        if (!_wallet.TryDeductBet(out _))
        {
            return false;
        }

        SpinsLeft--;
        _observable.NotifySpinStarted(_wallet.CurrentBet);
        return true;
    }

    private void UpdateRunStateAfterSpin()
    {
        if (RunState != GameRunState.Playing)
        {
            return;
        }

        if (_wallet.Balance >= TargetBalance)
        {
            FinishRun(GameRunState.Won, $"Victory! Balance {Balance} reached target {TargetBalance} with {SpinsLeft} spins left.");
            return;
        }

        if (_wallet.Balance < GameSettings.Instance.MinBet)
        {
            FinishRun(GameRunState.Lost, $"Game over: balance {Balance} is below the minimum bet.");
            return;
        }

        if (SpinsLeft <= 0)
        {
            FinishRun(GameRunState.Lost, $"Game over: target {TargetBalance} was not reached. Final balance: {Balance}.");
        }
    }

    private void FinishRun(GameRunState state, string message)
    {
        if (RunState != GameRunState.Playing)
        {
            return;
        }

        RunState = state;
        RunMessage = message;
        _observable.NotifyGameOver(state == GameRunState.Won, message);
    }
}
