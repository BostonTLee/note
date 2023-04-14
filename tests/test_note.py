import textwrap
import datetime
from unittest.mock import patch, mock_open
from note.note import Note
from note.note_id import NoteId
from pathlib import Path


def test_path_correctness():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
        assert (
            test_note.path
            == TEST_NOTES_DIR_PATH / str(TEST_NOTE_ID) / test_note.FILENAME
        )
        # mock_file.assert_called_with(f"{TEST_NOTES_DIR_PATH}/{TEST_NOTE_ID}")


def test_path_opened_if_exists():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
            print(test_note)
            mock_file.assert_called_with(test_note.path, "r")


def test_title_parsed():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    file_data = textwrap.dedent(
        """\
        # This is a test file

        body"""
    )
    with patch("builtins.open", mock_open(read_data=file_data)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
            assert test_note.title == "This is a test file"


def test_tags_parsed():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    file_data = textwrap.dedent(
        """\
        # This is a test file

        body

        tags: tag 1, tag 2"""
    )
    with patch("builtins.open", mock_open(read_data=file_data)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
            assert test_note.tags == ["tag 1", "tag 2"]


def test_date_parsed_if_present():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    file_data = textwrap.dedent(
        """\
        # This is a test file

        date: 2021-09-21

        body

        tags: tag 1, tag 2"""
    )
    with patch("builtins.open", mock_open(read_data=file_data)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
            assert test_note.date == datetime.date(2021, 9, 21)


def test_date_inferred_if_not_present():
    TEST_NOTE_ID = NoteId("20230414170046")
    TEST_NOTES_DIR_PATH = Path("test_notes")
    file_data = textwrap.dedent(
        """\
        # This is a test file

        body

        tags: tag 1, tag 2"""
    )
    with patch("builtins.open", mock_open(read_data=file_data)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            test_note = Note(TEST_NOTE_ID, TEST_NOTES_DIR_PATH)
            assert test_note.date == datetime.date(2023, 4, 14)
