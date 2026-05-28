using ParrotSlots.Core;
using ParrotSlots.Interpreter;
using ParrotSlots.Observer;
using ParrotSlots.Rules;
using ParrotSlots.Settings;
using ParrotSlots.Themes;
using ParrotSlots.Wallet;

namespace ParrotSlots.Builder;

public sealed class SlotMachineBuilder
{
    private ISlotThemeFactory? _themeFactory;
    private IWallet? _wallet;
    private IPayoutRule? _payoutRules;
    private IGameObservable? _observable;
    private IRandomSource? _random;
    private CommandInterpreter? _interpreter;
    private IBoardGenerator? _boardGeneratorOverride;
    private readonly List<IGameObserver> _observers = [];

    public SlotMachineBuilder WithTheme(ISlotThemeFactory themeFactory)
    {
        _themeFactory = themeFactory;
        return this;
    }

    public SlotMachineBuilder WithWallet(IWallet wallet)
    {
        _wallet = wallet;
        return this;
    }

    public SlotMachineBuilder WithPayoutRules(IPayoutRule payoutRules)
    {
        _payoutRules = payoutRules;
        return this;
    }

    public SlotMachineBuilder WithObservable(IGameObservable observable)
    {
        _observable = observable;
        return this;
    }

    public SlotMachineBuilder WithRandom(IRandomSource random)
    {
        _random = random;
        return this;
    }

    public SlotMachineBuilder WithBoardGenerator(IBoardGenerator boardGenerator)
    {
        _boardGeneratorOverride = boardGenerator;
        return this;
    }

    public SlotMachineBuilder WithInterpreter(CommandInterpreter interpreter)
    {
        _interpreter = interpreter;
        return this;
    }

    public SlotMachineBuilder AddObserver(IGameObserver observer)
    {
        _observers.Add(observer);
        return this;
    }

    public SlotMachine Build()
    {
        if (_themeFactory is null)
        {
            throw new InvalidOperationException("Theme factory is required.");
        }

        if (_wallet is null)
        {
            throw new InvalidOperationException("Wallet is required.");
        }

        if (_payoutRules is null)
        {
            throw new InvalidOperationException("Payout rules are required.");
        }

        var observable = _observable ?? new GameEventHub();
        foreach (var observer in _observers)
        {
            observable.Subscribe(observer);
        }

        var symbols = _themeFactory.CreateSymbolSet();
        var boardGenerator = _boardGeneratorOverride ?? _themeFactory.CreateBoardGenerator();
        var payTable = _themeFactory.CreatePayTable();
        var random = _random ?? new SeededRandomSource();

        var machine = new SlotMachine(
            _wallet,
            boardGenerator,
            payTable,
            symbols,
            _payoutRules,
            observable,
            random,
            _themeFactory.ThemeName);

        machine.AttachInterpreter(_interpreter ?? new CommandInterpreter());
        return machine;
    }
}
