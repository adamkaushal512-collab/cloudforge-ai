"""Opt-in guard for manual scripts that write to the configured database."""

import argparse
import os

from sqlalchemy.engine import make_url

CONFIRM_FLAG = "--confirm-dev-write"
DEFAULT_DATABASE_URL = "postgresql+psycopg:///cloudforge_db"


def require_write_confirmation(description: str) -> None:
    """Exit unless the caller explicitly confirms a committed write."""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        CONFIRM_FLAG,
        action="store_true",
        help="Required. Confirms committing rows to DATABASE_URL.",
    )
    args = parser.parse_args()

    target = make_url(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
    safe_target = target.render_as_string(hide_password=True)

    if not args.confirm_dev_write:
        parser.exit(
            2,
            f"Refusing to write: this script COMMITS rows to {safe_target}.\n"
            f"Re-run with {CONFIRM_FLAG} to proceed.\n",
        )

    print(f"Writing to {safe_target}")
