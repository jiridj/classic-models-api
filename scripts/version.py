#!/usr/bin/env python3
"""
Version management script for Classic Models API.
This script extracts version information and updates the API documentation.
"""

import re
import subprocess
import sys
from pathlib import Path


def get_git_version():
    """Get version from git tag or commit hash."""
    try:
        # Try to get the latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        tag = result.stdout.strip()
        # Remove 'v' prefix if present
        return tag.lstrip("v")
    except subprocess.CalledProcessError:
        # Fall back to commit hash
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return f"dev-{result.stdout.strip()}"


def update_settings_version(version):
    """Update the version in Django settings."""
    settings_file = Path("config/settings/base.py")

    if not settings_file.exists():
        print(f"Settings file not found: {settings_file}")
        return False

    content = settings_file.read_text()

    # Update SPECTACULAR_SETTINGS version
    pattern = r'("VERSION":\s*")[^"]*(")'
    replacement = rf"\g<1>{version}\g<2>"
    updated_content = re.sub(pattern, replacement, content)

    if updated_content != content:
        settings_file.write_text(updated_content)
        print(f"Updated API version to: {version}")
        return True
    else:
        print(f"Version already set to: {version}")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        version = get_git_version()

    print(f"Setting API version to: {version}")

    # Update settings
    updated = update_settings_version(version)

    if updated:
        print("Settings updated successfully")
    else:
        print("No changes needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
