# План выступления на 5 человек

Цель распределения: 4 человека рассказывают 7 паттернов из документации, один человек рассказывает общую механику игры и центральный класс `SlotMachine`. Нагрузка выровнена по количеству смысловых блоков: у первых трёх участников по 2 паттерна, у четвёртого один более глубокий паттерн с разбором грамматики команд, у пятого полный игровой цикл.

## Общее распределение

| Участник | Тема | Нагрузка |
|----------|------|----------|
| Участник 1 | Abstract Factory + Singleton | 2 паттерна: тема игры, продукты темы, глобальные настройки |
| Участник 2 | Builder + Proxy | 2 паттерна: сборка `SlotMachine`, кошелёк и проверки ставок |
| Участник 3 | Composite + Observer | 2 паттерна: правила выплат и событийная модель |
| Участник 4 | Interpreter | 1 паттерн, но глубокий разбор: грамматика, expression-классы, выполнение команд |
| Участник 5 | Как работает игра в целом | игровой цикл, `SlotMachine`, генерация поля, сбор кристаллов, каскады, анимация |

## Участник 1 — Abstract Factory и Singleton

### Что рассказывать

Участник объясняет, как игра отделяет тему слота от остальной логики. В проекте тема не просто задаёт название: она создаёт согласованное семейство объектов, без которых игра не сможет корректно запуститься.

Нужно показать, что `ISlotThemeFactory` создаёт три связанных продукта:

- `ISymbolSet` — отображения попугаев и кристаллов;
- `IPayTable` — таблицу выплат;
- `IBoardGenerator` — генератор стартового поля.

Затем нужно объяснить `GameSettings` как Singleton: настройки игры существуют в одном экземпляре и используются из разных частей проекта.

### Abstract Factory

**Идея паттерна:** создать семейство связанных объектов через общий фабричный интерфейс, чтобы клиентский код не зависел от конкретной темы.

**Код:**

- [ISlotThemeFactory.cs](../src/ParrotSlots/Themes/ISlotThemeFactory.cs) — интерфейс фабрики темы.
- [SlotThemeFactoryBase.cs](../src/ParrotSlots/Themes/SlotThemeFactoryBase.cs) — базовая реализация общих множителей и набора символов.
- [PirateParrotThemeFactory.cs](../src/ParrotSlots/Themes/PirateParrotThemeFactory.cs) — основная тема.
- [JungleParrotThemeFactory.cs](../src/ParrotSlots/Themes/JungleParrotThemeFactory.cs) — альтернативная демонстрационная тема.
- [ISymbolSet.cs](../src/ParrotSlots/Core/ISymbolSet.cs) — продукт фабрики: набор символов.
- [IPayTable.cs](../src/ParrotSlots/Core/IPayTable.cs) — продукт фабрики: таблица выплат.
- [IBoardGenerator.cs](../src/ParrotSlots/Core/IBoardGenerator.cs) — продукт фабрики: генератор поля.
- [SymbolSet.cs](../src/ParrotSlots/Core/SymbolSet.cs), [PayTable.cs](../src/ParrotSlots/Core/PayTable.cs), [BoardGenerator.cs](../src/ParrotSlots/Core/BoardGenerator.cs) — конкретные продукты.

**Как реализовано:**

`ISlotThemeFactory` задаёт контракт:

- `CreateSymbolSet()`;
- `CreatePayTable()`;
- `CreateBoardGenerator()`;
- `ThemeName`.

`PirateParrotThemeFactory` и `JungleParrotThemeFactory` реализуют один и тот же интерфейс. Поэтому `SlotMachineBuilder` может принимать любую тему через `WithTheme(...)` и не знать, какая конкретно фабрика используется.

**Что показать в коде:**

- в [SlotMachineBuilder.cs](../src/ParrotSlots/Builder/SlotMachineBuilder.cs) метод `Build()` вызывает методы фабрики;
- в [DefaultGameDirector.cs](../src/ParrotSlots/Builder/DefaultGameDirector.cs) по умолчанию используется `PirateParrotThemeFactory`;
- замена фабрики не требует менять `SlotMachine`.

**Тесты:**

- [ThemeFactoryTests.cs](../tests/ParrotSlots.Tests/ThemeFactoryTests.cs) — проверяет, что обе фабрики создают согласованные продукты.

### Singleton

