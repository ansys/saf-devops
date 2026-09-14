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

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# CVSS severity order used for comparison.
_SEVERITY_ORDER: dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

# NVD CVE API endpoint (no auth required for low-volume queries).
_NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"

# Seconds to wait between NVD requests to respect the public rate limit (5 req/30 s).
_NVD_REQUEST_DELAY = 7.0


def _severity_value(severity: str) -> int:
    """Return the numeric rank for a severity label (case-insensitive)."""
    return _SEVERITY_ORDER.get(severity.lower(), -1)


def _fetch_nvd_severity(cve_id: str) -> str:
    """Return the CVSS severity label for *cve_id* from the NVD API.

    Returns ``"unknown"`` when the CVE is not found or has no score yet.
    """
    url = _NVD_API_URL.format(cve_id=cve_id)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return "unknown"

    vulnerabilities = data.get("vulnerabilities", [])
    if not vulnerabilities:
        return "unknown"

    cve_data = vulnerabilities[0].get("cve", {})
    metrics = cve_data.get("metrics", {})

    # Prefer CVSS v3.1 > v3.0 > v2.0 > v4.0 for broadest coverage.
    for version_key in (
        "cvssMetricV31",
        "cvssMetricV30",
        "cvssMetricV40",
        "cvssMetricV2",
    ):
        entries = metrics.get(version_key, [])
        if entries:
            base_severity = entries[0].get("cvssData", {}).get("baseSeverity", "")
            if base_severity:
                return base_severity.lower()

    return "unknown"


def _evaluate_vulnerabilities(output_file: str, max_allowed_severity: str) -> bool:
    """Parse *output_file* and return ``True`` when the check should fail.

    A failure is triggered when any vulnerability has a CVSS severity strictly
    above *max_allowed_severity*.  Vulnerabilities whose CVE ID cannot be
    resolved are reported as warnings but do **not** cause failure.
    """
    path = Path(output_file)
    if not path.exists():
        print(
            f"[safety_check] ERROR: output file '{output_file}' not found.",
            file=sys.stderr,
        )
        return True

    with path.open(encoding="utf-8") as fh:
        report = json.load(fh)

    vulnerabilities: list[dict] = report.get("vulnerabilities", [])
    if not vulnerabilities:
        print("[safety_check] No vulnerabilities found.")
        return False

    max_allowed_value = _severity_value(max_allowed_severity)
    failed = False

    print(
        f"\n[safety_check] Evaluating {len(vulnerabilities)} vulnerabilities) "
        f"(max allowed severity: {max_allowed_severity.upper()}):\n"
    )

    for vuln in vulnerabilities:
        pkg = vuln.get("package_name", "unknown")
        vid = vuln.get("vulnerability_id", "?")
        cve_id: str = vuln.get("CVE", "") or ""

        if cve_id:
            severity = _fetch_nvd_severity(cve_id)
            time.sleep(_NVD_REQUEST_DELAY)
        else:
            severity = "unknown"

        severity_value = _severity_value(severity)
        exceeds = severity_value > max_allowed_value

        status = "FAIL" if exceeds else ("WARN" if severity == "unknown" else "OK")
        safety_url = f"https://getsafety.com/v/{vid}/97c" if vid and vid != "?" else ""
        nvd_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else ""

        print(
            f"  [{status}] {pkg} (Safety ID: {vid}, CVE: {cve_id or 'N/A'}) -> severity: {severity.upper()}"
        )
        if safety_url or nvd_url:
            url_line = "         "
            if safety_url:
                url_line += f"Safety: {safety_url}"
            if nvd_url:
                if safety_url:
                    url_line += " | "
                url_line += f"NVD: {nvd_url}"
            print(url_line)

        if exceeds:
            failed = True

    print()
    return failed


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--output", help="Path for the safety JSON output file.")
    parser.add_argument(
        "--max-allowed-severity",
        choices=list(_SEVERITY_ORDER.keys()),
        help="Vulnerabilities with severity above this level cause failure.",
    )
    args = parser.parse_args()

    failed = _evaluate_vulnerabilities(args.output, args.max_allowed_severity)

    if failed:
        print("[safety_check] FAILED: vulnerabilities detected.")
        sys.exit(1)
    else:
        print(
            "[safety_check] PASSED: no vulnerabilities above the allowed severity threshold."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
