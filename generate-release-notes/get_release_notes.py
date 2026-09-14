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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from github_pull_requests_manager import PullRequestManager
from github_release_manager import ReleaseManager
from release import ReleaseInformation

MANUAL_SECTION_SEPARATOR = (
    "<!-- MANUAL EDITION SHOULD BE DONE HERE; "
    "DO NOT INCLUDE LINKS/INFORMATION THAT END USERS CANNOT ACCESS TO -->"
)
AUTOMATIC_SECTION_SEPARATOR = (
    "<!-- DO NOT EDIT BELOW THIS LINE; "
    "INTERNAL INFORMATION WILL BE REMOVED AUTOMATICALLY FOR THE END USERS -->"
)

SECTION_TITLE_PER_KEYWORD = {
    "breaking-change": "🚨 Breaking changes",
    "feat": "✨ Features",
    "perf": "⚡ Performance",
    "fix": "🛠️ Fixes",
    "docs": "📚 Documentation",
}


class GitHubContext:
    def __init__(self):
        self.repository: str = os.environ["GITHUB_REPOSITORY"]
        self.issues_repository: str = os.environ["ISSUES_REPOSITORY"]
        self.tag_name: str = os.environ["TAG_NAME"]


def _get_pull_requests_per_type(
    pull_requests: list[dict[str, Any]],
    type_keyword: str,
) -> list[dict[str, Any]]:
    if type_keyword == "breaking-change":
        return [
            pr
            for pr in pull_requests
            if pr.get("title", "").split(":")[0].endswith("!")
        ]

    return [
        pr
        for pr in pull_requests
        if not pr.get("title", "").split(":")[0].endswith("!")
        and pr.get("title", "").startswith(type_keyword)
    ]


def generate_release_notes() -> None:
    context = GitHubContext()
    release_manager = ReleaseManager(context.repository)

    releases = release_manager.get_releases()
    target_release = ReleaseInformation(
        release_name=context.tag_name,
        published_at=datetime.now(timezone.utc),
        description="",
    )

    previous_release_found = False
    try:
        previous_tag = (
            target_release.previous_tag_name
            if target_release.release_label == ""
            else f"{target_release.previous_version}-{target_release.release_label}"
        )
        previous_release = release_manager.get_release_information_by_tag_name(
            releases,
            previous_tag,
        )
        previous_release_date = previous_release.published_at
        previous_release_found = True
    except IndexError:
        previous_release_date = datetime(1983, 3, 21, tzinfo=timezone.utc)

    pr_manager = PullRequestManager(context.repository)
    pull_requests = pr_manager.get_closed_pull_requests_since(
        target_release.base_name,
        previous_release_date,
        labels=[target_release.release_label] if target_release.release_label else None,
    )

    pr_line = "- {title} by @{user} in [#{number}](https://github.com/{repository}/pull/{number})\n"

    release_notes = Path("release_notes.md")
    with release_notes.open("w") as fh:
        fh.write(MANUAL_SECTION_SEPARATOR + "\n")
        fh.write("\n## Maintenance\n")
        if "dev" in target_release.release_name:
            fh.write(
                "⚠️ This is a development release. It is not intended for production use and may contain unstable features.\n",
            )
        elif previous_release_found:
            starting_date = (
                datetime.now(timezone.utc)
                if target_release.release_name.split("-")[0].endswith(".0")
                else previous_release_date
            )
            maintenance_end_date = (starting_date + timedelta(days=180)).strftime(
                "%Y-%m-%d"
            )
            fh.write(
                f"🔧 This release is under maintenance until {maintenance_end_date}. Beyond that date, no further bug fixes or security patches will be released on that minor version.\n"
            )

        fh.write("\n# What's changed\n")
        fh.write(AUTOMATIC_SECTION_SEPARATOR)
        for keyword, title in SECTION_TITLE_PER_KEYWORD.items():
            selected_prs = _get_pull_requests_per_type(pull_requests, keyword)
            if selected_prs:
                fh.write(f"\n## {title}\n")
            for pr in selected_prs:
                fh.write(
                    str(
                        pr_line.format(
                            title=pr.get("title"),
                            user=pr.get("user", {}).get("login"),
                            number=pr.get("number"),
                            repository=context.repository,
                        ),
                    ),
                )


if __name__ == "__main__":
    generate_release_notes()
