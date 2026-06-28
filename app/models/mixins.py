import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


def gen_uuid() -> str:
    return str(uuid.uuid4())


class UUIDPkMixin:
    """Gives every model a string UUID primary key, matching the `id: string`
    shape the frontend's TypeScript types expect."""

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
