from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """
    Represents a verified identity and its authorized
    tenant context.
    """

    # Unique identity of the authenticated user.
    user_id: str

    # Tenant the user is authorized to access.
    tenant_id: str

    # Application roles assigned to the user.
    roles: tuple[str, ...]


def require_role(
    principal: AuthenticatedPrincipal,
    allowed_roles: tuple[str, ...],
) -> None:
    """Require at least one permitted application role."""

    if not any(role in principal.roles for role in allowed_roles):
        raise PermissionError(
            "User does not have the required role"
        )
