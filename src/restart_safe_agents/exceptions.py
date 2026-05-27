class RestartSafeAgentsError(Exception):
    """Base exception for restart-safe-agents."""


class MarginCallError(RestartSafeAgentsError):
    def __init__(self, task_id: str, spent: float, limit: float):
        self.task_id = task_id
        self.spent = spent
        self.limit = limit
        super().__init__(
            f"Margin call on task {task_id}: spent ${spent:.4f}, limit ${limit:.4f}"
        )


class ReviewLoopError(RestartSafeAgentsError):
    def __init__(self, task_id: str, bounces: int):
        self.task_id = task_id
        self.bounces = bounces
        super().__init__(f"Review loop breaker on task {task_id}: {bounces} bounces")


class EscalationError(RestartSafeAgentsError):
    def __init__(self, task_id: str, reason: str):
        self.task_id = task_id
        self.reason = reason
        super().__init__(f"Escalation on task {task_id}: {reason}")
