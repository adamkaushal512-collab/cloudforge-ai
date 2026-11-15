"""
Unit tests for the RBAC helper and development auth dependency.

The auth dependency is a development simulation, not JWT/OIDC.
"""

import dataclasses

import pytest

from cloudforge.api.auth import get_current_principal
from cloudforge.core.security import AuthenticatedPrincipal, require_role

pytestmark = pytest.mark.unit


def _principal(*roles: str) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(user_id="u", tenant_id="t", roles=roles)


@pytest.mark.parametrize(
    ("roles", "allowed"),
    [
        (("model-admin",), ("platform-admin", "model-admin")),
        (("platform-admin",), ("platform-admin", "model-admin")),
        (("viewer", "model-admin"), ("model-admin",)),
    ],
)
def test_require_role_allows_matching_role(roles, allowed):
    require_role(_principal(*roles), allowed)


@pytest.mark.parametrize(
    ("roles", "allowed"),
    [
        ((), ("model-admin",)),
        (("viewer",), ("model-admin",)),
        (("model-admin",), ()),
        (("MODEL-ADMIN",), ("model-admin",)),
    ],
)
def test_require_role_denies_without_matching_role(roles, allowed):
    with pytest.raises(PermissionError):
        require_role(_principal(*roles), allowed)


def test_principal_is_immutable():
    principal = _principal("model-admin")

    with pytest.raises(dataclasses.FrozenInstanceError):
        principal.tenant_id = "other"  # type: ignore[misc]


def test_development_principal_is_simulated():
    principal = get_current_principal()

    # Documents the current dev-only identity; replace when JWT/OIDC lands.
    assert principal == AuthenticatedPrincipal(
        user_id="alice",
        tenant_id="tenant-retail",
        roles=("model-admin",),
    )
