import pytest
import datetime
from note.note_id import NoteId


def test_fail_init_invalid_id_str():
    invalid_note_id_str = "orgblorg"
    with pytest.raises(Exception) as e_info:
        test_id = NoteId(invalid_note_id_str)


def test_valid_check_fails_invalid_id_str():
    invalid_note_id_str = "orgblorg"
    assert not NoteId.is_valid_note_id(invalid_note_id_str)


def test_valid_check_succeeds_valid_id_str():
    note_id_str = "20230414170046"
    assert NoteId.is_valid_note_id(note_id_str)


def test_return_proper_dt():
    note_id_str = "20230414170046"
    note_id = NoteId(note_id_str)
    assert note_id.dt == datetime.datetime(2023, 4, 14, 17, 0, 46)


def test_return_proper_date():
    note_id_str = "20230414170046"
    note_id = NoteId(note_id_str)
    assert note_id.date == datetime.date(2023, 4, 14)
