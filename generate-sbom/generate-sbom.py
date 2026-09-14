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

import json
import os
import subprocess
import sys

REQUIREMENTS_PATH = "poetry.lock"
OUTPUT_PATH = "sbom.json"


def get_poetry_version() -> str:
    return os.environ["POETRY_VERSION"]


def get_project_version() -> str:
    return os.environ["PROJECT_VERSION"]


def get_project_name() -> str:
    return os.environ["PROJECT_NAME"]


def generate_sbom() -> None:
    base_arg_list = [sys.executable, "-m", "cyclonedx_py"]

    flags = [
        "-o",
        OUTPUT_PATH,
    ]

    project_dir = [os.path.dirname(REQUIREMENTS_PATH)]
    subprocess.run(
        base_arg_list + ["poetry", "--no-dev"] + flags + project_dir,
        check=False,
    )

    with open(OUTPUT_PATH, "r") as read_handle:
        json_data = read_handle.read()
        if not json_data.strip():
            print("SBOM file is empty or invalid.")
            return
        obj = json.loads(json_data)
    obj["metadata"]["component"] = {
        "version": get_project_version(),
        "type": "application",
        "name": get_project_name(),
    }
    obj["metadata"]["authors"] = [{"name": "ANSYS, Inc."}]

    components = obj.get("components", [])

    prod_components = []
    for component in components:
        try:
            props = component["properties"]
        except KeyError:
            props = None
        if props is not None:
            for prop in props:
                if prop["name"] == "cdx:poetry:group" and prop["value"] == "main":
                    print(
                        f"Keeping {component['name']} in SBOM - identified as a main component"
                    )
                    prod_components.append(component)
                else:
                    pass
    obj["components"] = prod_components

    json_formatted_str = json.dumps(obj, indent=4)

    with open(OUTPUT_PATH, "w") as write_handle:
        write_handle.write(json_formatted_str)


if __name__ == "__main__":
    generate_sbom()
