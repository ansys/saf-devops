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

import re
from pathlib import Path

import toml
from github_utilities import GitHubLogger


class PyprojectTomlManager:
    """
    A class to manage and extract information from a `pyproject.toml` file.
    """

    def __init__(self, pyproject_toml_path: Path | str):
        """
        Initializes the PyprojectTomlManager by loading the pyproject.toml file.

        Args:
            pyproject_toml_path (Path): The path to the pyproject.toml file.

        Raises:
            FileNotFoundError: If the provided pyproject.toml file does not exist.
        """
        file = (
            Path(pyproject_toml_path)
            if isinstance(pyproject_toml_path, str)
            else pyproject_toml_path
        )

        if not file.exists():
            GitHubLogger.error(title="FILE NOT FOUND", message=str(pyproject_toml_path))
            raise FileNotFoundError(str(pyproject_toml_path))

        try:
            with file.open("r") as fp:
                content = fp.read()
                regex = r"\{\{ cookiecutter\.\S* \}\}"
                content = re.sub(
                    regex,
                    "project",
                    content,
                )  # filter out line to be formatted by cookie-cutter
                self._pyproject_toml_data = toml.loads(content)
        except toml.TomlDecodeError as e:
            GitHubLogger.error(title="ERROR PARSING FILE", message=str(e))
            raise ValueError(f"Error parsing file: {e}") from e
        except Exception:
            raise

    def get_version(self) -> str:
        """
        Returns the version of the project as specified in the pyproject.toml file.

        Returns:
            str: The version of the project.
        """
        version = (
            self._pyproject_toml_data.get("tool", {})  # compatible with Poetry 1.X
            .get("poetry", {})
            .get("version", "")
        )

        if not version:  # compatible with Poetry 2.X
            version = self._pyproject_toml_data.get("project", {}).get("version")

        return version
