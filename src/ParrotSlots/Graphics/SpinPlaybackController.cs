using ParrotSlots.Core;
using ParrotSlots.Core.Animation;

namespace ParrotSlots.Graphics;

public sealed class SpinPlaybackController
{
    private enum PlaybackStage
    {
        DropIn,
        ParrotStep,
        CascadeGravity,
        CascadeRefill,
        Done
    }

    private SpinPlan? _plan;
    private AnimatedSpinSession? _session;
    private int _phaseIndex;
    private PlaybackStage _stage;
    private CascadePhase? _cascade;
    private ParrotStepPhase? _parrotStep;
    private bool _parrotStepShowingAfter;

    public bool IsPlaying { get; private set; }
    public GameBoard DisplayBoard { get; private set; } = CreateEmptyBoard();
    public float[,] CellOffsetY { get; private set; } = new float[GameConstants.GridRows, GameConstants.GridCols];
    public (int Row, int Col)? MovingParrotFrom { get; private set; }
    public (int Row, int Col)? MovingParrotTo { get; private set; }
    public float MovingParrotT { get; private set; } = 1f;
    public ParrotColor? MovingParrotColor { get; private set; }

    public void Start(AnimatedSpinSession session, GameBoard? previousBoard, bool fallOutPrevious)
    {
        _ = previousBoard;
        _ = fallOutPrevious;

        _session = session;
        _plan = session.Plan;
        _phaseIndex = 0;
        _parrotStep = null;
        _parrotStepShowingAfter = false;
        IsPlaying = true;
        BeginCurrentPhase();
    }

    public void Update(float deltaSeconds)
    {
        _ = deltaSeconds;

        if (!IsPlaying || _plan is null)
        {
            return;
        }

        ClearMotionState();

        switch (_stage)
        {
            case PlaybackStage.DropIn:
                AdvancePhase();
                break;
            case PlaybackStage.ParrotStep:
                if (!_parrotStepShowingAfter)
                {
                    DisplayBoard = _parrotStep!.Board.Clone();
                    _parrotStepShowingAfter = true;
                }
                else
                {
                    _parrotStep = null;
                    _parrotStepShowingAfter = false;
                    AdvancePhase();
                }

                break;
            case PlaybackStage.CascadeGravity:
                DisplayBoard = _cascade!.Plan.AfterGravity.Clone();
                _stage = PlaybackStage.CascadeRefill;
                break;
            case PlaybackStage.CascadeRefill:
                DisplayBoard = _cascade!.Plan.FinalBoard.Clone();
                AdvancePhase();
                break;
            case PlaybackStage.Done:
                Finish();
                break;
        }
    }

    private void ClearMotionState()
    {
        Array.Clear(CellOffsetY, 0, CellOffsetY.Length);
        MovingParrotFrom = null;
        MovingParrotTo = null;
        MovingParrotColor = null;
        MovingParrotT = 1f;
    }

    private void BeginCurrentPhase()
    {
        if (_plan is null)
        {
            Finish();
            return;
        }

        if (_phaseIndex >= _plan.Phases.Count)
        {
            _stage = PlaybackStage.Done;
            return;
        }

        var phase = _plan.Phases[_phaseIndex];

        switch (phase)
        {
            case DropInPhase dropIn:
                DisplayBoard = dropIn.Board.Clone();
                _stage = PlaybackStage.DropIn;
                break;
            case ParrotStepPhase parrot:
                _parrotStep = parrot;
                _parrotStepShowingAfter = false;
                DisplayBoard = parrot.BoardBefore.Clone();
                _stage = PlaybackStage.ParrotStep;
                break;
            case CascadePhase cascade:
                _cascade = cascade;
                DisplayBoard = cascade.BoardBefore.Clone();
                _stage = PlaybackStage.CascadeGravity;
                break;
            default:
                AdvancePhase();
                break;
        }
    }

    private void AdvancePhase()
    {
        _phaseIndex++;
        BeginCurrentPhase();
    }

    private void Finish()
    {
        if (_session is not null && _plan is not null)
        {
            DisplayBoard = _plan.FinalBoard.Clone();
            _session.MarkCompleted();
        }

        IsPlaying = false;
        _session = null;
        _plan = null;
        _cascade = null;
        _parrotStep = null;
        _parrotStepShowingAfter = false;
    }

    private static GameBoard CreateEmptyBoard()
    {
        var cells = new Cell[GameConstants.GridRows, GameConstants.GridCols];
        for (var row = 0; row < GameConstants.GridRows; row++)
        {
            for (var col = 0; col < GameConstants.GridCols; col++)
            {
                cells[row, col] = Cell.Empty;
            }
        }

        return new GameBoard(cells);
    }
}
