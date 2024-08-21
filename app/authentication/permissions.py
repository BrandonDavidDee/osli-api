from dataclasses import dataclass

PLACEHOLDER = "{source_id}"


@dataclass
class Permission:
    name: str
    description: str
    source_id: int | None = None


@dataclass
class PermissionGroup:
    name: str
    label: str
    description: str | None
    permissions: list[Permission]


bucket_item_read = Permission(
    name="bucket_{source_id}_item_read",
    description="Bucket Source Item View",
)

bucket_item_create = Permission(
    name="bucket_{source_id}_item_create",
    description="Bucket Source Item Create",
)

bucket_item_update = Permission(
    name="bucket_{source_id}_item_update",
    description="Bucket Source Item Update",
)

bucket_item_delete = Permission(
    name="bucket_{source_id}_item_delete",
    description="Bucket Source Item Delete",
)

vimeo_item_read = Permission(
    name="vimeo_{source_id}_item_read",
    description="Vimeo Source Item View",
)

vimeo_item_create = Permission(
    name="vimeo_{source_id}_item_create",
    description="Vimeo Source Item Create",
)

vimeo_item_update = Permission(
    name="vimeo_{source_id}_item_update",
    description="Vimeo Source Item Update",
)

vimeo_item_delete = Permission(
    name="vimeo_{source_id}_item_delete",
    description="Vimeo Source Item Delete",
)


dynamic_bucket_permissions = [
    bucket_item_read,
    bucket_item_create,
    bucket_item_update,
    bucket_item_delete,
]

dynamic_vimeo_permissions = [
    vimeo_item_read,
    vimeo_item_create,
    vimeo_item_update,
    vimeo_item_delete,
]

item_link_create = Permission(
    name="item_link_create",
    description="Create Item Link",
)

gallery_create = Permission(
    name="gallery_create",
    description="Create Gallery",
)

gallery_link_create = Permission(
    name="gallery_link_create",
    description="Create Gallery Link",
)

miscellaneous_permissions = [item_link_create, gallery_create, gallery_link_create]

all_permissions = []

all_permissions.extend(miscellaneous_permissions)
all_permissions.extend(dynamic_bucket_permissions)
all_permissions.extend(dynamic_vimeo_permissions)

group_bucket_item_manage = PermissionGroup(
    name="group_bucket_item_manage",
    label="Bucket Item Manage",
    description="Manage all bucket items across all source ids.",
    permissions=[
        bucket_item_read,
        bucket_item_create,
        bucket_item_update,
        bucket_item_delete,
    ],
)

group_bucket_item_update = PermissionGroup(
    name="group_bucket_item_update",
    label="Bucket Item Update",
    description="Create and update bucket items across all source ids. Cannot delete.",
    permissions=[
        bucket_item_read,
        bucket_item_create,
        bucket_item_update,
    ],
)

group_bucket_item_read = PermissionGroup(
    name="group_bucket_item_read",
    label="Bucket Item Read Only",
    description="View bucket items across all source ids.",
    permissions=[
        bucket_item_read,
    ],
)

group_vimeo_item_manage = PermissionGroup(
    name="group_vimeo_item_manage",
    label="Vimeo Item Manage",
    description="Manage All vimeo items across all source ids",
    permissions=[
        vimeo_item_read,
        vimeo_item_create,
        vimeo_item_update,
        vimeo_item_delete,
    ],
)

group_vimeo_item_update = PermissionGroup(
    name="group_vimeo_item_update",
    label="Vimeo Item Update",
    description="Create and update vimeo items. across all source ids. Cannot delete.",
    permissions=[
        vimeo_item_read,
        vimeo_item_create,
        vimeo_item_update,
    ],
)

group_vimeo_item_read = PermissionGroup(
    name="group_vimeo_item_read",
    label="Vimeo Item Read Only",
    description="View vimeo items across all source ids",
    permissions=[
        vimeo_item_read,
    ],
)

permission_groups = [
    group_bucket_item_manage,
    group_bucket_item_update,
    group_bucket_item_read,
    group_vimeo_item_manage,
    group_vimeo_item_update,
    group_vimeo_item_read,
]
