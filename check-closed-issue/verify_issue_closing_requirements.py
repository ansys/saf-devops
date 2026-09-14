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
import re

from github_issues_manager import (
    IssueManager,
)
from github_label_issues_manager import (
    IssueLabelsManager,
)
from markdown_manager import MarkdownManager

ISSUE_TYPES = ["task", "bug", "story", "test case", "test log"]


class GitHubContext:
    def __init__(self):
        self.repository: str = os.environ["GITHUB_REPOSITORY"]
        self.issue_number: int = int(os.environ["ISSUE_NUMBER"])
        self.issue_manager: IssueManager = IssueManager(self.repository)
        self.labels_manager: IssueLabelsManager = IssueLabelsManager(self.repository)


def _raise_for_missed_requirements(msg) -> None:
    context = GitHubContext()

    print(f"::error title=ISSUE CANNOT BE CLOSED:: {msg}")

    assignees = context.issue_manager.get_assignees(context.issue_number)

    comment = ""
    for assignee in assignees:
        comment += f"@{assignee} "
    if len(assignees) > 0:
        comment += ":\n"
    comment += msg
    context.issue_manager.comment_on_issue(context.issue_number, comment)
    context.issue_manager.reopen_issue(context.issue_number)

    raise ValueError("Issue closing requirements not met.")


def _verify_and_get_issue_type() -> str:
    context = GitHubContext()
    issue_type = (
        context.issue_manager.get_issue_type(context.issue_number) or ""
    ).lower()

    if not issue_type:
        _raise_for_missed_requirements(f"Issue {context.issue_number} has no type set.")

    return issue_type


def _check_label_for_story(issue_labels: list[str]):
    context = GitHubContext()

    valid_labels = [
        "technical",
        "functional",
        "maintenance",
        "documentation",
        "research",
    ]

    matching_labels = set(valid_labels).intersection(set(issue_labels))

    if not matching_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'story' must have at least one of the following labels: {', '.join(sorted(valid_labels))}."
        )

    if "technical" in matching_labels and "functional" in matching_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'story' cannot have both 'technical' and 'functional' labels."
        )

    if (
        "technical" in matching_labels or "functional" in matching_labels
    ) and "maintenance" in matching_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'story' cannot have 'maintenance' label along with 'technical' or 'functional' labels.",
        )

    invalid_labels = [
        "class 1",
        "class 2",
        "class 3",
        "test case",
        "test log",
        "bug",
    ]
    if set(invalid_labels).intersection(set(issue_labels)):
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'story' cannot have the following labels: {', '.join(sorted(invalid_labels))}.",
        )


def _check_label_for_bug(issue_labels: list[str]):
    context = GitHubContext()

    required_labels = ["class 1", "class 2", "class 3"]
    invalid_labels = [
        "triage",
        "research",
        "functional",
        "technical",
        "maintenance",
        "test case",
        "test log",
    ]

    matching_labels = set(required_labels).intersection(set(issue_labels))
    if not matching_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'bug' must have at one of the following labels: {', '.join(sorted(required_labels))}.",
        )

    if len(matching_labels) > 1:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'bug' can only have a single label among the following label(s): {', '.join(sorted(required_labels))}.",
        )

    matching_invalid_labels = set(invalid_labels).intersection(set(issue_labels))
    if matching_invalid_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'bug' cannot have the following label(s): {', '.join(sorted(matching_invalid_labels))}.",
        )


def _check_label_for_tests(issue_labels: list[str]):
    context = GitHubContext()

    invalid_labels = [
        "triage",
        "research",
        "functional",
        "technical",
        "class 1",
        "class 2",
        "class 3",
        "maintenance",
        "bug",
    ]

    matching_invalid_labels = set(invalid_labels).intersection(set(issue_labels))
    if matching_invalid_labels:
        _raise_for_missed_requirements(
            f"Issue {context.issue_number} of type 'test case' or 'test log' cannot have the following label(s):  {', '.join(sorted(matching_invalid_labels))}.",
        )


def _verify_and_get_issue_labels(issue_type: str) -> list[str]:
    context = GitHubContext()

    issue_labels = context.labels_manager.get_labels_names(context.issue_number)

    if issue_type == "story" or "story" in issue_labels:
        _check_label_for_story(issue_labels)
    if issue_type == "bug" or "bug" in issue_labels:
        _check_label_for_bug(issue_labels)
    if (
        issue_type in ["test case", "test log"]
        or "test case" in issue_labels
        or "test log" in issue_labels
    ):
        _check_label_for_tests(issue_labels)

    return issue_labels


def _has_linked_test_case_as_subissue() -> bool:

    context = GitHubContext()
    subissue_numbers = [
        subissue["number"]
        for subissue in context.issue_manager.get_subissues(context.issue_number)
    ]

    for subissue_number in subissue_numbers:
        subissue_type = (
            context.issue_manager.get_issue_type(subissue_number) or ""
        ).lower()
        if subissue_type == "test case":
            return True

        subissue_labels = context.labels_manager.get_labels_names(subissue_number)
        if "test case" in subissue_labels:
            return True

    return False


def _has_linked_test_case_in_issue_description() -> bool:
    context = GitHubContext()

    raw_description = context.issue_manager.get_issue_description(
        context.issue_number,
    ).splitlines()

    try:
        starting_index = next(
            (
                index
                for index, line in enumerate(raw_description)
                if "### Additional Links" in line
            ),
            None,
        )
        if starting_index is None:
            return False

        next_section_index = MarkdownManager.find_next_section_index(
            raw_description,
            starting_index,
        )
        additional_links_section = raw_description[starting_index:next_section_index]

        link_pattern = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/(\d+)")

        for line in additional_links_section:
            match = link_pattern.search(line)
            if match:
                linked_issue_number = int(match.group(1))
                linked_issue_type = (
                    context.issue_manager.get_issue_type(linked_issue_number) or ""
                ).lower()
                if linked_issue_type == "test case":
                    return True
                linked_issue_labels = context.labels_manager.get_labels_names(
                    linked_issue_number
                )
                if "test case" in linked_issue_labels:
                    return True
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return False


def check_closed_issue():
    context = GitHubContext()

    issue_type = _verify_and_get_issue_type()
    issue_labels = _verify_and_get_issue_labels(issue_type)

    if "skip:sub-issue-verification" in issue_labels:
        return

    # it is assumed the subissue is in the repository as the parent issue
    if "class 1" in issue_labels or "class 3" in issue_labels:
        has_linked_test_case = _has_linked_test_case_as_subissue()
        if not has_linked_test_case:
            _raise_for_missed_requirements(
                f"Issue {context.issue_number} of type 'bug' of class 1 or class 3 must have a linked test case as a sub-issue.",
            )

    if "functional" in issue_labels or "technical" in issue_labels:
        has_linked_test_case = _has_linked_test_case_as_subissue()

        if not has_linked_test_case:
            has_linked_test_case = _has_linked_test_case_in_issue_description()
            if not has_linked_test_case:
                _raise_for_missed_requirements(
                    f"Issue {context.issue_number} of type 'story' must have a linked test case as a sub-issue or in the issue description.",
                )


if __name__ == "__main__":
    check_closed_issue()
