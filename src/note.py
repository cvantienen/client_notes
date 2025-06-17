import re
import colorlog

NOTE_PATTERN = (
    r"- Started: (\d{4}-\d{2}-\d{2})\n"
    r"\s+Updated: (\d{4}-\d{2}-\d{2})\n"
    r"\s+Action: (.+?)\n"
    r"\s+Summary: (.+?)"
    r"\n\s+Status: (.+?)"           # Status is required and always last
    r"(?=\n\n- Started:|\Z)"
)

NOTE_SECTIONS = {
    "In Progress": r"## \*In Progress\*\s*(.*?)(?=\n\s*----|\n----|----|$)",
    "Que": r"## \*Que\*\s*(.*?)(?=\n\s*----|\n----|----|$)",
    "Archive": r"## \*Archive\*\s*(.*?)(?=\n\s*----|\n----|----|$)"
}

logger = colorlog.getLogger(__name__)


class Note:
    """
    Represents a client note with details about the action taken, summary, and status.
    Attributes:
        started (str): The date when the note was started.
        updated (str): The date when the note was last updated.
        action (str): The action taken or to be taken.
        summary (str): A summary of the note.
        status (str): The current status of the note.
    """

    def __init__(self, started, updated, action, summary, status=None):
        self.started = started
        self.updated = updated
        self.action = action
        self.summary = summary
        self.status = status


    def to_markdown(self):
        md = (
            "```code\n"
            f"{self.action}\n"
            f"{self.summary}\n"
            f"Started On: {self.started}\n"
            f"Last Updated: {self.updated}\n"
            f"Status: {self.status}\n"
            "\n```\n"
        )
        return md
    
    def to_display(self):
        """Format the note for console display."""
        return f"{self.action}:{self.status}"


def parse_client_notes(note_section_content:str) -> list[Note]:
    """
    Parse client notes from markdown text and return Note objects.

    - Each note starts with '- Started:' and ends with 'Status:'.
    - Captures started, updated, action, summary, and status.
    - Uses regex with lookahead to separate notes.
    
    Args:
        note_section_content (str): The content of the section to parse.
    Returns:
        list[Note]: A list of Note objects parsed from the section content.
    """
    if not note_section_content:
        return []
    matches = re.findall(NOTE_PATTERN, note_section_content, re.DOTALL)
    notes = []
    for started, updated, action, summary, status in matches:
        notes.append(Note(started, updated, action, summary, status))
    return notes

def extract_note_section(content:str, section_name:str) -> str:
    """Extract content from a specific section of the markdown file."""
    pattern = NOTE_SECTIONS.get(section_name)
    if not pattern:
        return None
    match = re.search(pattern, content, re.DOTALL)
    if match:
        note_section_content = match.group(1).strip()
        if note_section_content:
            return note_section_content  
    return None


def get_active_mods(content:str, client_name:str) -> list[dict]:
    """Extract active modifications for a client from the markdown content.
    Args:
        content (str): The markdown content of the client file.
        client_name (str): The name of the client.
    Returns:
        list[dict]: A list of dictionaries containing active modifications for the client.
    """
    active_mod_list = []

    # Extract in progress
    in_progress_content = extract_note_section(content, "In Progress")
    # Extract que sections
    que_content = extract_note_section(content, "Que")

    # Parse the detailed notes from each section
    in_progress_notes = parse_client_notes(in_progress_content)
    que_notes = parse_client_notes(que_content)
    
    # Only include clients with active items
    if in_progress_notes or que_notes:
        active_mod_list.append({
            'name': client_name,
            'in_progress': in_progress_notes,
            'que': que_notes
        })
    return active_mod_list