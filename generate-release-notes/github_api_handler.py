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

import requests


class APIHandler:
    @staticmethod
    def get_items_from_all_github_pages(url, headers=None, params=None):
        """
        Retrieve and aggregate items from all pages of a paginated GitHub API endpoint.

        It iterates over all available pages, collecting items until there are no
        more pages to retrieve.

        Args:
            url (str): The base URL of the GitHub API endpoint from which to fetch items.
            params (dict, optional): A dictionary of query parameters to include in the
                                     request. Defaults to an empty dictionary. Note that
                                     the function modifies this dictionary to include
                                     pagination-related parameters.

        Returns:
            list: A list containing all items retrieved from all pages of the GitHub API endpoint.

        Example:
            items = get_items_from_all_github_pages("https://api.github.com/repos/owner/repo/issues")
            print(items)

        Notes:
            - The function uses a `per_page` parameter of 100 to maximize the number
              of items retrieved per page, as allowed by many APIs.
            - The function automatically handles the "Link" header in the response to
              determine if there are additional pages and to extract the URL of the next
              page when available.
            - The function modifies the `params` argument in place to include pagination
              parameters (`per_page` and `page`). If you want to preserve the original
              `params` dictionary, make a copy before passing it to the function.
        """
        headers = headers or {}
        params = params or {}
        params["per_page"] = 100
        params["page"] = 1

        items = []

        while url is not None:
            if "&page" in url:  # The next pages includes the initial params.
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            items.extend(response.json())

            # GitHub API provides a "Link" header with pagination information
            url = response.links.get("next", {}).get("url")

        return items
