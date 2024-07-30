from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AuthUser(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    notes = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    scopes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True))


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    bucket_name = Column(String)
    access_key_id = Column(String)
    secret_access_key = Column(String)
    media_prefix = Column(String)
    grid_view = Column(Boolean, default=False)


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    source_id = Column(
        Integer,
        ForeignKey("source.id", name="item_source_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )
    mime_type = Column(String(100))
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    notes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)


class TagItem(Base):
    __tablename__ = "tag_item"

    id = Column(Integer, primary_key=True)
    tag_id = Column(
        Integer,
        ForeignKey("tag.id", name="tag_item_tag_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )
    item_id = Column(
        Integer,
        ForeignKey("item.id", name="tag_item_item_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )
