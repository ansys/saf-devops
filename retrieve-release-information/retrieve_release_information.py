# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from enum import Enum
from pathlib import Path

from github_utilities import GitHubLogger, set_as_github_outputs
from pyproject_toml_manager import PyprojectTomlManager

BRANCH_NAME_ENV_VAR = "GITHUB_REF_NAME"  # Defined in Github context
MANIFEST_DIRECTORY_ENV_VAR = "MANIFEST_DIRECTORY"
RELEASE_TYPE_ENV_VAR = "RELEASE_TYPE"


class ReleaseType(Enum):
    DEV = "dev"
    STABLE = "stable"


def _verify_branch_name(release_type: ReleaseType):
    branch_name = os.environ[BRANCH_NAME_ENV_VAR]

    if release_type == ReleaseType.DEV:
        if branch_name != "main":
            message = f"Development release must be triggered from main but got {branch_name}."
            GitHubLogger.error(title="INVALID BRANCH FOR DEV RELEASE", message=message)
            raise ValueError(message)
        return

    if release_type == ReleaseType.STABLE:
        pattern = r"^release/v\d+\.\d+(?:/[^/\s]+)?$"
        if not (branch_name == "main" or re.match(pattern, branch_name)):
            message = f"Stable release must be triggered from main, release/vX.Y, or release/vX.Y/<suffix> but got {branch_name}"
            GitHubLogger.error(
                title="INVALID BRANCH FOR STABLE RELEASE",
                message=message,
            )
            raise ValueError(message)


def _get_release_type() -> ReleaseType:
    raw_release_type = os.environ[RELEASE_TYPE_ENV_VAR].lower().strip()
    return ReleaseType(raw_release_type)


def _get_manifest_file() -> Path:
    manifest_directory = Path(os.environ[MANIFEST_DIRECTORY_ENV_VAR])
    return manifest_directory / "pyproject.toml"


def _get_bumped_version(version_to_bump: str, release_type: ReleaseType) -> str:
    match = re.match(r"(\d+)\.(\d+)\.(dev\d+)", version_to_bump)

    if match:
        major, minor, patch = match.groups()

        if release_type == ReleaseType.DEV:
            match = re.search(r"\d+", patch)
            if not match:
                message = f"Could not find build version from {patch}"
                GitHubLogger.error(title="NO MATCHING", message=message)
                raise ValueError(message)

            build = int(match.group())

            return f"{major}.{minor}.dev{build + 1}"
        else:
            next_minor = int(minor) + 1

            return f"{major}.{next_minor}.dev0"
    else:
        if release_type == ReleaseType.DEV:
            message = f"Could not find dev version from {version_to_bump}"
            GitHubLogger.error(title="NO MATCHING", message=message)
            raise ValueError(message)
        else:
            match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_to_bump)
            if not match:
                message = f"Could not find stable version from {version_to_bump}"
                GitHubLogger.error(title="NO MATCHING", message=message)
                raise ValueError(message)
            major, minor, patch = match.groups()

            return f"{major}.{minor}.{int(patch) + 1}"


def _get_version_to_release(
    version_in_manifest_file: str,
    release_type: ReleaseType,
) -> str:
    match = re.match(r"(\d+)\.(\d+)\.(dev\d+)", version_in_manifest_file)

    if match:
        major, minor, _ = match.groups()
        if release_type == ReleaseType.STABLE:
            return f"{major}.{minor}.0"
    else:
        if release_type == ReleaseType.DEV:
            message = f"Could not find the dev version from {version_in_manifest_file}"
            GitHubLogger.error(title="NO MATCHING", message=message)
            raise ValueError(message)

        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_in_manifest_file)

        if not match:
            message = (
                f"Could not find the stable version from {version_in_manifest_file}"
            )
            GitHubLogger.error(title="NO MATCHING", message=message)
            raise ValueError(message)

        _, _, patch = match.groups()

        if patch == "0":
            message = "A minor release should be released from a dev version."
            GitHubLogger.error(
                title="Minor release should be released from a dev version.",
                message=message,
            )

            raise ValueError(message)

    return version_in_manifest_file


def _get_version_from_manifest_file() -> str:
    manifest_file = _get_manifest_file()
    manager = PyprojectTomlManager(manifest_file)
    return manager.get_version()


def retrieve_release_information():
    release_type = _get_release_type()
    _verify_branch_name(release_type)

    version_from_manifest_file = _get_version_from_manifest_file()
    version_to_release = _get_version_to_release(
        version_from_manifest_file,
        release_type,
    )
    next_version = _get_bumped_version(version_from_manifest_file, release_type)

    set_as_github_outputs(
        release_name=f"v{version_to_release}",
        version_to_bump_in_triggering_branch=next_version,
        version_to_release=version_to_release,
    )

    if release_type == ReleaseType.STABLE:
        next_version_in_release_branch = _get_bumped_version(
            version_to_release,
            release_type,
        )

        match = re.match(r"(\d+)\.(\d+)", version_from_manifest_file)
        major, minor = match.groups()  # type: ignore

        set_as_github_outputs(
            version_to_bump_in_release_branch=next_version_in_release_branch,
            release_branch_name=f"release/v{major}.{minor}",
            version_major_minor=f"{major}.{minor}",
            version_type="dev" if "dev" in version_from_manifest_file else "stable",
        )


if __name__ == "__main__":
    retrieve_release_information()
