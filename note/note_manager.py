import re
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from note.note import Note
from collections import defaultdict


class NoteManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.index = self._generate_note_index()

    def _generate_note_index(self) -> Dict[str, Note]:
        index = {}
        for note in self.list_notes():
            index[note.id] = note
        return index

    def generate_note_id(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def list_note_ids(self):
        return [
            str(entry.name)
            for entry in self.root_dir.iterdir()
            if entry.is_dir() and self.is_valid_note_id(str(entry.name))
        ]

    def list_notes(self):
        notes = sorted([Note(id, self.root_dir) for id in self.list_note_ids()])
        return notes

    def is_valid_note_id(self, note_id):
        exp = r"^[0-9]{14}$"
        return re.match(exp, note_id)

    def print_notes(self, how="summary"):
        for note in reversed(self.index.values()):
            note.print(how=how)

    def find_last_note_id(self) -> str:
        return max(self.list_note_ids())

    def create_note(self):
        id = self.generate_note_id()
        note = Note(id, self.root_dir)
        note.edit()

    def edit_note(self, id):
        note = Note(id, self.root_dir)
        note.edit()

    def search_tags(self, search_string, how="exact") -> Dict[str, int]:
        ret_dict = defaultdict(int)
        for note in self.index.values():
            num_hits = note.search_tags(search_string, how)
            if num_hits > 0:
                ret_dict[note.id] = num_hits
        return ret_dict

    def search_body(self, search_string, how="exact") -> Dict[str, int]:
        ret_dict = defaultdict(int)
        for note in self.index.values():
            num_hits = note.search_body(search_string, how)
            if num_hits > 0:
                ret_dict[note.id] = num_hits
        return ret_dict

    def _merge_searches_union(self, searches: List[Dict[str, int]]):
        merged_search = defaultdict(int)
        for search in searches:
            for key in search.keys():
                if search.get(key, 0) > 0:
                    merged_search[key] += search[key]
        return merged_search

    def _merge_searches_intersection(self, searches: List[Dict[str, int]]):
        merged_search = defaultdict(int)
        for search in searches:
            for key in search.keys():
                if all([search.get(key, 0) > 0 for search in searches]):
                    merged_search[key] += search[key]
        return merged_search

    def search_all(
        self, search_strings: List[str], how_tags, how_body, join_method="or"
    ):
        searches = []
        for search_string in search_strings:
            tag_hits = self.search_tags(search_string, how_tags)
            body_hits = self.search_body(search_string, how_body)
            searches.append(self._merge_searches_union([tag_hits, body_hits]))
        if join_method == "and":
            hits = self._merge_searches_intersection(searches)
            return hits
        elif join_method == "or":
            hits = self._merge_searches_union(searches)
            return hits
        else:
            raise ValueError('join must be one of "and", "or"')

    def print_search(
        self, search_strings: List[str], how_tags, how_body, how_print, join_method="or"
    ):
        hits = self.search_all(
            search_strings=search_strings,
            how_tags=how_tags,
            how_body=how_body,
            join_method=join_method,
        )
        sorted_hits = hits.keys()
        for id in sorted_hits:
            self.index[id].print(how=how_print)
