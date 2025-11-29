"""
Content Extraction Service for OCA GitHub repositories.

Extracts clean descriptions from modules with fallback strategy:
1. readme/DESCRIPTION.rst (clean, preferred)
2. README.rst (needs cleaning)
3. README.md (needs cleaning)
4. __manifest__.py description field (last resort)
"""

import re
import time
from datetime import datetime
from typing import Optional, Tuple

import requests

from ..config import get_settings

settings = get_settings()


class RateLimitError(Exception):
    """Raised when GitHub rate limit is exceeded."""

    def __init__(self, reset_time: int):
        self.reset_time = reset_time
        super().__init__(f"Rate limit exceeded. Resets at {datetime.fromtimestamp(reset_time)}")


class ContentExtractionService:
    """Service for extracting and cleaning module descriptions from GitHub."""

    def __init__(self):
        self.token = settings.gh_token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.raw",  # Get raw content directly
        }
        self.base_url = "https://api.github.com"
        self.raw_base_url = "https://raw.githubusercontent.com"

    def _check_rate_limit(self, response: requests.Response) -> None:
        """Check if rate limit is exceeded and raise error with reset time."""
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if remaining == "0":
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitError(reset_time)

    def _get_raw_content(self, repo_name: str, version: str, path: str) -> Optional[str]:
        """
        Get raw content from GitHub using raw.githubusercontent.com.
        This doesn't count against API rate limit.
        """
        url = f"{self.raw_base_url}/OCA/{repo_name}/{version}/{path}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            return None
        except requests.RequestException:
            return None

    def _get_api_content(self, repo_name: str, version: str, path: str) -> Optional[str]:
        """
        Get content using GitHub API.
        Counts against rate limit but more reliable.
        """
        url = f"{self.base_url}/repos/OCA/{repo_name}/contents/{path}?ref={version}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            self._check_rate_limit(response)

            if response.status_code == 200:
                # With Accept: application/vnd.github.v3.raw, we get raw content
                return response.text
            return None
        except requests.RequestException:
            return None

    def get_clean_description(
        self, repo_name: str, version: str, module_name: str
    ) -> Tuple[Optional[str], str]:
        """
        Get clean description for a module with fallback strategy.

        Args:
            repo_name: OCA repository name (e.g., "l10n-spain")
            version: Odoo version (e.g., "16.0")
            module_name: Technical module name (e.g., "l10n_es_aeat_mod303")

        Returns:
            Tuple of (clean_description, source)
            source can be: "description_rst", "readme_rst_cleaned",
                          "readme_md_cleaned", "manifest", "none"
        """
        # Strategy 1: Try readme/DESCRIPTION.rst (cleanest source)
        description_path = f"{module_name}/readme/DESCRIPTION.rst"
        content = self._get_raw_content(repo_name, version, description_path)

        if content and content.strip():
            cleaned = self._clean_rst_minimal(content)
            if cleaned:
                return (cleaned, "description_rst")

        # Strategy 2: Try README.rst and clean it
        readme_rst_path = f"{module_name}/README.rst"
        content = self._get_raw_content(repo_name, version, readme_rst_path)

        if content and content.strip():
            cleaned = self.clean_readme_rst(content)
            if cleaned:
                return (cleaned, "readme_rst_cleaned")

        # Strategy 3: Try README.md and clean it
        readme_md_path = f"{module_name}/README.md"
        content = self._get_raw_content(repo_name, version, readme_md_path)

        if content and content.strip():
            cleaned = self.clean_readme_md(content)
            if cleaned:
                return (cleaned, "readme_md_cleaned")

        # Strategy 4: No description found
        return (None, "none")

    def _clean_rst_minimal(self, content: str) -> str:
        """
        Minimal cleaning for DESCRIPTION.rst files.
        These are usually already clean, just need basic normalization.
        """
        # Remove any leading/trailing whitespace
        content = content.strip()

        # Normalize multiple newlines
        content = re.sub(r"\n{3,}", "\n\n", content)

        return content

    def clean_readme_rst(self, content: str) -> str:
        """
        Clean README.rst from OCA-generated noise:
        - Badges (.. image::, |badge1|)
        - RST comments (.. !!!...)
        - Image directives (:target:, :alt:)
        - Title underlines (====, ----)
        - Excessive whitespace
        """
        # Remove badge references |badge1| |badge2| etc
        content = re.sub(r"\|badge\d+\|", "", content)

        # Remove .. |badgeX| image:: lines and following lines
        content = re.sub(
            r"\.\.\s+\|badge\d+\|\s+image::.*?(?=\n\n|\n\.\.|$)", "", content, flags=re.DOTALL
        )

        # Remove .. image:: blocks (including :target:, :alt:, :width: etc)
        content = re.sub(r"\.\.\s+image::.*?(?=\n\n|\n[^\s:]|$)", "", content, flags=re.DOTALL)

        # Remove OCA-generated comment blocks
        content = re.sub(r"\.\.\s*\n\s*!+.*?!+", "", content, flags=re.DOTALL)

        # Remove RST directives we don't want
        directives_to_remove = [
            r"\.\.\s+contents::.*?(?=\n\n|\n\.\.|$)",
            r"\.\.\s+sectnum::.*?(?=\n\n|\n\.\.|$)",
            r"\.\.\s+raw::.*?(?=\n\n|\n\.\.|$)",
        ]
        for pattern in directives_to_remove:
            content = re.sub(pattern, "", content, flags=re.DOTALL)

        # Remove title underlines (===, ---, ~~~, etc.) but keep the title text
        content = re.sub(r'^[=\-~`\'"^_*+#]+\s*$', "", content, flags=re.MULTILINE)

        # Remove :target: and :alt: lines
        content = re.sub(
            r"^\s*:(target|alt|width|height|scale|align):.*$", "", content, flags=re.MULTILINE
        )

        # Remove Table of Contents section
        content = re.sub(
            r"\*\*Table of contents\*\*.*?(?=\n\n[A-Z]|\n\n\*\*[A-Z]|$)",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove Credits/Authors section at the end
        content = re.sub(
            r"(Credits|Authors|Contributors|Maintainers?)\s*[-=]*\s*$.*",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove "This module is maintained by" section
        content = re.sub(
            r"This module is maintained by.*?$", "", content, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove OCA banner text
        content = re.sub(r"Odoo Community Association.*?(?=\n\n|$)", "", content, flags=re.DOTALL)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Clean up leading/trailing whitespace on each line
        lines = [line.rstrip() for line in content.split("\n")]
        content = "\n".join(lines)

        # Remove leading/trailing blank lines
        content = content.strip()

        # If content is too short after cleaning, it's probably just noise
        if len(content) < 50:
            return ""

        return content

    def clean_readme_md(self, content: str) -> str:
        """
        Clean README.md from badges and noise:
        - Badge images ![](url)
        - Linked badges [![](url)](url)
        - HTML comments
        - Excessive headers
        """
        # Remove linked badges [![...](...)][...]
        content = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", content)
        content = re.sub(r"\[!\[.*?\]\(.*?\)\]\[.*?\]", "", content)

        # Remove badge images ![badge](url)
        content = re.sub(r"!\[.*?\]\(.*?\)", "", content)

        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

        # Remove HTML images
        content = re.sub(r"<img[^>]*>", "", content, flags=re.IGNORECASE)

        # Remove reference-style links definitions [badge]: url
        content = re.sub(r"^\[.*?\]:\s*http.*$", "", content, flags=re.MULTILINE)

        # Remove Credits/Authors section
        content = re.sub(
            r"^#{1,3}\s*(Credits|Authors|Contributors|Maintainers?).*$.*",
            "",
            content,
            flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )

        # Remove "This module is maintained by" section
        content = re.sub(
            r"This module is maintained by.*?$", "", content, flags=re.DOTALL | re.IGNORECASE
        )

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Clean up leading/trailing whitespace
        content = content.strip()

        # If content is too short after cleaning, it's probably just noise
        if len(content) < 50:
            return ""

        return content

    def get_rate_limit_status(self) -> dict:
        """Get current GitHub API rate limit status."""
        url = f"{self.base_url}/rate_limit"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                core = data.get("resources", {}).get("core", {})
                return {
                    "limit": core.get("limit", 0),
                    "remaining": core.get("remaining", 0),
                    "reset": core.get("reset", 0),
                    "reset_datetime": datetime.fromtimestamp(core.get("reset", 0)),
                }
        except requests.RequestException:
            pass
        return {"limit": 0, "remaining": 0, "reset": 0}


# Singleton
_content_extraction_service = None


def get_content_extraction_service() -> ContentExtractionService:
    """Get singleton instance of ContentExtractionService."""
    global _content_extraction_service
    if _content_extraction_service is None:
        _content_extraction_service = ContentExtractionService()
    return _content_extraction_service
