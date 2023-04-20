import os
from note.note_manager import NoteManager
from unittest import mock
from unittest.mock import Mock
from click.testing import CliRunner
from note.cli import cli

def test_list_no_fail():
    runner = CliRunner()
    with runner.isolated_filesystem() as temp_dir:
        id = "20230405161655"
        temp_file = f"{temp_dir}/{id}/README.md"
        os.mkdir(os.path.dirname(temp_file))
        with open(temp_file, 'w') as f:
            f.write('Hello World!')
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0

def test_search_no_fail():
    runner = CliRunner()
    with runner.isolated_filesystem() as temp_dir:
        id = "20230405161655"
        temp_file = f"{temp_dir}/{id}/README.md"
        os.mkdir(os.path.dirname(temp_file))
        with open(temp_file, 'w') as f:
            f.write('Hello World!')
        result = runner.invoke(cli, ["search", "test_str"])
        assert result.exit_code == 0

def test_create_no_fail():
    runner = CliRunner()
    # Mock so that EDITOR process isn't spawned
    with mock.patch("subprocess.call"):
        with runner.isolated_filesystem() as temp_dir:
            id = "20230405161655"
            temp_file = f"{temp_dir}/{id}/README.md"
            os.mkdir(os.path.dirname(temp_file))
            with open(temp_file, 'w') as f:
                f.write('Hello World!')
            result = runner.invoke(cli, ["edit", id], env={"NOTES_DIR": temp_dir})
            assert result.exit_code == 0

def test_edit_no_fail():
    runner = CliRunner()
    # Mock so that EDITOR process isn't spawned
    with mock.patch("subprocess.call"):
        with runner.isolated_filesystem() as temp_dir:
            id = "20230405161655"
            temp_file = f"{temp_dir}/{id}/README.md"
            os.mkdir(os.path.dirname(temp_file))
            with open(temp_file, 'w') as f:
                f.write('Hello World!')
            result = runner.invoke(cli, ["edit", id], env={"NOTES_DIR": temp_dir})
            assert result.exit_code == 0

def test_edit_exit_with_invalid_noteid():
    runner = CliRunner()
    # Mock so that EDITOR process isn't spawned
    with mock.patch("subprocess.call"):
        with runner.isolated_filesystem() as temp_dir:
            id = "orgblorg"
            result = runner.invoke(cli, ["edit", id], env={"NOTES_DIR": temp_dir})
            assert result.exit_code == 1
