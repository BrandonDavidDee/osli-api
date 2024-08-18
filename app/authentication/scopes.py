from dataclasses import dataclass

PLACEHOLDER = "{source_id}"


@dataclass
class Permission:
    name: str
    description: str


@dataclass
class PermissionGroup:
    name: str
    description: str | None
    permissions: list[Permission]


bucket_item_read = Permission(
    name="bucket_{source_id}_item_read",
    description="Bucket source item read",
)

bucket_item_create = Permission(
    name="bucket_{source_id}_item_create",
    description="Bucket source item create",
)

bucket_item_update = Permission(
    name="bucket_{source_id}_item_update",
    description="Bucket source item update",
)

bucket_item_delete = Permission(
    name="bucket_{source_id}_item_delete",
    description="Bucket source item delete",
)

vimeo_item_read = Permission(
    name="vimeo_{source_id}_item_read",
    description="Vimeo source item read",
)

vimeo_item_create = Permission(
    name="vimeo_{source_id}_item_create",
    description="Vimeo source item create",
)

vimeo_item_update = Permission(
    name="vimeo_{source_id}_item_update",
    description="Vimeo source item update",
)

vimeo_item_delete = Permission(
    name="vimeo_{source_id}_item_delete",
    description="Vimeo source item delete",
)

dynamic_permissions = [
    bucket_item_read,
    bucket_item_create,
    bucket_item_update,
    bucket_item_delete,
    vimeo_item_read,
    vimeo_item_create,
    vimeo_item_update,
    vimeo_item_delete,
]

group_bucket_item_manage = PermissionGroup(
    name="group_bucket_item_manage",
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
    description="Create and update bucket items across all source ids. Cannot delete.",
    permissions=[
        bucket_item_read,
        bucket_item_create,
        bucket_item_update,
    ],
)

group_bucket_item_read = PermissionGroup(
    name="group_bucket_item_read",
    description="Read bucket items across all source ids.",
    permissions=[
        bucket_item_read,
    ],
)

group_vimeo_item_manage = PermissionGroup(
    name="group_vimeo_item_manage",
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
    description="Create and update vimeo items. across all source ids. Cannot delete.",
    permissions=[
        vimeo_item_read,
        vimeo_item_create,
        vimeo_item_update,
    ],
)

group_vimeo_item_read = PermissionGroup(
    name="group_vimeo_item_read",
    description="Read vimeo items across all source ids",
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


def get_dynamic_group_permissions(scope: str, source_id: int) -> list[str]:
    output = []
    result: PermissionGroup | None = next(
        (group for group in permission_groups if group.name == scope), None
    )
    if result:
        for group in result.permissions:
            if PLACEHOLDER in group.name:
                scope = group.name.replace(PLACEHOLDER, str(source_id))
                output.append(scope)
    return output


def process_user_permissions(
    token_scopes: list[str], source_id: int | None
) -> list[str]:
    output = []
    for scope in token_scopes:
        if "group_" in scope and source_id is not None:
            group_permissions = get_dynamic_group_permissions(scope, source_id)
            output.extend(group_permissions)
        else:
            output.append(scope)
    return output


def process_required_scopes(
    required_scopes: list[str], source_id: int | None
) -> list[str]:
    if not source_id:
        return required_scopes
    output = []
    for scope in required_scopes:
        if PLACEHOLDER in scope:
            # Replace the placeholder with the actual source_id
            scope = scope.replace(PLACEHOLDER, str(source_id))
        output.append(scope)
    return output
