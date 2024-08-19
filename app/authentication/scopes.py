from .permissions import (
    PLACEHOLDER,
    Permission,
    PermissionGroup,
    all_permissions,
    permission_groups,
)


def find_permission(scope: str) -> Permission | None:
    result: Permission | None = next(
        (perm for perm in all_permissions if perm.name == scope), None
    )
    return result


def find_permission_group(scope: str) -> PermissionGroup | None:
    result: PermissionGroup | None = next(
        (group for group in permission_groups if group.name == scope), None
    )
    return result


def get_permissions_from_scopes(
    token_scopes: list[str], source_id: int | None
) -> list[str]:
    output = []
    for scope in token_scopes:
        found_group = find_permission_group(scope)
        if found_group:
            # extrapolates group permissions
            for perm in found_group.permissions:
                dynamic_scope = perm.name.replace(PLACEHOLDER, str(source_id))
                output.append(dynamic_scope)
        else:
            output.append(scope)
        output.append(scope)
    return output


def process_required_scopes(
    security_scopes: list[str], source_id: int | None
) -> list[str]:
    # replaces {source_id} placeholder when source_id is present
    if not source_id:
        return security_scopes
    output = []
    for scope in security_scopes:
        if PLACEHOLDER in scope:
            # Replace the placeholder with the actual source_id
            scope = scope.replace(PLACEHOLDER, str(source_id))
        output.append(scope)
    return output
