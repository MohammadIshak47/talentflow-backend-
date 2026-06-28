from pydantic import BaseModel


class FunnelStage(BaseModel):
    stage: str
    count: int
    color: str


class MonthlyData(BaseModel):
    month: str
    apps: int


class AnalyticsData(BaseModel):
    funnel: list[FunnelStage]
    over_time: list[MonthlyData]
    time_to_hire: float
    offer_acceptance: float
    active_jobs: int
    total_candidates: int


class DashboardStats(BaseModel):
    active_jobs: int
    total_candidates: int
    time_to_hire: float
    offer_acceptance: float
