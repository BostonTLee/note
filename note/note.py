import os
import json
import subprocess
import datetime
from markdown import Markdown
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from thefuzz import fuzz
from functools import total_ordering
from note.note_id import NoteId


@total_ordering
class Note:
    FILENAME: str = "README.md"
    TAG_MARKER: str = "tags:"
    DATE_MARKER: str = "date:"

    def __init__(self, id: NoteId, notes_dir: Path):
        self.id: NoteId = id
        self.notes_dir: Path = notes_dir
        self.dir: Path = self.notes_dir / str(self.id)
        self.path: Path = self.dir / self.FILENAME
        self._parser = Markdown(extensions=["meta"])
        self.title: str = ""
        self._tag_line: str = ""
        self.body: str = ""
        self.body_lines: List[str] = []
        self.tags: List[str] = []
        self.date: datetime.date = self.id.date
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

    def _parse_title(self, lines) -> Optional[str]:
        lines = [line for line in lines if line != ""]
        return lines[0].replace("# ", "").strip() if len(lines) > 0 else None

    def _parse_date(self, raw_date) -> Optional[datetime.date]:
        try:
            return datetime.date.fromisoformat(raw_date)
        except:
            return None

    def _parse(self):
        with open(self.path, "r") as f:
            text = f.read()
            self._parser.convert(text)
            lines = self._parser.lines
            self.body_lines = lines
            raw_tags = self._parser.Meta.get("tags")
            self._tag_line = raw_tags[0] if raw_tags else None
            raw_date_list = self._parser.Meta.get("date")
            raw_date = raw_date_list[0] if raw_date_list and len(raw_date_list) > 0 else None
            self.date = self._parse_date(raw_date) or self.id.date
            raw_title = self._parser.Meta.get("title")
            self.title = raw_title[0] if raw_title and len(raw_title) > 0 else self._parse_title(lines)
            self.tags: List[str] = (
                [tag.strip() for tag in self._tag_line.split(",") if tag != ""]
                if self._tag_line
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
