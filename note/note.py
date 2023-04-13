import os
import json
import subprocess
import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from thefuzz import fuzz
from functools import total_ordering


@dataclass
class NoteSearchResult:
    matched: bool
    matched_tags: List[str] = field(default_factory=list)


@total_ordering
class Note:
    FILENAME: str = "README.md"
    TAG_MARKER: str = "tags:"
    DATE_MARKER: str = "date:"

    def __init__(self, id, notes_dir):
        self.id: str = id
        self.notes_dir: Path = notes_dir
        self.dir: Path = self.notes_dir / self.id
        self.path: Path = self.dir / self.FILENAME
        self.title: Optional[str] = None
        self._tag_line: Optional[str] = None
        self.body: Optional[str] = None
        self.body_lines: Optional[List[str]] = None
        self.tags: List[str] = []
        self.date: Optional[datetime] = None
        self.has_tags: bool = False
        if self.path.exists():
            self._parse()

    def __str__(self):
        return str(self.path)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(int(self.id))

    def _parse_title(self, lines):
        self.title = lines[0].replace("# ", "").strip() if len(lines) > 0 else None

    def _parse_date(self, lines):
        date_line = None
        if len(lines) > 1:
            for line in lines[1:]:
                if line.strip() != "":
                    date_line = line.strip()
                    break
            if date_line and date_line.startswith(self.DATE_MARKER):
                date_line_tokens = date_line.split()
                try:
                    self.date = datetime.date.fromisoformat(date_line_tokens[1])
                except:
                    self.date = None

    def _parse_tags(self, lines):
        if len(lines) > 1:
            final_line = lines[len(lines) - 1].strip()
            if final_line.startswith(self.TAG_MARKER):
                self._tag_line: str = final_line.replace(self.TAG_MARKER, "")
                self.has_tags = True
            else:
                self._tag_line = None
                self.has_tags = False
        else:
            self.has_tags = False

    def _parse(self):
        with open(self.path, "r") as f:
            lines = f.readlines()
            self._parse_title(lines)
            self._parse_date(lines)
            self._parse_tags(lines)

            if self.has_tags:
                if len(lines) > 2:
                    self.body_lines = [line for line in lines[1 : len(lines) - 2]]
                    self.body = "".join(self.body_lines)
                    self.body_lines = [
                        line.strip() for line in self.body_lines if line.strip() != ""
                    ]
                else:
                    self.body_lines = None
                    self.body = None
            else:
                if len(lines) > 2:
                    self.body_lines = [line for line in lines[1 : len(lines) - 1]]
                    self.body = "".join(self.body_lines)
                    self.body_lines = [
                        line.strip() for line in self.body_lines if line.strip() != ""
                    ]
                else:
                    self.body_lines = None
                    self.body = None

            self.tags: List[str] = (
                [tag.strip() for tag in self._tag_line.split(",") if tag != ""]
                if self.has_tags
                else []
            )

    def create(self):
        if not self.dir.is_dir():
            self.dir.mkdir()

    def edit(self):
        self.create()
        cmd = os.environ.get("EDITOR", "vi") + " " + str(self.path)
        subprocess.call(cmd, shell=True)

    def print(self, how="user"):
        if how == "full":
            print(self.title)
            print(self.body)
            print(self.tags)
        elif how == "summary":
            print(f"{self.id}: {self.title}")
            print(f"    date: {self.date}")
            print(f"    tags: {self.tags}")
        elif how == "plain":
            padded_date = self.date.isoformat() if self.date else " " * 10
            print(f"{self.id}: ({padded_date}) {self.title}: {self.tags}")
        elif how == "json":
            dict_repr = {
                "id": self.id,
                "date": self.date,
                "title": self.title,
                "tags": self.tags,
            }
            print(json.dumps(dict_repr, default=str))

    def search_body(self, search_string, how="exact") -> int:
        search_string = search_string.lower()
        if how == "exact":
            return self.body.lower().count(search_string) + self.title.lower().count(
                search_string
            )
        if how == "fuzzy":
            match_count = 0
            for line in self.body_lines:
                if fuzz.partial_ratio(search_string, line.lower()) > 70:
                    match_count += 1
            if fuzz.partial_ratio(search_string, self.title.lower()) > 70:
                match_count += 1
            return match_count
        return 0

    def search_tags(self, search_string, how="exact") -> int:
        search_string = search_string.lower()
        if how == "exact":
            match_count = 0
            for tag in self.tags:
                if search_string in tag:
                    match_count += 1
                return match_count
        if how == "fuzzy":
            match_count = 0
            for tag in self.tags:
                if fuzz.partial_ratio(search_string, tag) > 70:
                    match_count += 1
            return match_count
        return 0
