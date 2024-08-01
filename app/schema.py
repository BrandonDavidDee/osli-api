from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import declarative_base, relationship, backref

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


class SourceBucket(Base):
    __tablename__ = "source_bucket"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    bucket_name = Column(String, nullable=False)
    access_key_id = Column(String, nullable=False)
    secret_access_key = Column(String, nullable=False)
    media_prefix = Column(String)
    grid_view = Column(Boolean, default=False)


class SourceVimeo(Base):
    __tablename__ = "source_vimeo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    client_identifier = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    grid_view = Column(Boolean, default=False)


class ItemBucket(Base):
    __tablename__ = "item_bucket"

    id = Column(Integer, primary_key=True, index=True)
    source_bucket_id = Column(
        Integer,
        ForeignKey(
            "source_bucket.id",
            name="item_bucket_source_bucket_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    title = Column(String)
    mime_type = Column(String(100))
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    notes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)


class ItemVimeo(Base):
    __tablename__ = "item_vimeo"

    id = Column(Integer, primary_key=True, index=True)
    source_vimeo_id = Column(
        Integer,
        ForeignKey(
            "source_vimeo.id",
            name="item_vimeo_source_vimeo_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    video_id = Column(String, nullable=False)
    title = Column(String)
    thumbnail = Column(String)
    notes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)


class TagItemBucket(Base):
    __tablename__ = "tag_item_bucket"

    id = Column(Integer, primary_key=True)
    tag_id = Column(
        Integer,
        ForeignKey("tag.id", name="tag_item_bucket_tag_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )
    item_bucket_id = Column(
        Integer,
        ForeignKey(
            "item_bucket.id",
            name="tag_item_bucket_item_bucket_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


class TagItemVimeo(Base):
    __tablename__ = "tag_item_vimeo"

    id = Column(Integer, primary_key=True)
    tag_id = Column(
        Integer,
        ForeignKey("tag.id", name="tag_item_vimeo_tag_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )
    item_vimeo_id = Column(
        Integer,
        ForeignKey(
            "item_vimeo.id",
            name="tag_item_vimeo_item_vimeo_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    items = relationship("GalleryItem", back_populates="gallery", cascade="all, delete-orphan")


class GalleryItem(Base):
    __tablename__ = "gallery_item"

    id = Column(Integer, primary_key=True, index=True)
    gallery_id = Column(
        Integer,
        ForeignKey(
            "gallery.id",
            name="gallery_item_gallery_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    item_bucket_id = Column(
        Integer,
        ForeignKey(
            "item_bucket.id",
            name="gallery_item_item_bucket_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    item_vimeo_id = Column(
        Integer,
        ForeignKey(
            "item_vimeo.id",
            name="gallery_item_item_vimeo_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    order = Column(Integer, nullable=False)
    gallery = relationship("Gallery", back_populates="items")
    item_bucket = relationship("ItemBucket", backref=backref("gallery_items", cascade="all, delete-orphan"))
    item_vimeo = relationship("ItemVimeo", backref=backref("gallery_items", cascade="all, delete-orphan"))
