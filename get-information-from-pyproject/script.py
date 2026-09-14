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

import toml

file_path = os.getenv("FILE_PATH")

with open(file_path, "r") as toml_file:
    toml_data = toml.load(toml_file)

if toml_data.get("tool", {}).get("poetry", {}).get("version"):
    version = toml_data.get("tool").get("poetry").get("version")
    package_name = toml_data.get("tool").get("poetry").get("name")
else:
    version = toml_data.get("project").get("version")
    package_name = toml_data.get("project").get("name")

major_version = version.split(".")[0] if version else None
minor_version = version.split(".")[1] if version else None
patch_version = version.split(".")[2] if version else None


output_file = os.environ["GITHUB_OUTPUT"]
with Path(output_file).open("a") as file:
    file.write(f"package_version={version}\n")
    file.write(f"package_name={package_name}\n")
    file.write(f"major_version={major_version}\n")
    file.write(f"minor_version={minor_version}\n")
    file.write(f"patch_version={patch_version}\n")
