import datetime
from functools import total_ordering


@total_ordering
class NoteId:
    NOTE_DATETIME_FORMAT = "%Y%m%d%H%M%S"

    @classmethod
    def generate_note_id(cls):
        return NoteId(datetime.datetime.now().strftime(cls.NOTE_DATETIME_FORMAT))

    @classmethod
    def is_valid_note_id(cls, string: str):
        try:
            datetime.datetime.strptime(string, cls.NOTE_DATETIME_FORMAT)
            return True
        except Exception:
            return False

    @classmethod
    def _parse_note_id(cls, string: str) -> datetime.datetime:
        if not cls.is_valid_note_id(string):
            raise ValueError(f"Invalid NoteID string: {string}")
        dt = datetime.datetime.strptime(string, cls.NOTE_DATETIME_FORMAT)
        return dt

    def __init__(self, id_str: str):
        self._id_str: str = id_str
        self._dt: datetime.datetime = self._parse_note_id(self._id_str)

    def __eq__(self, other):
        return self.dt == other.dt

    def __lt__(self, other):
        return self.dt < other.dt

    def __str__(self) -> str:
        return self._id_str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"

    def __hash__(self) -> int:
        return hash(self._id_str)

    @property
    def dt(self) -> datetime.datetime:
        return self._dt

    @property
    def date(self) -> datetime.date:
        return self.dt.date()
