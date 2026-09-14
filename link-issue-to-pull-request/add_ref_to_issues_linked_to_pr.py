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

from github_issues_manager import IssueManager
from github_pull_requests_manager import PullRequestManager
from github_utilities import GitHubLogger

KEYWORD = "related issue"
PR_SECTION_HEADER = "<details><summary><h2>Linked Pull Requests</h2></summary>"
PR_SECTION_FOOTER = "<!-- end-of-linked-pull-requests-section --></details>"


class GitHubContext:
    def __init__(self):
        self.pull_request_repository: str = os.environ["GITHUB_REPOSITORY"]
        self.pull_request_number: int = int(os.environ["PULL_REQUEST_NUMBER"])
        self.pull_request_title: str = os.environ["PULL_REQUEST_TITLE"]


def _is_pull_request_must_include_linked_issues(pull_request_title: str) -> bool:
    """
    Returns True if the PR title does not match any skipping patterns.
    """
    skipping_patterns = [
        r"^chore\(bump\):.*$",
        r"^ci\(dependabot\):.*$",
        r"^ci\(fix\):.*$",
        r"^ci\(chore\):.*$",
        r"^ci\(refactor\):.*$",
    ]

    if any(re.match(pattern, pull_request_title) for pattern in skipping_patterns):
        GitHubLogger.info(
            title="SKIPPING LINKED ISSUES PROCESSING",
            message=f"Pull request title '{pull_request_title}' matches skipping pattern.",
        )
        return False
    return True


def _get_linked_issues_from_pull_request_description(
    pull_request_description: str,
    pull_request_github_repository: str,
) -> list[dict[str, str | int]]:
    """
    Extract linked issues from pull request description following the keyword "Related Issue".

    Args:
        pull_request_description: The PR description text
        pull_request_github_repository: The repository of the PR (org/repo format)

    Returns:
        List of dictionaries with 'repository' and 'number' keys
    """
    linked_issues = []

    # Pattern 1: Just issue number (#123) - assumes same repo as PR
    pattern_simple = rf"{KEYWORD}\s+#(\d+)"
    matches = re.findall(pattern_simple, pull_request_description, flags=re.IGNORECASE)
    for match in matches:
        linked_issues.append(
            {"repository": pull_request_github_repository, "number": int(match)}
        )

    # Pattern 2: org/repo#issue_number format
    pattern_org_repo = rf"{KEYWORD}\s+([\w\-\.]+/[\w\-\.]+)#(\d+)"
    matches = re.findall(
        pattern_org_repo, pull_request_description, flags=re.IGNORECASE
    )
    for match in matches:
        linked_issues.append({"repository": match[0], "number": int(match[1])})

    # Pattern 3: Full GitHub URL
    pattern_url = rf"{KEYWORD}\s+https://github\.com/([\w\-\.]+/[\w\-\.]+)/issues/(\d+)"
    matches = re.findall(pattern_url, pull_request_description, flags=re.IGNORECASE)
    for match in matches:
        linked_issues.append({"repository": match[0], "number": int(match[1])})

    # Remove duplicates while preserving order
    unique_issues = []
    seen = set()
    for issue in linked_issues:
        key = (issue["repository"], issue["number"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return unique_issues


def add_ref_to_issues_linked_to_pr() -> None:
    """
    Updates linked issues with a reference to the pull request.

    Fetch pull request number, and repository names from environment variables.
    Find issues linked in the pull request description.
    For each linked issue:
       - Add a "Linked pull request(s)" section if not present.
       - Append a markdown link to the pull request.
       - Update the issue description if it was changed.
    Log important steps and errors for traceability.

    Raises:
        ValueError: If no linked issues are found in the PR description.
    """
    context = GitHubContext()
    if not _is_pull_request_must_include_linked_issues(context.pull_request_title):
        return

    pull_request_manager = PullRequestManager(context.pull_request_repository)
    pull_request_description = pull_request_manager.get_pull_request_description(
        context.pull_request_number
    )

    linked_issues = _get_linked_issues_from_pull_request_description(
        pull_request_description=pull_request_description,
        pull_request_github_repository=context.pull_request_repository,
    )

    if not linked_issues:
        # Check for dependabot security advisory pattern
        dependabot_pattern = rf"{KEYWORD}\s+https://github\.com/{context.pull_request_repository}/security/dependabot/\d+"
        if re.search(dependabot_pattern, pull_request_description, flags=re.IGNORECASE):
            GitHubLogger.info(
                title="DEPENDABOT SECURITY ADVISORY",
                message="Dependabot security advisory detected in PR description. Skipping linked issues requirement.",
            )
            return

        message = "A linked issue could not be found in the PR description."
        GitHubLogger.error(
            title="MISSING LINKED ISSUES",
            message=message,
        )
        raise ValueError(message)

    pr_text = f"""- https://github.com/{context.pull_request_repository}/pull/{context.pull_request_number}"""

    for linked_issue in linked_issues:
        issue_manager = IssueManager(linked_issue["repository"])
        issue_number = linked_issue["number"]
        original_description = issue_manager.get_issue_description(issue_number)

        if PR_SECTION_HEADER not in original_description:
            description = (
                f"{original_description}\n{PR_SECTION_HEADER}\n\n{PR_SECTION_FOOTER}"
            )
        else:
            description = original_description

        if pr_text not in description:
            description = description.replace(
                PR_SECTION_FOOTER, f"{pr_text}\n{PR_SECTION_FOOTER}"
            )

        if description != original_description:
            issue_manager.update_issue_description(
                issue_number=issue_number,
                issue_description=description,
            )


if __name__ == "__main__":
    add_ref_to_issues_linked_to_pr()
