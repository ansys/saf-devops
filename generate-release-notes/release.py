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

from datetime import datetime

from packaging.version import Version, parse


class ReleaseInformation:
    def __init__(self, release_name: str, description: str, published_at: datetime):
        self.release_name = release_name
        self.description = description
        self.published_at = published_at
        self._version: Version | None = None
        self._release_label: str | None = None
        self._base_name: str | None = None
        self._previous_release: Version | None = None

    @property
    def base_name(self) -> str:
        if not self._base_name:
            self._set_private_fields()
        return self._base_name  # pyright: ignore[reportReturnType]

    @property
    def release_label(self) -> str:
        if not self._release_label:
            self._set_private_version_fields()
        return self._release_label  # pyright: ignore[reportReturnType]

    @property
    def version(self) -> Version:
        if not self._version:
            self._set_private_version_fields()
        return self._version  # pyright: ignore[reportReturnType]

    @property
    def previous_version(self) -> Version:
        if not self._previous_release:
            self._set_private_fields()
        return self._previous_release  # pyright: ignore[reportReturnType]

    @property
    def previous_tag_name(self) -> str:
        if self.release_label != "":
            return f"{self.release_label}-v{self.previous_version}"
        return f"v{self.previous_version}"

    def _set_private_version_fields(self):
        if "-" not in self.release_name:
            self._release_label = ""
            self._version_str = self.release_name
        else:
            parts = self.release_name.split("-")
            self._version_str = parts[0]
            self._release_label = "-".join(parts[1:]) if len(parts) > 1 else ""
        self._version = parse(self._version_str)

    def _set_private_fields(self):
        if self.version.is_devrelease:
            if self.version.dev == 0:
                self._previous_release = Version(
                    f"v{self.version.major}.{self.version.minor - 1}.0",
                )
            else:
                self._previous_release = Version(
                    f"v{self.version.major}.{self.version.minor}.dev{self.version.dev - 1}",  # pyright: ignore[reportOptionalOperand]
                )
            self._base_name = "main"
            return

        if self.version.micro == 0:
            if self.version.minor != 0:
                self._previous_release = Version(
                    f"v{self.version.major}.{self.version.minor - 1}.0",
                )
            elif self.version.major != 0:
                self._previous_release = Version(
                    f"v{self.version.major - 1}.0.0",
                )
            else:
                raise NotImplementedError("Not implemented yet for 0.0.0 release.")
            self._base_name = "main"
        else:
            self._previous_release = Version(
                f"v{self.version.major}.{self.version.minor}.{self.version.micro - 1}",
            )
            if self.release_label == "":
                self._base_name = f"release/v{self.version.major}.{self.version.minor}"
            else:
                self._base_name = f"release/{self.release_label}-v{self.version.major}.{self.version.minor}"
