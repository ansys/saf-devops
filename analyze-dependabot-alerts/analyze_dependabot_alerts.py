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
from github_utilities import (
    GitHubLogger,
    send_to_github_step_summary,
)
from poetry_export_dependencies_extractor import (
    get_dependencies_from_poetry_export_output,
)
from severity_level import SeverityLevel


class GitHubContext:
    def __init__(self):
        self.github_repository: str = os.environ["GITHUB_REPOSITORY"]
        self.github_ref: str = os.environ["GITHUB_REF"]
        self.severity: SeverityLevel = SeverityLevel.from_string(
            os.environ["SEVERITY_LEVEL"]
        )
        self.manifest_path: str = os.environ["MANIFEST_PATH"]
        self.filter_out_non_production_dependencies: bool = bool(
            os.environ["FILTER_OUT_NON_PRODUCTION_DEPENDENCIES"].lower() == "true"
        )


class Alert:
    def __init__(self, package: str, advisory: str, cve: str):
        self.package = package
        self.advisory = advisory
        self.cve = cve


def _get_dependabot_alerts() -> list[Alert]:
    """
    Fetches and returns a set of alerts from Dependabot for a given GitHub repository.

    This method interacts with GitHub's Dependabot service to retrieve the list of security alerts associated
    with the dependencies specified in a repository's manifest file. It filters the alerts based on the
    provided severity level threshold.

    The GitHub API token required to authenticate the requests must be available as the `GITHUB_TOKEN`
    environment variable.

    Returns:
    --------
    list[dict[str, Any]]
        A list of dictionaries representing the alerts that match or exceed the specified
        severity threshold.
    """
    github_context = GitHubContext()

    if github_context.github_ref != "refs/heads/main":
        GitHubLogger.info(
            title="Dependabot Alerts analysis",
            message="Dependabot Alerts analysis has been skipped. It is only executed for the main branch.",
        )
        return []

    github_token = os.getenv("GITHUB_TOKEN")
    page_count = 0
    url = f"https://api.github.com/repos/{github_context.github_repository}/dependabot/alerts?state=open&per_page=100"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    raw_alerts: list[dict[str, Any]] = []

    while url is not None:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        page_alerts_response = response.json()
        raw_alerts.extend(page_alerts_response)

        url = (
            response.links["next"]["url"] if "next" in response.links else None
        )  # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
        page_count += 1

    selected_raw_alerts = [
        alert
        for alert in raw_alerts
        if alert["dependency"]["manifest_path"] == github_context.manifest_path
    ]

    info_alerts: list[dict[str, Any]] = []
    for alert in selected_raw_alerts:
        if (
            SeverityLevel.from_string(alert["security_advisory"]["severity"])
            >= github_context.severity
        ):
            info_alerts.append(
                Alert(
                    package=alert["dependency"]["package"]["name"],
                    advisory=alert["security_advisory"]["summary"],
                    cve=alert["security_advisory"]["cve_id"],
                )
            )

    # Remove duplicate alerts by package name (keep the first occurrence)
    unique_alerts = {}
    for alert in info_alerts:
        if alert.package not in unique_alerts:
            unique_alerts[alert.package] = alert

    # Return alerts sorted by package name
    return [unique_alerts[pkg] for pkg in sorted(unique_alerts)]


def _get_alerts() -> list[Alert]:
    """
    Retrieves Dependabot alerts that affect dependencies.
    Args:
        filter_out_alert_on_non_production_dependencies (bool, optional):
            If True (default), filters out alerts that are not related to production dependencies.
        list[Alert]: A list of alerts affecting dependencies.
    Notes:
        - Alerts are fetched from Dependabot.
        - Production dependencies are determined using the Poetry export output.
        - If filtering is disabled, all alerts are returned regardless of dependency type.
    """
    github_context = GitHubContext()
    alerts = _get_dependabot_alerts()

    if not github_context.filter_out_non_production_dependencies:
        return alerts

    production_dependencies = get_dependencies_from_poetry_export_output()
    production_alerts = [
        alert for alert in alerts if alert.package in production_dependencies
    ]

    return production_alerts


def _send_analysis_report_to_github_summary(
    production_dependabot_alerts: list[Alert],
):
    github_context = GitHubContext()

    send_to_github_step_summary(
        "# Dependabot Alerts Report",
        "## Analysis configuration",
        f"- Manifest path: {github_context.manifest_path}",
        f"- Severity level threshold: {github_context.severity.name}",
        f"- Filter out non-production dependencies: {github_context.filter_out_non_production_dependencies}",
        "",
    )

    if github_context.github_ref != "refs/heads/main":
        send_to_github_step_summary(
            ":exclamation: Dependabot alerts are not analyzed because the current branch is not main.",
            "",
        )

        return

    send_to_github_step_summary(
        "## Analysis results",
    )

    if not production_dependabot_alerts:
        send_to_github_step_summary(
            "### :white_check_mark: No alert detected in the production dependencies.",
        )
    else:
        send_to_github_step_summary("### :red_circle: Alert(s) detected")
        for alert in production_dependabot_alerts:
            send_to_github_step_summary(f"#### {alert.package}")
            send_to_github_step_summary(f"- {alert.advisory} ({alert.cve})")
            send_to_github_step_summary("")


def analyze_dependabot_alerts():
    dependabot_alerts = _get_dependabot_alerts()

    _send_analysis_report_to_github_summary(
        dependabot_alerts,
    )

    if dependabot_alerts:
        message = "Dependabot alerts detected. Please refer to the GitHub Step Summary for more details."
        GitHubLogger.error(
            title="DEPENDABOT_ALERTS_DETECTED",
            message=message,
        )
        raise ValueError(message)


if __name__ == "__main__":
    analyze_dependabot_alerts()
