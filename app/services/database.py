"""
Database service layer for common database operations.
"""

from typing import List, Optional, Type, TypeVar
from sqlalchemy.orm import Query
from app.core.extensions import db

ModelType = TypeVar("ModelType", bound=db.Model)


class BaseService:
    """Base service class for common database operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_all(self) -> List[ModelType]:
        """Get all records."""
        return self.model.query.all()

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        return self.model.query.get(id)

    def get_by_field(self, field: str, value) -> Optional[ModelType]:
        """Get record by field value."""
        return self.model.query.filter(getattr(self.model, field) == value).first()

    def create(self, **kwargs) -> ModelType:
        """Create new record."""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record by ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.session.commit()
        return instance

    def delete(self, id: int) -> bool:
        """Delete record by ID."""
        instance = self.get_by_id(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False

    def paginate(self, page: int = 1, per_page: int = 20) -> Query:
        """Paginate records."""
        return self.model.query.paginate(page=page, per_page=per_page, error_out=False)
