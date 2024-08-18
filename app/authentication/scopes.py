from dataclasses import dataclass


@dataclass
class Scope:
    name: str
    description: str


@dataclass
class ScopeGroup:
    name: str
    description: str | None
    scopes: list[Scope]


bucket_item_read = Scope(
    name="bucket_{source_id}_item_read",
    description="Bucket source item read",
)

bucket_item_create = Scope(
    name="bucket_{source_id}_item_create",
    description="Bucket source item create",
)

bucket_item_update = Scope(
    name="bucket_{source_id}_item_update",
    description="Bucket source item update",
)

bucket_item_delete = Scope(
    name="bucket_{source_id}_item_delete",
    description="Bucket source item delete",
)

vimeo_item_read = Scope(
    name="vimeo_{source_id}_item_read",
    description="Vimeo source item read",
)

vimeo_item_create = Scope(
    name="vimeo_{source_id}_item_create",
    description="Vimeo source item create",
)

vimeo_item_update = Scope(
    name="vimeo_{source_id}_item_update",
    description="Vimeo source item update",
)

vimeo_item_delete = Scope(
    name="vimeo_{source_id}_item_delete",
    description="Vimeo source item delete",
)

all_scopes = [
    bucket_item_read,
    bucket_item_create,
    bucket_item_update,
    bucket_item_delete,
    vimeo_item_read,
    vimeo_item_create,
    vimeo_item_update,
    vimeo_item_delete,
]

group_bucket_item_manage = ScopeGroup(
    name="group_bucket_item_manage",
    description="Manage all bucket items across all source ids.",
    scopes=[
        bucket_item_read,
        bucket_item_create,
        bucket_item_update,
        bucket_item_delete,
    ],
)

group_bucket_item_update = ScopeGroup(
    name="group_bucket_item_update",
    description="Create and update bucket items across all source ids. Cannot delete.",
    scopes=[
        bucket_item_read,
        bucket_item_create,
        bucket_item_update,
    ],
)

group_bucket_item_read = ScopeGroup(
    name="group_bucket_item_read",
    description="Read bucket items across all source ids.",
    scopes=[
        bucket_item_read,
    ],
)

group_vimeo_item_manage = ScopeGroup(
    name="group_vimeo_item_manage",
    description="Manage All vimeo items across all source ids",
    scopes=[vimeo_item_read, vimeo_item_create, vimeo_item_update, vimeo_item_delete],
)

group_vimeo_item_update = ScopeGroup(
    name="group_vimeo_item_update",
    description="Create and update vimeo items. across all source ids. Cannot delete.",
    scopes=[
        vimeo_item_read,
        vimeo_item_create,
        vimeo_item_update,
    ],
)

group_vimeo_item_read = ScopeGroup(
    name="group_vimeo_item_read",
    description="Read vimeo items across all source ids",
    scopes=[
        vimeo_item_read,
    ],
)

all_groups = [
    group_bucket_item_manage,
    group_bucket_item_update,
    group_bucket_item_read,
    group_vimeo_item_manage,
    group_vimeo_item_update,
    group_vimeo_item_read,
]
