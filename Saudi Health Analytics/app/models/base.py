"""
Base Model Class
Provides common fields and methods for all database models
"""

from datetime import datetime
from app import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, DateTime, String


class BaseModel(db.Model):
    """
    Base model class with common fields and methods
    All other models inherit from this class
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name"""
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def save(self, commit=True):
        """Save the model instance to database"""
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        return False
    
    def delete(self, commit=True):
        """Delete the model instance from database"""
        db.session.delete(self)
        if commit:
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        return False
    
    def update(self, **kwargs):
        """Update model instance with provided data"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self.save()
    
    def to_dict(self, include_relationships=False):
        """Convert model instance to dictionary"""
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Handle different data types
            if isinstance(value, datetime):
                data[column.name] = value.isoformat()
            else:
                data[column.name] = value
        
        if include_relationships:
            # Include relationship data
            for relationship in self.__mapper__.relationships:
                related_data = getattr(self, relationship.key)
                if related_data is not None:
                    if hasattr(related_data, '__iter__') and not isinstance(related_data, str):
                        # One-to-many or many-to-many relationship
                        data[relationship.key] = [
                            item.to_dict() if hasattr(item, 'to_dict') else str(item)
                            for item in related_data
                        ]
                    else:
                        # One-to-one relationship
                        data[relationship.key] = (
                            related_data.to_dict() if hasattr(related_data, 'to_dict') 
                            else str(related_data)
                        )
        
        return data
    
    @classmethod
    def find_by_id(cls, id):
        """Find model instance by ID"""
        return cls.query.get(id)
    
    @classmethod
    def find_all(cls):
        """Get all instances of the model"""
        return cls.query.all()
    
    @classmethod
    def find_by(cls, **kwargs):
        """Find model instances by specified criteria"""
        return cls.query.filter_by(**kwargs).all()
    
    @classmethod
    def find_one_by(cls, **kwargs):
        """Find single model instance by specified criteria"""
        return cls.query.filter_by(**kwargs).first()
    
    @classmethod
    def count(cls):
        """Get count of all instances"""
        return cls.query.count()
    
    @classmethod
    def paginate(cls, page=1, per_page=20, **filters):
        """Get paginated results"""
        query = cls.query
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    def __repr__(self):
        """String representation of the model"""
        return f'<{self.__class__.__name__} {self.id}>' 