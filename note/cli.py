import click
import os
import sys
from note.note_manager import NoteManager
from pathlib import Path
import subprocess

pass_note_manager = click.make_pass_decorator(NoteManager)


@click.group()
@click.option("--personal", "note_dir_type", flag_value="personal", default=True)
@click.option("--work", "note_dir_type", flag_value="work")
@click.pass_context
def cli(ctx, note_dir_type):
    """Manage notes, stored as markdown files.

    Notes can optionally end with a set of tags at the end of the file.
    The final line should look as follows:

        tags: tag 1, tag 2, ...

    These tags can be used to search and index the notes"""
    if note_dir_type == "personal":
        note_dir = os.path.expanduser(os.environ.get("NOTES_DIR", "~/test-notes"))
    if note_dir_type == "work":
        note_dir = os.path.expanduser(os.environ.get("WORK_NOTES_DIR", "~/test-work_notes"))
    manager = NoteManager(Path(note_dir))
    ctx.obj = manager


@cli.command()
def update():
    """Installs `note` and its dependencies in an isolated env using `pipx`.

    NOTE: Requires `pipx` to be installed on the system prior to running
    """
    repo_dir = os.path.expanduser(os.environ.get("NOTE_REPO_DIR", "~/github/note"))
    cmd_str = "pipx install . --force"
    subprocess.run(cmd_str, shell=True, cwd=repo_dir)


@cli.command()
@click.option("--summary", "how_print", flag_value="summary", default=True)
@click.option("--plain", "how_print", flag_value="plain")
@click.option("--json", "how_print", flag_value="json")
@pass_note_manager
def list(manager, how_print):
    """List all notes from the given notes directory"""
    manager.print_notes(how=how_print)


@cli.command()
@pass_note_manager
def create(manager):
    """Create a new note with an auto-generated note ID"""
    manager.create_note()


@cli.command()
@click.argument("note_id", required=True)
@pass_note_manager
def edit(manager, note_id):
    """Edit an existing note, by ID

    Optionally, pass the special string "last" to edit the most recent note,
    by ID timestamp
    """
    if note_id == "last":
        note_id = manager.find_last_note_id()
    if not manager.is_valid_note_id(note_id):
        click.echo(f"Invalid note ID: {note_id}")
        sys.exit(1)
    manager.edit_note(note_id)


@cli.command()
@click.option(
    "--how-body",
    "how_body",
    default="fuzzy",
    show_default=True,
    type=click.Choice(["fuzzy", "exact"], case_sensitive=True),
)
@click.option(
    "--how-tags",
    "how_tags",
    default="fuzzy",
    show_default=True,
    type=click.Choice(["fuzzy", "exact"], case_sensitive=True),
)
@click.option("--summary", "how_print", flag_value="summary", default=True)
@click.option("--plain", "how_print", flag_value="plain")
@click.option("--json", "how_print", flag_value="json")
@click.argument("search_terms", required=True, nargs=-1)
@pass_note_manager
def search(manager, how_body, how_tags, how_print, search_terms):
    """Search note bodies and IDs with either fuzzy or exact search"""
    manager.print_search(search_terms, how_tags, how_body, how_print)


def main():
    cli()
