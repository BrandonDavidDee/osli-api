from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class AuthUser(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    notes = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    scopes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    created_buckets = relationship("SourceBucket", back_populates="creator")
    created_videos = relationship("SourceVimeo", back_populates="creator")


class SourceBucket(Base):
    __tablename__ = "source_bucket"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    bucket_name = Column(String, nullable=False)
    access_key_id = Column(String, nullable=False)
    secret_access_key = Column(String, nullable=False)
    media_prefix = Column(String)
    grid_view = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False)

    # Relationships
    creator = relationship("AuthUser", back_populates="created_buckets")
    items = relationship("ItemBucket", back_populates="source_bucket")


class SourceVimeo(Base):
    __tablename__ = "source_vimeo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    client_identifier = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    grid_view = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False)

    # Relationships
    creator = relationship("AuthUser", back_populates="created_videos")
    items = relationship("ItemVimeo", back_populates="source_vimeo")


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
    title = Column(String(100))
    mime_type = Column(String(100))
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    notes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("auth_user.id"))

    # Relationships
    source_bucket = relationship("SourceBucket", back_populates="items")
    tags = relationship("TagItemBucket", back_populates="item_bucket")


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
    video_id = Column(String(255), nullable=False)
    title = Column(String(255))
    thumbnail = Column(String)
    notes = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("auth_user.id"))

    # Relationships
    source_vimeo = relationship("SourceVimeo", back_populates="items")
    tags = relationship("TagItemVimeo", back_populates="item_vimeo")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True, index=True, nullable=False)


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

    # Relationships
    tag = relationship(
        "Tag", backref=backref("tagged_items_bucket", cascade="all, delete-orphan")
    )
    item_bucket = relationship("ItemBucket", back_populates="tags")


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

    # Relationships
    tag = relationship(
        "Tag", backref=backref("tagged_items_vimeo", cascade="all, delete-orphan")
    )
    item_vimeo = relationship("ItemVimeo", back_populates="tags")


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("auth_user.id"))

    # Relationships
    items = relationship(
        "GalleryItem", back_populates="gallery", cascade="all, delete-orphan"
    )


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
    item_order = Column(Integer, nullable=False)

    # Relationships
    gallery = relationship("Gallery", back_populates="items")
    item_bucket = relationship(
        "ItemBucket", backref=backref("gallery_items", cascade="all, delete-orphan")
    )
    item_vimeo = relationship(
        "ItemVimeo", backref=backref("gallery_items", cascade="all, delete-orphan")
    )


class GalleryLink(Base):
    __tablename__ = "gallery_link"

    id = Column(Integer, primary_key=True, index=True)
    gallery_id = Column(
        Integer,
        ForeignKey(
            "gallery.id",
            name="gallery_link_gallery_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    title = Column(String, nullable=True)  # optional
    link = Column(String, nullable=False, unique=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("auth_user.id"))

    # Relationships
    gallery = relationship("Gallery", back_populates="links")
