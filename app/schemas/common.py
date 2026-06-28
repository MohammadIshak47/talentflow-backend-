from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: T
    message: str | None = None
    success: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int = 1
    per_page: int = 20
    total_pages: int = 1


def ok(data, message: str | None = None) -> dict:
    """Shortcut to build the {data, message, success} envelope the frontend expects."""
    return {"data": data, "message": message, "success": True}


def paginated(items: list, total: int, page: int = 1, per_page: int = 20) -> dict:
    total_pages = max(1, -(-total // per_page)) if per_page else 1
    return {"data": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}
