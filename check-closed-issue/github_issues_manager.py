# Copyright (C) 2026 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import Any

import requests


class IssueManager:
    def __init__(self, github_repository: str):
        self._github_repository = github_repository
        self._github_repository_name = self._github_repository.split("/")[-1]

    @property
    def _headers(self) -> dict[str, Any]:
        github_token = os.environ.get("GITHUB_TOKEN")
        return {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

    def _get_url(self, issue_number: int | None = None) -> str:
        return (
            f"https://api.github.com/repos/{self._github_repository}/issues/{issue_number}"
            if issue_number
            else f"https://api.github.com/repos/{self._github_repository}/issues"
        )

    def get_issue_description(self, issue_number: int) -> str:
        response = requests.get(self._get_url(issue_number), headers=self._headers)
        response.raise_for_status()

        return response.json().get("body", "")

    def get_issue_type(self, issue_number: int) -> str | None:
        response = requests.get(self._get_url(issue_number), headers=self._headers)
        response.raise_for_status()

        issue_type = response.json().get("type", {})

        return issue_type.get("name") if issue_type else None

    def get_assignees(self, issue_number: int) -> list[str]:
        response = requests.get(self._get_url(issue_number), headers=self._headers)
        response.raise_for_status()

        return [
            assignee.get("login", "")
            for assignee in response.json().get("assignees", [])
        ]

    def comment_on_issue(
        self,
        issue_number: int,
        comment: str,
    ) -> None:
        payload = {"body": comment}

        response = requests.post(
            f"{self._get_url(issue_number)}/comments",
            headers=self._headers,
            json=payload,
        )
        response.raise_for_status()

    def reopen_issue(self, issue_number: int) -> None:
        payload = {"state": "open"}

        response = requests.patch(
            self._get_url(issue_number),
            headers=self._headers,
            json=payload,
        )
        response.raise_for_status()

    def get_subissues(self, issue_number: int) -> list[dict[str, Any]]:
        url = f"{self._get_url(issue_number)}/sub_issues"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()
        return response.json()