**Идея паттерна:** гарантировать один общий экземпляр настроек игры.

**Код:**

- [GameSettings.cs](../src/ParrotSlots/Settings/GameSettings.cs)

**Как реализовано:**

`GameSettings` имеет:

- приватный конструктор;
- статическое поле `Lazy<GameSettings>`;
- публичный доступ через `GameSettings.Instance`.

В настройках хранятся:

- `ColCount = 6`;
- `RowCount = 7`;
- `ParrotCount = 4`;
- `MaxCrystalLevel = 7`;
- начальный баланс;
- лимиты ставки.

**Где используется:**

- [WalletProxy.cs](../src/ParrotSlots/Wallet/WalletProxy.cs) — проверка min/max ставки.
- [BoardGenerator.cs](../src/ParrotSlots/Core/BoardGenerator.cs) — размер поля и число попугаев.
- [SlotMachine.cs](../src/ParrotSlots/SlotMachine.cs) — текст правил.

**Тесты:**

- [GameSettingsTests.cs](../tests/ParrotSlots.Tests/GameSettingsTests.cs) — проверяет, что `Instance` возвращает один и тот же объект.

## Участник 2 — Builder и Proxy

### Что рассказывать

Участник показывает, как собирается сложный объект `SlotMachine` и как кошелёк игрока защищён через прокси. Это часть про создание игры и безопасную работу со ставками.

### Builder

**Идея паттерна:** пошагово собрать сложный объект без огромного конструктора и без дублирования конфигурации.

**Код:**

- [SlotMachineBuilder.cs](../src/ParrotSlots/Builder/SlotMachineBuilder.cs)
- [DefaultGameDirector.cs](../src/ParrotSlots/Builder/DefaultGameDirector.cs)
- [TerminalGameBootstrap.cs](../src/ParrotSlots/Terminal/TerminalGameBootstrap.cs)
- [SlotMachine.cs](../src/ParrotSlots/SlotMachine.cs)

**Как реализовано:**

`SlotMachineBuilder` хранит параметры сборки:

- тему;
- кошелёк;
- правила выплат;
- observable-шину;
- генератор случайных чисел;
- interpreter;
- observers.

Методы вида `WithTheme`, `WithWallet`, `WithPayoutRules`, `WithObservable`, `WithRandom`, `WithInterpreter`, `AddObserver` возвращают сам builder, поэтому можно строить цепочку вызовов.

Метод `Build()`:

- проверяет обязательные зависимости;
- подписывает observers на `GameEventHub`;
- получает продукты темы через `ISlotThemeFactory`;
- создаёт `SlotMachine`;
- подключает `CommandInterpreter`.

`DefaultGameDirector` — готовый сценарий сборки стандартной игры.

**Что показать в коде:**

- цепочку вызовов в `DefaultGameDirector.CreateStandardGame()`;
- проверки обязательных зависимостей в `SlotMachineBuilder.Build()`;
- отличие builder от прямого вызова конструктора `SlotMachine`.

**Тесты:**

- [SlotMachineBuilderTests.cs](../tests/ParrotSlots.Tests/SlotMachineBuilderTests.cs)

### Proxy

**Идея паттерна:** объект-заместитель контролирует доступ к реальному объекту и добавляет поведение, не меняя сам реальный объект.

**Код:**

- [IWallet.cs](../src/ParrotSlots/Wallet/IWallet.cs) — общий контракт.
- [PlayerWallet.cs](../src/ParrotSlots/Wallet/PlayerWallet.cs) — реальный кошелёк.
- [WalletProxy.cs](../src/ParrotSlots/Wallet/WalletProxy.cs) — прокси.
- [GameSettings.cs](../src/ParrotSlots/Settings/GameSettings.cs) — лимиты ставок.
- [IGameObservable.cs](../src/ParrotSlots/Observer/IGameObservable.cs) — уведомления о балансе и ошибках.

**Как реализовано:**

`PlayerWallet` просто хранит баланс и текущую ставку.

`WalletProxy` реализует тот же `IWallet`, но перед вызовом реального кошелька:

- запрещает ставку ниже `MinBet`;
- запрещает ставку выше `MaxBet`;
- запрещает ставку больше баланса;
- запрещает спин при недостатке средств;
- уведомляет observers через `NotifyBalanceChanged`;
- отправляет ошибки через `NotifyCommandFailed`.

