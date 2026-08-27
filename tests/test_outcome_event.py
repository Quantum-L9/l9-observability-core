from l9_observability_core import EffectivenessSignal, OutcomeEvent, OutcomeKind

from .helpers import NOW, execution, trace


def test_outcome_is_observation_not_policy():
    event = OutcomeEvent(
        event_id="evt-o",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        outcome_kind=OutcomeKind.ARTIFACT_PRODUCED,
        success=True,
        effectiveness_signal=EffectivenessSignal.NOT_APPLICABLE,
    )
    assert not hasattr(event, "promotion_decision")
