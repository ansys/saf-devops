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
from typing import Any

GITHUB_OUTPUT_FILE_ENV_VAR = "GITHUB_OUTPUT"
GITHUB_ENV_FILE_ENV_VAR = "GITHUB_ENV"
GITHUB_STEP_SUMMARY_FILE_ENV_VAR = "GITHUB_STEP_SUMMARY"
DEBUG_MODE_ENV_VAR = "RUNNER_DEBUG"


class GitHubLogger:
    @staticmethod
    def info(title: str, message: str) -> None:
        print(f"::notice title={title} :: {message}")

    @staticmethod
    def debug(title: str, message: str) -> None:
        runner_debug_mode = os.getenv("RUNNER_DEBUG")

        if runner_debug_mode == "1":
            print(f"::debug title={title} :: {message}")

    @staticmethod
    def error(title: str, message: str) -> None:
        print(f"::error title={title} :: {message}")

    @staticmethod
    def warning(title: str, message: str) -> None:
        print(f"::warning title={title} :: {message}")


class WorkflowLogger:
    def __init__(self):
        self.errors: list[str] = []

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def print_errors(self) -> None:
        """Print all errors."""
        for error in self.errors:
            send_to_github_step_summary(f"❌ {error}")

    def get_errors_as_string(self) -> str:
        """Get all errors as a single string."""
        return "\n".join(self.errors)


def set_as_github_outputs(**outputs: Any) -> None:
    output_file = os.getenv(GITHUB_OUTPUT_FILE_ENV_VAR)

    if output_file:
        with Path(output_file).open("a") as file:
            file.writelines(f"{key}={value}\n" for key, value in outputs.items())


def set_as_github_environment_variables(**variables: Any) -> None:
    environment_file = os.getenv(GITHUB_ENV_FILE_ENV_VAR)

    if environment_file:
        with Path(environment_file).open("a") as file:
            file.writelines(
                f"{key.upper()}={value}\n" for key, value in variables.items()
            )


def send_to_github_step_summary(*messages: str) -> None:
    step_summary_file = os.getenv(GITHUB_STEP_SUMMARY_FILE_ENV_VAR)

    if step_summary_file:
        with Path(step_summary_file).open("a", encoding="utf-8") as file:
            file.writelines(f"{message}\n" for message in messages)
