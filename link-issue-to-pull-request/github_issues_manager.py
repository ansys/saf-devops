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
from typing import Any

import requests


class IssueManager:
    def __init__(self, github_repository: str):
        self._github_repository = github_repository
        self._github_repository_name = self._github_repository.split("/")[-1]

    @property
    def _headers(self) -> dict[str, Any]:
        github_token = os.environ.get("ISSUE_GITHUB_TOKEN")
        if not github_token:
            github_token = os.environ.get("GITHUB_TOKEN")

        return {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

    def _get_url(self, issue_number: int) -> str:
        return f"https://api.github.com/repos/{self._github_repository}/issues/{issue_number}"

    def get_issue_description(self, issue_number: int) -> str:
        response = requests.get(self._get_url(issue_number), headers=self._headers)
        response.raise_for_status()

        return response.json().get("body", "")

    def update_issue_description(
        self,
        issue_number: int,
        issue_description: str,
    ) -> None:
        payload = {"body": issue_description}

        response = requests.patch(
            self._get_url(issue_number),
            headers=self._headers,
            json=payload,
        )
        response.raise_for_status()