`SlotMachine` работает только с `IWallet`, поэтому он не зависит от того, передан настоящий кошелёк или proxy.

**Что показать в коде:**

- `WalletProxy.TrySetBet(...)`;
- `WalletProxy.TryDeductBet(...)`;
- использование `_wallet` в `SlotMachine.Spin()`.

**Тесты:**

- [WalletProxyTests.cs](../tests/ParrotSlots.Tests/WalletProxyTests.cs)

## Участник 3 — Composite и Observer

### Что рассказывать

Участник отвечает за правила выплат и событийную модель. Нужно показать, как игра вычисляет выигрыш через единый интерфейс правил и как разные части UI/логирования получают события без прямой зависимости от `SlotMachine`.

### Composite

**Идея паттерна:** одинаково работать и с одним правилом, и с группой правил через общий интерфейс.

**Код:**

- [IPayoutRule.cs](../src/ParrotSlots/Rules/IPayoutRule.cs) — общий компонент.
- [CrystalCollectionRule.cs](../src/ParrotSlots/Rules/CrystalCollectionRule.cs) — leaf-правило.
- [PayoutRuleGroup.cs](../src/ParrotSlots/Rules/PayoutRuleGroup.cs) — composite.
- [PayoutContext.cs](../src/ParrotSlots/Rules/PayoutContext.cs) — контекст расчёта.
- [PayoutResult.cs](../src/ParrotSlots/Rules/PayoutResult.cs) — результат расчёта.
- [CollectionEngine.cs](../src/ParrotSlots/Core/CollectionEngine.cs) — механика сбора кристаллов.

**Как реализовано:**

`IPayoutRule` задаёт метод `Evaluate(PayoutContext context)`.

`CrystalCollectionRule` — отдельное правило, которое запускает `CollectionEngine`.

`PayoutRuleGroup` хранит список `IPayoutRule`, вызывает каждое дочернее правило и суммирует:

- общий выигрыш;
- сообщения о сборе кристаллов.

Для `SlotMachine` не важно, одно правило передано или группа правил: он вызывает `_payoutRules.Evaluate(context)`.

**Что показать в коде:**

- `PayoutRuleGroup.Evaluate(...)`;
- `CrystalCollectionRule.Evaluate(...)`;
- вызов `_payoutRules.Evaluate(...)` в `SlotMachine.Spin()`;
- создание `new PayoutRuleGroup("All Rules", [new CrystalCollectionRule()])` в `DefaultGameDirector`.

**Тесты:**

- [PayoutRuleGroupTests.cs](../tests/ParrotSlots.Tests/PayoutRuleGroupTests.cs)
- [CollectionEngineTests.cs](../tests/ParrotSlots.Tests/CollectionEngineTests.cs)

### Observer

**Идея паттерна:** отделить источник событий от подписчиков. `SlotMachine` и `WalletProxy` публикуют события, а UI, логгер и статистика реагируют независимо.

**Код:**

- [IGameObservable.cs](../src/ParrotSlots/Observer/IGameObservable.cs) — издатель.
- [IGameObserver.cs](../src/ParrotSlots/Observer/IGameObserver.cs) — подписчик.
- [GameEventHub.cs](../src/ParrotSlots/Observer/GameEventHub.cs) — шина событий.
- [GameEvent.cs](../src/ParrotSlots/Observer/GameEvent.cs) — тип события.
- [ConsoleRenderer.cs](../src/ParrotSlots/Observer/ConsoleRenderer.cs) — консольный вывод.
- [StatisticsTracker.cs](../src/ParrotSlots/Observer/StatisticsTracker.cs) — статистика.
- [GameLogger.cs](../src/ParrotSlots/Observer/GameLogger.cs) — лог событий.
- [TerminalUiObserver.cs](../src/ParrotSlots/Terminal/TerminalUiObserver.cs) — обновление terminal UI.

**Как реализовано:**

`GameEventHub` хранит список `IGameObserver` и публикует события:

- `SpinStarted`;
- `SpinFinished`;
- `BalanceChanged`;
- `CommandFailed`;
- `ModifierTriggered`.

`SlotMachine` отправляет события начала и конца спина.

`WalletProxy` отправляет события изменения баланса и ошибки команд.

Подписчики ничего не знают о внутренностях `SlotMachine`, они получают только `GameEvent`.

**Что показать в коде:**

