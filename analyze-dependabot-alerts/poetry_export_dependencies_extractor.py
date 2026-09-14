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

from pathlib import Path

RAW_PRODUCTION_DEPS_DIRECTORY = Path("raw_production_deps")
RAW_PRODUCTION_DEPS_NAME = "raw_production_dependencies.txt"
RAW_PRODUCTION_DEPS = RAW_PRODUCTION_DEPS_DIRECTORY / RAW_PRODUCTION_DEPS_NAME


def get_dependencies_from_poetry_export_output() -> set[str]:
    with RAW_PRODUCTION_DEPS.open("r") as open_file:
        raw_data = open_file.readlines()

    packages: list[str] = []
    for line in raw_data:
        if "==" not in line:
            continue

        split_line = line.split("==")
        packages.append(split_line[0])

    return set(packages)
