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
from pathlib import Path
from urllib.parse import quote

import requests

# Get environment variables, using os.environ[] instead of os.getenv() to make it fail if not set
ORGANIZATION = os.environ["ORGANIZATION"]
OUTPUT_FILE = os.environ["GITHUB_OUTPUT"]
PACKAGE_NAME = os.environ["PACKAGE_NAME"]
PACKAGE_TAG = os.environ["PACKAGE_TAG"]
TOKEN = os.environ["GITHUB_TOKEN"]

PACKAGE_TYPE = "container"  # For Docker images


def set_as_github_outputs(**outputs) -> None:
    with Path(OUTPUT_FILE).open("a") as file:
        file.writelines(f"{key}={value}\n" for key, value in outputs.items())


package_name_encoded = quote(PACKAGE_NAME, safe="")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}

url = f"https://api.github.com/orgs/{ORGANIZATION}/packages/{PACKAGE_TYPE}/{package_name_encoded}/versions"
response = requests.get(url, headers=headers)
response.raise_for_status()

tags = []
for package in response.json():
    package_tags = package.get("metadata", {}).get("container", {}).get("tags", [])
    tags.extend(package_tags)

tag_exists = PACKAGE_TAG in tags
set_as_github_outputs(tags=",".join(tags), tag_exists=tag_exists)
