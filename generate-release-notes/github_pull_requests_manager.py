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


class PullRequestManager:
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
        return f"https://api.github.com/repos/{self._github_repository}/pulls"

    def get_closed_pull_requests_since(
        self,
        base_name: str,
        from_date: datetime | None = None,
        labels: list[str] | None = None,
    ) -> list[dict[str, Any]]:

        params = {
            "state": "closed",
            "base": base_name,
            "sort": "created",
            "direction": "desc",
        }

        pull_requests = APIHandler.get_items_from_all_github_pages(
            url=self._get_url(),
            headers=self._headers,
            params=params,
        )

        if from_date is None:
            return pull_requests

        selected_pull_requests = [
            pr
            for pr in pull_requests
            if pr.get("merged_at") is not None
            and datetime.strptime(pr.get("merged_at"), "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc,
            )
            > from_date
        ]

        if labels:
            selected_pull_requests = [
                pr
                for pr in selected_pull_requests
                if any(label.get("name") in labels for label in pr.get("labels", []))
            ]

        return selected_pull_requests
