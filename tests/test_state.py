from restart_safe_agents.state import TaskComplexity


def test_task_complexity_values():
    assert TaskComplexity.SIMPLE.value == "simple"
    assert TaskComplexity.COMPLEX.value == "complex"
    assert TaskComplexity.IMPOSSIBLE.value == "impossible"
