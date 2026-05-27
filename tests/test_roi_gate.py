import pytest

from restart_safe_agents.exceptions import MarginCallError
from restart_safe_agents.safety.roi_gate import ROIGate


def test_roi_gate_allows_profitable_task():
    gate = ROIGate(min_ratio=0.5, tokens_per_dollar=1000)
    cost = gate.evaluate({"task_id": "t1", "bounty_usd": 10.0}, estimated_tokens=1000)
    assert cost == 1.0


def test_roi_gate_blocks_loss_making_task():
    gate = ROIGate(min_ratio=0.2, tokens_per_dollar=1000)
    with pytest.raises(MarginCallError):
        gate.evaluate({"task_id": "t2", "bounty_usd": 2.0}, estimated_tokens=1000)