- `GameEventHub.Subscribe(...)`;
- `GameEventHub.NotifySpinStarted(...)`;
- `SlotMachine.Spin()` и `SlotMachine.BeginAnimatedSpin()`;
- `WalletProxy.NotifyCommandFailed(...)`;
- `StatisticsTracker.OnGameEvent(...)`;
- `TerminalUiObserver.OnGameEvent(...)`.

**Тесты:**

- [ObserverTests.cs](../tests/ParrotSlots.Tests/ObserverTests.cs)

## Участник 4 — Interpreter

### Что рассказывать

Участник отвечает за текстовый интерфейс команд. Хотя это один паттерн, нагрузка сопоставима с двумя маленькими паттернами, потому что нужно объяснить грамматику, парсер, expression-классы и выполнение цепочек команд.

### Interpreter

**Идея паттерна:** представить команды как объекты выражений, которые умеют выполнять себя над контекстом игры.

**Код:**

- [CommandInterpreter.cs](../src/ParrotSlots/Interpreter/CommandInterpreter.cs) — парсер.
- [ICommandExpression.cs](../src/ParrotSlots/Interpreter/ICommandExpression.cs) — общий интерфейс выражения.
- [CommandExpressions.cs](../src/ParrotSlots/Interpreter/CommandExpressions.cs) — конкретные выражения.
- [CommandResult.cs](../src/ParrotSlots/Interpreter/CommandResult.cs) — результат команды.
- [Program.cs](../src/ParrotSlots/Program.cs) — текстовый режим `--text`.
- [SlotMachine.cs](../src/ParrotSlots/SlotMachine.cs) — контекст, над которым выполняются команды.

**Грамматика:**

```text
program  ::= command (';' command)*
command  ::= spin
           | auto INT
           | bet INT
           | balance
           | rules
           | quit
```

**Как реализовано:**

`CommandInterpreter.Execute(input, game)`:

1. Разбивает строку по `;`.
2. Для каждой части вызывает `ParseCommand`.
3. Создаёт конкретный `ICommandExpression`.
4. Если команд несколько, оборачивает их в `SequenceExpression`.
5. Вызывает `program.Execute(game)`.

Конкретные выражения:

- `SpinExpression` вызывает `game.Spin()`;
- `AutoSpinExpression` запускает несколько спинов;
- `BetExpression` меняет ставку;
- `BalanceExpression` возвращает баланс;
- `RulesExpression` возвращает правила;
- `QuitExpression` завершает цикл;
- `SequenceExpression` выполняет цепочку команд.

**Что показать в коде:**

- `ParseCommand(...)` в `CommandInterpreter`;
- `SpinExpression.Execute(...)`;
- `BetExpression.Execute(...)`;
- `SequenceExpression.Execute(...)`;
- цикл `RunGameLoop(...)` в `Program.cs`.

**Тесты:**

- [CommandInterpreterTests.cs](../tests/ParrotSlots.Tests/CommandInterpreterTests.cs)

## Участник 5 — как работает игра в целом

### Что рассказывать

Этот участник не разбирает отдельный паттерн, а связывает всё в единую историю: как игрок запускает спин, как строится поле, как попугаи собирают кристаллы, как считается выигрыш и как запускается анимация.

### Центральные файлы

- [Program.cs](../src/ParrotSlots/Program.cs) — выбор режима запуска: `--text`, `--terminal`, Raylib.
- [SlotMachine.cs](../src/ParrotSlots/SlotMachine.cs) — главный класс игровой логики.
- [BoardGenerator.cs](../src/ParrotSlots/Core/BoardGenerator.cs) — генерация стартового поля.
- [GameBoard.cs](../src/ParrotSlots/Core/GameBoard.cs) — представление поля.
- [Cell.cs](../src/ParrotSlots/Core/Cell.cs) — кристалл, попугай или пустая клетка.
- [CollectionEngine.cs](../src/ParrotSlots/Core/CollectionEngine.cs) — сбор кристаллов и каскады для обычного спина.
- [SpinPlanner.cs](../src/ParrotSlots/Core/Animation/SpinPlanner.cs) — план фаз для анимированного спина.
- [CascadePlanner.cs](../src/ParrotSlots/Core/Animation/CascadePlanner.cs) — падение и дозаполнение клеток.
- [AnimatedSpinSession.cs](../src/ParrotSlots/AnimatedSpinSession.cs) — сессия анимированного спина.
- [SpinPlaybackController.cs](../src/ParrotSlots/Graphics/SpinPlaybackController.cs) — проигрывание фаз анимации.
- [TerminalGameApplication.cs](../src/ParrotSlots/Terminal/TerminalGameApplication.cs) — terminal UI.
- [ChafaConsoleApplication.cs](../src/ParrotSlots/Terminal/ChafaConsoleApplication.cs) — полноэкранный Chafa-режим.
- [RaylibGameApplication.cs](../src/ParrotSlots/Graphics/RaylibGameApplication.cs) — графический Raylib-режим.

