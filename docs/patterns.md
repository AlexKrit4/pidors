# Pattern Mapping — Pirate Parrots Slots

Отчёт о применении паттернов проектирования в проекте **Pirate Parrots Slots** (C# / .NET 9).

Игра — слот с полем **7×6**, четырьмя цветными попугаями и каскадным сбором кристаллов. Механика выплат строится вокруг `CollectionEngine`, а не вокруг классических paylines.

---

## Abstract Factory

**Назначение:** создавать согласованное семейство объектов для выбранной темы слота.

**Где в коде:** `src/ParrotSlots/Themes/`

| Элемент | Файл |
|---------|------|
| Интерфейс фабрики | `ISlotThemeFactory.cs` |
| Базовая реализация | `SlotThemeFactoryBase.cs` |
| Основная тема | `PirateParrotThemeFactory.cs` |
| Демо-тема | `JungleParrotThemeFactory.cs` |

**Создаваемые продукты:**

- `ISymbolSet` — набор попугаев и кристаллов (4 цвета, уровни кристаллов 1–7)
- `IPayTable` — таблица множителей выплат по цвету и уровню кристалла
- `IBoardGenerator` — генератор стартового поля 7×6 с фиксированным числом попугаев

```csharp
public interface ISlotThemeFactory
{
    string ThemeName { get; }
    ISymbolSet CreateSymbolSet();
    IPayTable CreatePayTable();
    IBoardGenerator CreateBoardGenerator();
}
```

**Как используется:** `SlotMachineBuilder.WithTheme(...)` передаёт фабрику в сборку. При `Build()` создаются все три продукта одной темы, чтобы символы, выплаты и генератор поля не конфликтовали друг с другом.

**Две фабрики:**

- `PirateParrotThemeFactory` — тема по умолчанию («Pirate Parrots»)
- `JungleParrotThemeFactory` — вторая демонстрационная тема («Jungle Parrots»); использует те же механики и множители через общий базовый класс, меняется только имя темы

---

## Singleton

**Назначение:** единая точка доступа к неизменяемым игровым константам.

**Где в коде:** `src/ParrotSlots/Settings/GameSettings.cs`

```csharp
private static readonly Lazy<GameSettings> LazyInstance = new(() => new GameSettings());
public static GameSettings Instance => LazyInstance.Value;
```

**Хранимые настройки:**

| Свойство | Значение | Описание |
|----------|----------|----------|
| `ColCount` | 6 | Ширина поля |
| `RowCount` | 7 | Высота поля |
| `ParrotCount` | 4 | Число попугаев на поле при генерации |
| `MaxCrystalLevel` | 7 | Максимальный уровень кристалла |
| `StartingBalance` | 1000 | Стартовый баланс |
| `MinBet` / `MaxBet` | 1 / 100 | Диапазон ставки |
| `DefaultBet` | 10 | Ставка по умолчанию |

Конструктор приватный — экземпляр создаётся один раз через `Lazy<T>`.

**Где читается:** `WalletProxy` (лимиты ставки), `SlotMachine.GetRulesText()`, UI-приложения (Raylib, Terminal, Chafa).

> В этой игре нет «количества линий» — выплаты считаются через сбор кристаллов попугаями, а не через paylines.

---

## Builder

**Назначение:** пошаговая сборка сложного объекта `SlotMachine` без перегруженного конструктора.

**Где в коде:** `src/ParrotSlots/Builder/`

| Класс | Роль |
|-------|------|
| `SlotMachineBuilder` | Fluent-сборка: тема, кошелёк, правила, observable, RNG, interpreter, observers |
| `DefaultGameDirector` | Готовый «рецепт» стандартной игры для `Program.cs` |

**Цепочка сборки в `DefaultGameDirector.CreateStandardGame()`:**

1. `GameSettings.Instance` — константы
2. `GameEventHub` — шина событий
3. `WalletProxy(new PlayerWallet(...), hub)` — кошелёк с проверками
4. `PayoutRuleGroup("All Rules", [new CrystalCollectionRule()])` — правила выплат
5. `SlotMachineBuilder` — тема, кошелёк, правила, observable, interpreter
6. Observers: `ConsoleRenderer`, `StatisticsTracker`, `GameLogger`
7. `builder.Build()` → `SlotMachine`

**Точки входа:**

- `--text` → `DefaultGameDirector().CreateStandardGame()` + текстовый REPL
- `--terminal` / Raylib → `TerminalGameBootstrap` со своей сборкой на том же builder

---

## Composite

**Назначение:** единый интерфейс для отдельного правила выплат и для группы правил.

**Где в коде:** `src/ParrotSlots/Rules/`

| Элемент | Файл | Роль |
|---------|------|------|
| `IPayoutRule` | `IPayoutRule.cs` | Общий контракт: `Evaluate(PayoutContext)` |
| `CrystalCollectionRule` | `CrystalCollectionRule.cs` | Лист: запускает `CollectionEngine` |
| `PayoutRuleGroup` | `PayoutRuleGroup.cs` | Компоновщик: суммирует выигрыши дочерних правил |

```csharp
public interface IPayoutRule
{
    string Name { get; }
    PayoutResult Evaluate(PayoutContext context);
}
```

**Лист — `CrystalCollectionRule`:**

- Делегирует расчёт `CollectionEngine`
- Попугай собирает достижимые кристаллы своего цвета → каскад (падение + дозаполнение) → начисление по `IPayTable`

**Компоновщик — `PayoutRuleGroup`:**

- Хранит список `IPayoutRule`
- При `Evaluate()` вызывает каждое дочернее правило и суммирует `WinAmount`

Клиент (`SlotMachine.Spin()`) всегда вызывает `_payoutRules.Evaluate(context)` — неважно, передано одно правило или группа.

> В текущей версии единственный leaf — `CrystalCollectionRule`. Архитектура Composite позволяет добавить новые правила (например, бонус за комбо) без изменения `SlotMachine`.

---

## Proxy

**Назначение:** контроль доступа к кошельку и уведомление наблюдателей без усложнения `PlayerWallet`.

**Где в коде:** `src/ParrotSlots/Wallet/`

| Элемент | Класс | Роль |
|---------|-------|------|
| Интерфейс | `IWallet` | Контракт кошелька |
| Реальный объект | `PlayerWallet` | Хранит баланс и ставку, списывает/начисляет |
| Заместитель | `WalletProxy` | Валидация + события |

**Проверки в `WalletProxy`:**

- `TrySetBet` — ставка не ниже `MinBet`, не выше `MaxBet`, не больше баланса
- `TryDeductBet` — запрет списания при нехватке средств
- При успехе — `NotifyBalanceChanged` через `IGameObservable`
- При ошибке — `NotifyCommandFailed`

`SlotMachine` работает только с `IWallet` и не знает, используется ли прокси.

---

## Interpreter

**Назначение:** разбор текстовых команд игрока в режиме `--text`.

**Где в коде:** `src/ParrotSlots/Interpreter/`

| Файл | Содержимое |
|------|------------|
| `CommandInterpreter.cs` | Парсер и точка входа `Execute(input, game)` |
| `CommandExpressions.cs` | Классы выражений |
| `ICommandExpression.cs` | `Execute(SlotMachine game) → CommandResult` |

**Грамматика:**

```
program  ::= command (';' command)*
command  ::= spin
           | auto INT
           | bet INT
           | balance
           | rules
           | quit
```

**Выражения:**

| Команда | Класс |
|---------|-------|
| `spin` | `SpinExpression` |
| `auto N` | `AutoSpinExpression` |
| `bet N` | `BetExpression` |
| `balance` | `BalanceExpression` |
| `rules` | `RulesExpression` |
| `quit` | `QuitExpression` |
| `cmd1; cmd2; ...` | `SequenceExpression` |

`CommandInterpreter` разбивает строку по `;`, парсит каждую часть и выполняет одно выражение или `SequenceExpression`.

---

## Observer

**Назначение:** слабая связь между игровой логикой и подписчиками (лог, статистика, консольный вывод).

**Где в коде:** `src/ParrotSlots/Observer/`

| Элемент | Класс / тип |
|---------|-------------|
| Издатель | `IGameObservable` |
| Реализация шины | `GameEventHub` |
| Подписчик | `IGameObserver` |
| Тип события | `GameEventType` / `GameEvent` |

**События:**

| Событие | Кто публикует | Когда |
|---------|---------------|-------|
| `SpinStarted` | `SlotMachine` | Начало спина |
| `SpinFinished` | `SlotMachine` | Конец спина с `SpinResult` |
| `BalanceChanged` | `WalletProxy` | Изменение ставки или баланса |
| `CommandFailed` | `WalletProxy` | Отклонённая ставка / списание |
| `ModifierTriggered` | — | Объявлено в API; в текущем геймплее не вызывается |

**Наблюдатели (подключаются в `DefaultGameDirector`):**

| Класс | Назначение |
|-------|------------|
| `ConsoleRenderer` | Вывод спина, поля, выигрыша, ошибок в консоль |
| `StatisticsTracker` | Счётчики спинов, ставок, выигрышей, ошибок |
| `GameLogger` | Журнал событий с меткой времени |

UI-режимы (Terminal, Raylib, Chafa) используют отдельный `TerminalUiObserver`, но тот же механизм `IGameObserver`.

---

## Игровой цикл (связь паттернов)

```
Program.cs
  └─ DefaultGameDirector          [Builder]
       └─ PirateParrotThemeFactory [Abstract Factory]
            → ISymbolSet, IPayTable, IBoardGenerator
       └─ WalletProxy(PlayerWallet) [Proxy]
       └─ PayoutRuleGroup → CrystalCollectionRule [Composite]
       └─ GameEventHub + observers  [Observer]

Игрок: spin
  └─ SlotMachine.Spin()
       ├─ WalletProxy.TryDeductBet()     → BalanceChanged / CommandFailed
       ├─ NotifySpinStarted()
       ├─ IBoardGenerator.CreateBoard()
       ├─ IPayoutRule.Evaluate()         → CollectionEngine (каскады)
       ├─ WalletProxy.AddWin()
       └─ NotifySpinFinished()
```

---

## Сводная таблица

| Паттерн | Ключевые типы | Папка |
|---------|---------------|-------|
| Abstract Factory | `ISlotThemeFactory`, `PirateParrotThemeFactory`, `JungleParrotThemeFactory` | `Themes/` |
| Singleton | `GameSettings.Instance` | `Settings/` |
| Builder | `SlotMachineBuilder`, `DefaultGameDirector` | `Builder/` |
| Composite | `IPayoutRule`, `CrystalCollectionRule`, `PayoutRuleGroup` | `Rules/` |
| Proxy | `IWallet`, `PlayerWallet`, `WalletProxy` | `Wallet/` |
| Interpreter | `CommandInterpreter`, `*Expression` | `Interpreter/` |
| Observer | `IGameObservable`, `IGameObserver`, `GameEventHub` | `Observer/` |

---

## Тесты

Покрытие паттернов в `tests/ParrotSlots.Tests/`:

- `ThemeFactoryTests` — Abstract Factory
- `GameSettingsTests` — Singleton
- `SlotMachineBuilderTests` — Builder
- `PayoutRuleGroupTests` — Composite
- `WalletProxyTests` — Proxy
- `CommandInterpreterTests` — Interpreter
- `ObserverTests` — Observer
