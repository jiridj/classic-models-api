#!/usr/bin/env python3
"""
Version management script for Classic Models API.
Similar to 'npm version' - handles git tagging, config updates, and Docker builds.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


class VersionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.settings_file = self.project_root / "config" / "settings" / "base.py"

    def get_current_version(self):
        """Get current version from git tag or settings."""
        try:
            # Get all tags and find the latest semver version
            result = subprocess.run(
                ["git", "tag", "-l", "v*"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            tags = result.stdout.strip().split("\n")
            if tags and tags[0]:  # Check if we have any tags
                # Sort tags by semver and get the latest
                latest_tag = sorted(
                    tags, key=lambda x: [int(v) for v in x.lstrip("v").split(".")]
                )[-1]
                return latest_tag.lstrip("v")
            else:
                # No tags found, fall back to settings
                return self._get_version_from_settings()
        except subprocess.CalledProcessError:
            # Fall back to reading from settings
            return self._get_version_from_settings()

    def _get_version_from_settings(self):
        """Extract version from Django settings file."""
        if not self.settings_file.exists():
            return "0.0.0"

        content = self.settings_file.read_text()
        match = re.search(r'"VERSION":\s*"([^"]*)"', content)
        return match.group(1) if match else "0.0.0"

    def _update_settings_version(self, version):
        """Update version in Django settings."""
        if not self.settings_file.exists():
            print(f"Settings file not found: {self.settings_file}")
            return False

        content = self.settings_file.read_text()

        # Update get_version() function default value
        pattern = r'(return os\.environ\.get\("API_VERSION",\s*")[^"]*("\))'
        replacement = rf"\g<1>{version}\g<2>"
        updated_content = re.sub(pattern, replacement, content)

        if updated_content != content:
            self.settings_file.write_text(updated_content)
            print(f"Updated API version to: {version}")
            return True
        else:
            print(f"Version already set to: {version}")
            return False

    def _parse_version(self, version_str):
        """Parse version string and return (major, minor, patch)."""
        # Remove 'v' prefix if present
        version_str = version_str.lstrip("v")

        # Split by dots
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid version format: {version_str}. Expected format: X.Y.Z"
            )

        try:
            return tuple(int(part) for part in parts)
        except ValueError:
            raise ValueError(
                f"Invalid version format: {version_str}. All parts must be integers."
            )

    def _increment_version(self, current_version, increment_type):
        """Increment version based on type (major, minor, patch)."""
        major, minor, patch = self._parse_version(current_version)

        if increment_type == "major":
            return f"{major + 1}.0.0"
        elif increment_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif increment_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid increment type: {increment_type}")

    def _validate_git_status(self):
        """Validate git repository status."""
        # Check if we're in a git repository
        try:
            subprocess.run(
                ["git", "status"],
                capture_output=True,
                check=True,
                cwd=self.project_root,
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("Not in a git repository")

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            cwd=self.project_root,
        )

        if result.stdout.strip():
            print("Warning: You have uncommitted changes:")
            print(result.stdout)
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
                raise RuntimeError("Aborted due to uncommitted changes")

    def _check_main_branch_up_to_date(self):
        """Check if main branch is up to date with origin/main before tagging."""
        print("Checking if main branch is up to date...")

        # Fetch latest from remote
        try:
            subprocess.run(
                ["git", "fetch", "origin"],
                capture_output=True,
                check=True,
                cwd=self.project_root,
            )
        except subprocess.CalledProcessError:
            print("Warning: Could not fetch from origin. Continuing anyway...")
            return

        # Check if main branch exists locally
        try:
            subprocess.run(
                ["git", "rev-parse", "--verify", "main"],
                capture_output=True,
                check=True,
                cwd=self.project_root,
            )
        except subprocess.CalledProcessError:
            # Try 'master' as fallback
            try:
                subprocess.run(
                    ["git", "rev-parse", "--verify", "master"],
                    capture_output=True,
                    check=True,
                    cwd=self.project_root,
                )
                main_branch = "master"
            except subprocess.CalledProcessError:
                print(
                    "Warning: Could not find main or master branch. Skipping check..."
                )
                return
        else:
            main_branch = "main"

        # Check if origin/main exists
        try:
            subprocess.run(
                ["git", "rev-parse", "--verify", f"origin/{main_branch}"],
                capture_output=True,
                check=True,
                cwd=self.project_root,
            )
        except subprocess.CalledProcessError:
            print(f"Warning: origin/{main_branch} does not exist. Skipping check...")
            return

        # Compare local main with origin/main
        try:
            # Get commit hashes
            local_result = subprocess.run(
                ["git", "rev-parse", main_branch],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            local_commit = local_result.stdout.strip()

            subprocess.run(
                ["git", "rev-parse", f"origin/{main_branch}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )

            # Check if local is behind remote
            behind_result = subprocess.run(
                ["git", "rev-list", "--count", f"{local_commit}..origin/{main_branch}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            behind_count = int(behind_result.stdout.strip())

            if behind_count > 0:
                raise RuntimeError(
                    f"main branch is {behind_count} commit(s) behind origin/main. "
                    f"Please pull the latest changes before creating a tag.\n"
                    f"Run: git checkout {main_branch} && git pull origin {main_branch}"
                )

            # Check if local is ahead of remote (optional, but good to know)
            ahead_result = subprocess.run(
                ["git", "rev-list", "--count", f"origin/{main_branch}..{local_commit}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            ahead_count = int(ahead_result.stdout.strip())

            if ahead_count > 0:
                print(
                    f"Note: main branch is {ahead_count} commit(s) ahead of origin/main"
                )

            print(f"✓ main branch is up to date with origin/{main_branch}")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not compare branches: {e}. Continuing anyway...")

    def _commit_version_change(self, version):
        """Commit version changes."""
        # Add the settings file
        subprocess.run(
            ["git", "add", str(self.settings_file)], check=True, cwd=self.project_root
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", f"Bump version to {version}"],
            check=True,
            cwd=self.project_root,
        )
        print(f"Committed version change: {version}")

    def _create_git_tag(self, version):
        """Create git tag."""
        tag_name = f"v{version}"

        # Check if tag already exists
        try:
            subprocess.run(
                ["git", "rev-parse", tag_name],
                capture_output=True,
                check=True,
                cwd=self.project_root,
            )
            print(f"Tag {tag_name} already exists")
            return tag_name
        except subprocess.CalledProcessError:
            pass

        # Create tag
        subprocess.run(["git", "tag", tag_name], check=True, cwd=self.project_root)
        print(f"Created tag: {tag_name}")
        return tag_name

    def _build_docker_image(self, version, push=False):
        """Build Docker image."""
        tag_name = f"v{version}"
        image_name = f"ghcr.io/{self._get_repo_name()}:{tag_name}"
        latest_name = f"ghcr.io/{self._get_repo_name()}:latest"

        print(f"Building Docker image: {image_name}")

        # Build the image
        subprocess.run(
            ["docker", "build", "-t", image_name, "-t", latest_name, "."],
            check=True,
            cwd=self.project_root,
        )

        print(f"Built Docker image: {image_name}")
        print(f"Built Docker image: {latest_name}")

        if push:
            print(f"Pushing Docker image: {image_name}")
            subprocess.run(["docker", "push", image_name], check=True)
            subprocess.run(["docker", "push", latest_name], check=True)
            print("Docker images pushed successfully")

    def _get_repo_name(self):
        """Get repository name from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            url = result.stdout.strip()
            # Extract repo name from URL (handle both https and ssh formats)
            if url.endswith(".git"):
                url = url[:-4]
            return url.split("/")[-1]
        except subprocess.CalledProcessError:
            return "classic-models-api"

    def version(self, version_arg, options):
        """Main version command."""
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")

        # Determine new version
        if version_arg in ["major", "minor", "patch"]:
            new_version = self._increment_version(current_version, version_arg)
        else:
            # Validate the provided version
            self._parse_version(version_arg)
            new_version = version_arg.lstrip("v")

        print(f"New version: {new_version}")

        # Validate git status
        if not options.skip_git:
            self._validate_git_status()

        # Update settings
        updated = self._update_settings_version(new_version)

        # For version increments, always commit (even if settings didn't change)
        # This ensures we have a commit to tag
        if not options.skip_git:
            if updated or version_arg in ["major", "minor", "patch"]:
                self._commit_version_change(new_version)
            else:
                print("No changes to commit")

        # Check if main is up to date before tagging
        if not options.skip_git and not options.force:
            self._check_main_branch_up_to_date()

        # Create tag (always create, even if no settings changes)
        if not options.skip_git:
            self._create_git_tag(new_version)

        # Build Docker image
        if options.build:
            self._build_docker_image(new_version, push=options.push)

        # Push to remote
        if options.push and not options.skip_git:
            print("Pushing changes to remote...")
            subprocess.run(["git", "push"], check=True, cwd=self.project_root)
            subprocess.run(["git", "push", "--tags"], check=True, cwd=self.project_root)
            print("Changes pushed to remote")

        print(f"\n✅ Version {new_version} ready!")
        if not options.skip_git:
            print(f"Tag: v{new_version}")
        if options.build:
            print(f"Docker image: ghcr.io/{self._get_repo_name()}:v{new_version}")


def main():
    parser = argparse.ArgumentParser(
        description="Version management for Classic Models API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s patch                    # Bump patch version (0.0.1 -> 0.0.2)
  %(prog)s minor                    # Bump minor version (0.0.1 -> 0.1.0)
  %(prog)s major                    # Bump major version (0.0.1 -> 1.0.0)
  %(prog)s 1.2.3                    # Set specific version
  %(prog)s patch --build            # Bump patch and build Docker image
  %(prog)s minor --build --push     # Bump minor, build, and push Docker image
  %(prog)s patch --skip-git         # Bump patch without git operations
        """,
    )

    parser.add_argument(
        "version", help="Version to set or increment type (major, minor, patch)"
    )

    parser.add_argument(
        "--build", action="store_true", help="Build Docker image after version bump"
    )

    parser.add_argument(
        "--push",
        action="store_true",
        help="Push Docker image and git changes to remote",
    )

    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip git operations (commit, tag, push)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force version update even if no changes, and bypass main branch up-to-date check",
    )

    args = parser.parse_args()

    try:
        manager = VersionManager()
        manager.version(args.version, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
