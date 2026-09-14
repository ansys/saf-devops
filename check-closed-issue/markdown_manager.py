# Copyright (C) 2026 - 2026 ANSYS, Inc. and/or its affiliates.
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


class MarkdownManager:
    @staticmethod
    def find_next_section_index(lines: list[str], start_index: int) -> int:
        """Find the start of the next section or end of content."""
        if not lines:
            return 0
        for i in range(start_index, len(lines)):
            if re.match(r"^#.*$", lines[i]):
                return i
        return len(lines) - 1
