from typing import Generic, TypeVar, Type, Optional, Sequence
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: UUID) -> Optional[ModelT]:
        return await self.session.get(self.model, id_)

    async def list(self, *, limit: int = 20, offset: int = 0) -> Sequence[ModelT]:
        q = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()