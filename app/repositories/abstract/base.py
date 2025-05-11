from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict, Optional, Any


T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
        @abstractmethod
        async def add(self, entity: T) -> T:
            """Add new entity to collection"""
            ...

        @abstractmethod
        async def update(self, entity: T, data: Dict[str, Any]) -> T:
            """Hard update and make sure that entity has been updated"""
            ...

        @abstractmethod
        async def delete(self, entity: T) -> None:
            """Remove entity from collection"""
            ...

        @abstractmethod
        async def list(
                self,
                skip: int = 0,
                limit: int = 100,
                order_by: Optional[str] = None,
                desc_order: bool = False,
                **filters: Any,
        ) -> List[T]:
            """Get list of entities"""
            ...

        @abstractmethod
        async def exists(self, _id: Any) -> bool:
            """Check entity exists"""
            ...

        @abstractmethod
        async def count(self) -> int:
            """Get general count of entities"""
            ...

        @abstractmethod
        async def get_by_id(self, _id: Any) -> Optional[T]:
            """Get entity by unique identifier"""
            ...