### Обычный спин

Путь выполнения:

1. Игрок вводит команду или нажимает кнопку.
2. `SlotMachine.Spin()` проверяет и списывает ставку через `IWallet`.
3. `SlotMachine` публикует `SpinStarted`.
4. `IBoardGenerator.CreateBoard(...)` создаёт поле 7×6.
5. `PayoutContext` собирает поле, ставку, таблицу выплат, символы и random.
6. `_payoutRules.Evaluate(context)` запускает правила выплат.
7. `CrystalCollectionRule` вызывает `CollectionEngine`.
8. `CollectionEngine` двигает попугаев к достижимым кристаллам своего цвета.
9. После сбора запускаются каскады: пустые клетки заполняются новыми кристаллами.
10. `WalletProxy.AddWin(...)` начисляет выигрыш.
11. `SlotMachine` сохраняет `LastBoard` и публикует `SpinFinished`.

### Анимированный спин

Путь выполнения:

1. UI вызывает `SlotMachine.BeginAnimatedSpin()`.
2. Ставка списывается сразу.
3. `SpinPlanner.Build(...)` строит список фаз:
   - `DropInPhase`;
   - `ParrotStepPhase`;
   - `CascadePhase`.
4. `AnimatedSpinSession` хранит план и итоговый выигрыш.
5. `SpinPlaybackController` по кадрам выдаёт текущее отображаемое поле.
6. Когда проигрывание завершается, `AnimatedSpinSession.MarkCompleted()` вызывает `SlotMachine.CompleteAnimatedSpin(...)`.
7. Выигрыш начисляется, публикуется `SpinFinished`.

### Что важно объяснить

- `SlotMachine` не знает деталей UI.
- `SlotMachine` не создаёт тему напрямую, она приходит через builder и factory.
- Кошелёк доступен через `IWallet`, поэтому проверки вынесены в proxy.
- Расчёт выплат идёт через `IPayoutRule`, поэтому можно добавлять новые правила.
- UI получает состояние через Observer, а не через прямую связанность.
- Text mode использует Interpreter, terminal/Raylib режимы используют те же игровые классы.

### Тесты для общей механики

- [CollectionEngineTests.cs](../tests/ParrotSlots.Tests/CollectionEngineTests.cs)
- [SpinPlannerTests.cs](../tests/ParrotSlots.Tests/SpinPlannerTests.cs)
- [SlotMachineBuilderTests.cs](../tests/ParrotSlots.Tests/SlotMachineBuilderTests.cs)

## Рекомендуемый порядок выступления

1. Участник 5: коротко объясняет, что это за игра и какой общий игровой цикл.
2. Участник 1: показывает тему, фабрики и настройки.
3. Участник 2: показывает, как игра собирается и как защищён кошелёк.
4. Участник 3: показывает правила выплат и события.
5. Участник 4: показывает текстовый язык команд.
6. Участник 5: завершает связкой: как все паттерны вместе работают внутри `SlotMachine`.

## Короткая шпаргалка по связям паттернов

```text
Program
  -> DefaultGameDirector / TerminalGameBootstrap       [Builder]
  -> SlotMachineBuilder
      -> PirateParrotThemeFactory                      [Abstract Factory]
      -> WalletProxy(PlayerWallet)                     [Proxy]
      -> PayoutRuleGroup(CrystalCollectionRule)        [Composite]
      -> GameEventHub + observers                      [Observer]
      -> CommandInterpreter + expressions              [Interpreter]

SlotMachine
  -> IBoardGenerator.CreateBoard()
  -> IPayoutRule.Evaluate()
  -> WalletProxy.AddWin()
  -> GameEventHub.NotifySpinFinished()
```
