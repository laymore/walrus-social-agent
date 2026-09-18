"""
Customer Profile Data Model and Entity Extraction Engine.
Defines customer memory structures for long-term on-chain persistence on Walrus.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class InteractionHistory(BaseModel):
    comment: str
    response: str
    timestamp: str


class CustomerProfile(BaseModel):
    author: str
    birth_year: Optional[int] = None
    can_chi: Optional[str] = None
    nap_am: Optional[str] = None
    primary_need: str = "GENERAL_INQUIRY"
    interactions_count: int = 1
    first_seen: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_seen: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    history: List[InteractionHistory] = []
    walrus_synced: bool = False
    source: str = "WALRUS_PRIMARY"

    def to_walrus_fact(self, last_comment: str = "", last_response: str = "") -> str:
        """Serializes the profile into a high-density, semantic-searchable text fact for Walrus Memory."""
        cc_info = f"({self.can_chi} - {self.nap_am})" if self.can_chi and self.nap_am else ""
        year_info = f"Born: {self.birth_year} {cc_info}".strip() if self.birth_year else "Born: Unknown"
        recent_context = ""
        if last_comment and last_response:
            recent_context = f' Latest: "{last_comment}" -> "{last_response}".'
        elif self.history:
            h = self.history[-1]
            recent_context = f' Latest: "{h.comment}" -> "{h.response}".'

        return (
            f"[SOCIAL_CRM_PROFILE] User: @{self.author}. "
            f"Interactions: {self.interactions_count} sessions. "
            f"{year_info}. "
            f"Focus: {self.primary_need}. "
            f"{recent_context} "
            f"LastActive: {self.last_seen}."
        ).strip()

    @classmethod
    def from_walrus_text(cls, author: str, raw_text: str) -> Optional["CustomerProfile"]:
        """Parses raw text retrieved from Walrus Memory semantic search into a structured profile."""
        if not raw_text:
            return None

        clean_author = author.lower().replace("@", "").strip()
        matching_line = None
        for line in raw_text.split("\n"):
            if clean_author in line.lower():
                matching_line = line
                break

        if not matching_line:
            return None

        profile = cls(author=author, source="WALRUS_PRIMARY")

        # Extract birth year
        m_year = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", matching_line)
        if m_year:
            profile.birth_year = int(m_year.group(1))

        # Extract Lunar Can Chi & Element (e.g. At Hoi - Son Dau Hoa)
        m_cc = re.search(r"\(([\w\s]+)\s*-\s*([\w\s]+)\)", matching_line)
        if m_cc:
            profile.can_chi = m_cc.group(1).strip()
            profile.nap_am = m_cc.group(2).strip()

        # Extract focus / need
        m_need = re.search(r"(?:Focus|Nhu cầu):\s*([^.]+)", matching_line, re.IGNORECASE)
        if m_need:
            profile.primary_need = m_need.group(1).strip()
        elif any(k in matching_line.lower() for k in ["tài lộc", "tiền", "wealth", "career"]):
            profile.primary_need = "CAREER_AND_WEALTH"
        elif any(k in matching_line.lower() for k in ["tình duyên", "love", "relationship"]):
            profile.primary_need = "RELATIONSHIP_AND_LOVE"

        # Extract interactions count
        m_count = re.search(r"(?:Interactions|Tương tác):\s*(\d+)", matching_line, re.IGNORECASE)
        if m_count:
            profile.interactions_count = int(m_count.group(1))

        return profile
