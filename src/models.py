
#!usr/bin/env python3

"""lnkd-report/src/modules.py"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, field_validator
from pathlib import Path
from typing import Optional

def main():
    print("Hello from lnkd-report.modules")

class Account(BaseModel):
    name: str = Field(..., description="Full name of the team member")
    linkedin_url: HttpUrl = Field(..., description="Full LinkedIn profile URL")
    tags_to_watch: list[str] = Field(default_factory=list, description="List of hashtags to filter for")



class Post(BaseModel):
    post_id: str
    author: str
    date: datetime
    content: str
    post_url: str
    hashtags: list[str] = []
    source_account: str
    is_repost: bool = False
    original_author: Optional[str] = None

    @classmethod
    def from_content(cls, **kwargs) -> "Post":
        content = kwargs.get("content", "")
        hashtags = [word for word in content.split() if word.startswith("hashtag#")]
        kwargs["hashtags"] = hashtags
        return cls(**kwargs)

class ConfigFile(BaseModel):
    """
    Represents a validated reference to a YAML configuration file.

    This model ensures that the provided file path is valid and points to
    an acceptable YAML file (.yml or .yaml extension). It helps catch common
    mistakes early before attempting to load configurations.

    Attributes
    ----------
    path : Path
        Path to the YAML configuration file.
    """

    path: Path

    @field_validator("path", mode="before")
    @classmethod
    def check_suffix(cls, v):
        """
        Checks that the provided file path ends with a .yml or .yaml extension.

        Parameters
        ----------
        v : Path
            The input file path to validate.

        Returns
        -------
        Path
            The validated file path.

        Raises
        ------
        ValueError
            If the file does not have a supported YAML extension.
        """
        if v.suffix not in {".yml", ".yaml"}:
            raise ValueError("Configuration file must be a '.yml' or '.yaml' filetype")
        return v

if __name__ == "__main__":
    main()

