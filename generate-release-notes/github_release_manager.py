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
from datetime import datetime, timezone
from typing import Any

from github_api_handler import APIHandler
from release import ReleaseInformation


class ReleaseManager:
    def __init__(self, github_repository: str):
        self._github_repository = github_repository

    @property
    def _headers(self) -> dict[str, Any]:
        github_token = os.environ.get("GITHUB_TOKEN")

        return {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

    def _get_url(self) -> str:
        return f"https://api.github.com/repos/{self._github_repository}/releases"

    def get_releases(self) -> list[ReleaseInformation]:
        releases = APIHandler.get_items_from_all_github_pages(
            self._get_url(),
            self._headers,
        )

        releases_information: list[ReleaseInformation] = []
        for release in releases:
            release_information = ReleaseInformation(
                release_name=release.get("tag_name"),
                published_at=(
                    datetime.strptime(
                        release.get("published_at"),
                        "%Y-%m-%dT%H:%M:%SZ",
                    ).replace(tzinfo=timezone.utc)
                    if release.get("published_at")
                    else datetime.now(timezone.utc)
                ),
                description=release.get("body", ""),
            )
            releases_information.append(release_information)

        return releases_information

    @staticmethod
    def get_release_information_by_tag_name(
        candidates: list[ReleaseInformation],
        tag_name: str,
    ) -> ReleaseInformation:
        """
        Retrieve a specific release information from a list of candidates based on the specified tag name.

        Args:
            candidates (List[ReleaseInformation]): A list of `ReleaseInformation` objects to search through.
            tag_name (str): The tag name used to identify the specific release information.

        Returns:
            ReleaseInformation: The `ReleaseInformation` object that matches the given tag name.

        Raises:
            IndexError: If no release with the specified tag name is found within the candidates list.
            IndexError: If more than one release with the specified tag name is found within the candidate list.

        Example:
            >>> release = get_release_information_by_tag_name(candidates, "v1.1.1")
            >>> print(release.published_at)
        """
        wild_card = ReleaseInformation(
            release_name=tag_name,
            description="",
            published_at=datetime.now(timezone.utc),
        )
        selected_candidates = [
            candidate
            for candidate in candidates
            if candidate.version == wild_card.version
            and candidate.release_label == wild_card.release_label
        ]

        if len(selected_candidates) == 0:
            raise IndexError("Not found.")
        elif len(selected_candidates) == 1:
            return selected_candidates[0]
        else:
            raise IndexError("Found multiple candidates.")
