from fastapi import HTTPException, status

from cloudforge.core.security import AuthenticatedPrincipal


def get_current_principal() -> AuthenticatedPrincipal:
    """
    Development-only authentication simulation.

    TODO: Replace with validated JWT/OIDC authentication
    and trusted tenant membership checks.
    """

    # Simulated identity for local development only.
    principal = AuthenticatedPrincipal(
        user_id="alice",
        tenant_id="tenant-retail",
        roles=("model-admin",),
    )

    if not principal.user_id or not principal.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return principal
