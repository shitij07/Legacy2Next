from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.core.database import Base


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    category = Column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "category", name="uq_technology_name_category"),
    )
