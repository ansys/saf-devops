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

from enum import Enum
from typing import Final

_SEVERITY_RANK: Final[dict[str, int]] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def from_string(cls, value: str):
        """Converts a string to the corresponding enum member."""
        for severity_level in cls:
            if severity_level.name.lower() == value.lower():
                return severity_level
        raise ValueError(f"'{value}' is not a valid {cls.__name__} value")

    def __gt__(self, other: "SeverityLevel"):
        return _SEVERITY_RANK[self.name] > _SEVERITY_RANK[other.name]

    def __ge__(self, other: "SeverityLevel"):
        return _SEVERITY_RANK[self.name] >= _SEVERITY_RANK[other.name]

    def __lt__(self, other: "SeverityLevel"):
        return _SEVERITY_RANK[self.name] < _SEVERITY_RANK[other.name]

    def __le__(self, other: "SeverityLevel"):
        return _SEVERITY_RANK[self.name] <= _SEVERITY_RANK[other.name]
