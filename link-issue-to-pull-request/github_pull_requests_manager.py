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

    def get_pull_request(self, pull_request_number: int) -> dict[str, Any]:
        response = requests.get(
            f"{self._get_url()}/{pull_request_number}",
            headers=self._headers,
        )
        response.raise_for_status()
        return response.json()

    def get_pull_request_description(self, pull_request_number: int) -> str:
        pr = self.get_pull_request(pull_request_number)
        return pr.get("body", "")
