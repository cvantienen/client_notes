import os
import re
import inquirer
import logging
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

CLIENT_DIR = "/mnt/g/clients/client_notes/docs/clients"

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger(__name__)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("logs/note_taker.log"),
        logging.StreamHandler()
    ]
)

def get_client_list():
    """Get a list of all client files in the directory."""
    clients = []
    for filename in sorted(os.listdir(CLIENT_DIR)):
        if filename.endswith(".md"):
            client_id = filename[:-3]  # Remove .md extension
            client_name = client_id.replace("_", " ").replace("  ", " & ")
            clients.append((client_id, client_name))
    return clients


def select_client(clients):
    """Let user select a client with autocomplete support."""
    # Create a dictionary mapping client names to their IDs
    client_dict = {name: client_id for client_id, name in clients}

    # Create a fuzzy word completer with all client names
    client_completer = FuzzyWordCompleter(list(client_dict.keys()))

    logger.info("Start typing to search for a client (Tab for completion, Enter to select):")
    try:
        # Use prompt_toolkit's prompt with autocomplete
        client_name = prompt("Client: ", completer=client_completer)

        # Verify the selected client exists
        # and get current notes
        if client_name in client_dict:
            current_note_file = os.path.join(CLIENT_DIR, f"{client_dict[client_name]}.md")
            if os.path.exists(current_note_file):
                with open(current_note_file, "r") as f:
                    current_notes = f.read()
                    if not current_notes.strip():
                        logger.warning(f"Client file '{current_note_file}' is empty.")

                return (client_dict[client_name], client_name)
        else:
            logger.warning(f"Client '{client_name}' not found. Please try again.")
            return select_client(clients)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return None


def get_client_mods(note_file):
    """Get a list of all modifications for a specific client note."""
    mods = []
    with open(note_file, "r") as f:
        content = f.read()
        
        # Find all detailed notes using regex
        pattern = r"- Started: (\d{4}-\d{2}-\d{2})\n\s+Updated: (\d{4}-\d{2}-\d{2})\n\s+Action: (.+?)\n\s+Summary: (.+?)(?=\n\n- Started:|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        for started, updated, action, summary in matches:
            mods.append({
                'started': started,
                'updated': updated,
                'action': action.strip(),
                'summary': summary.strip()
            })
    return mods


def select_section():
    """Let user select which section to add the note to using a dropdown."""
    questions = [
        inquirer.List(
            "section",
            message="Select a section",
            choices=[
                ("In Progress", "In Progress"),
                ("Que", "Que"),
                ("Archive", "Archive"),
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    return answers["section"] if answers else None


def get_mod_action():
    """Get the action type from the user."""
    questions = [
        inquirer.List(
            "action",
            message="Select an action type",
            choices=[
                ("EPA", "Epa"),
                ("Add Sin", "Add Sin"),
                ("Add", "Add"),
                ("Delete", "Delete"),
                ("Sale", "Sale"),
                ("Terms", "Terms"),
                ("Description", "Description"),
                ("Photo", "Photo"),
                ("Other", "Other"),
            ],
        )
    ]
    answers = inquirer.prompt(questions)
    
    if answers and answers["action"] == "Other":
        custom_action = input("Enter custom action type: ")
        return custom_action
        
    return answers["action"] if answers else "Note"


def get_user_content():
    """Get the note content from the user."""
    logger.info("\nEnter note content (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line and (not lines or not lines[-1]):
            break
        lines.append(line)
    return "\n".join(lines)


def add_note_to_file(client_id, section, action, summary):
    """Add the note to the appropriate section in the client file."""
    file_path = os.path.join(CLIENT_DIR, f"{client_id}.md")

    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()

    # Format the note with timestamps
    timestamp = datetime.now().strftime("%Y-%m-%d")
    formatted_note = f"- Started: {timestamp}\n  Updated: {timestamp}\n  Action: {action}\n  Summary: {summary}"

    # Find the section and add the note after it
    section_pattern = f"## \\*{section}\\*"
    section_match = re.search(section_pattern, content)

    if section_match:
        # Find the position to insert the note (after the section heading)
        pos = section_match.end()

        # Insert the note after the section heading
        new_content = content[:pos] + "\n\n" + formatted_note + content[pos:]

        # Write the updated content back to the file
        with open(file_path, "w") as f:
            f.write(new_content)

        return True

    return False


def update_existing_note(file_path, mods):
    """Update an existing note in the client file."""
    if not mods:
        return False

    # Let user select which note to update
    choices = []
    for i, note in enumerate(mods):
        summary_preview = note["summary"][:40] + "..." if len(note["summary"]) > 40 else note["summary"]
        choices.append((f"[{note['started']}] {note['action']}: {summary_preview}", i))
        
    questions = [
        inquirer.List(
            "note_index",
            message="Select a note to update",
            choices=choices,
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return False

    note_index = answers["note_index"]
    note = mods[note_index]

    logger.info(f"\nCurrent note:")
    logger.info(f"Started: {note['started']}")
    logger.info(f"Updated: {note['updated']}")
    logger.info(f"Action: {note['action']}")
    logger.info(f"Summary: {note['summary']}")
    
    # Choose what to update
    update_questions = [
        inquirer.Checkbox(
            "fields",
            message="What would you like to update?",
            choices=[
                ("Action", "action"),
                ("Summary", "summary"),
            ],
        )
    ]
    update_answers = inquirer.prompt(update_questions)
    if not update_answers or not update_answers["fields"]:
        logger.warning("No fields selected for update. Operation cancelled.")
        return False
        
    # Get updated values
    updated_note = note.copy()
    
    if "action" in update_answers["fields"]:
        updated_note["action"] = get_mod_action()
        
    if "summary" in update_answers["fields"]:
        logger.info("\nEnter the updated summary (press Enter twice to finish):")
        updated_note["summary"] = get_user_content()
        
    if updated_note["summary"] == note["summary"] and updated_note["action"] == note["action"]:
        logger.warning("No changes made. Update cancelled.")
        return False
        
    # Update the timestamp
    updated_note["updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()
    
    # Format the old note to find and remove it
    if note.get("_legacy", False):
        old_entry = f"- {note['started']}: {note['summary']}"
    else:
        old_entry = f"- Started: {note['started']}\n  Updated: {note['updated']}\n  Action: {note['action']}\n  Summary: {note['summary']}"
    
    # Format the new note
    new_entry = f"- Started: {updated_note['started']}\n  Updated: {updated_note['updated']}\n  Action: {updated_note['action']}\n  Summary: {updated_note['summary']}"
    
    # Use regex for more precise matching with proper handling of surrounding whitespace
    pattern = f"(\n\n)?{re.escape(old_entry)}(\n\n)?"
    
    # Replace the old note with the new one
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"\n\n{new_entry}\n\n", content, count=1)
        
        # Clean up excessive newlines
        new_content = re.sub(r'\n{3,}', '\n\n', new_content)
        
        # Write the updated content back to the file
        with open(file_path, "w") as f:
            f.write(new_content)
            
        return True
        
    logger.error("Could not find the original note in the file. This might be due to a format mismatch.")
    return False


def archive_note(client_id, mods):
    """Move a note to the Archive section in the client file."""
    note_file_path = os.path.join(CLIENT_DIR, f"{client_id}.md")
    
    # Let user select which note to archive
    choices = []
    for i, note in enumerate(mods):
        summary_preview = note["summary"][:40] + "..." if len(note["summary"]) > 40 else note["summary"]
        choices.append((f"[{note['updated']}] {note['action']}: {summary_preview}", i))
        
    questions = [
        inquirer.List(
            "note_index",
            message="Select a note to archive",
            choices=choices,
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return False

    note_index = answers["note_index"]
    note = mods[note_index]

    # Format the note to find and remove it
    entry_to_remove = f"- Started: {note['started']}\n  Updated: {note['updated']}\n  Action: {note['action']}\n  Summary: {note['summary']}"
    
    # Format the new note for archive with updated timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    formatted_note = f"- Started: {note['started']}\n  Updated: {timestamp}\n  Action: {note['action']}\n  Summary: {note['summary']}"

    # Read the file as lines for better handling
    with open(note_file_path, "r") as f:
        lines = f.read().split('\n')
    
    # Find and remove the note
    entry_lines = entry_to_remove.split('\n')
    new_lines = []
    i = 0
    found = False
    
    while i < len(lines):
        if i+len(entry_lines)-1 < len(lines) and lines[i] == entry_lines[0]:
            # Check if this is our note
            match = True
            for j in range(1, len(entry_lines)):
                if i+j >= len(lines) or lines[i+j] != entry_lines[j]:
                    match = False
                    break
            
            if match:
                # Skip these lines (the note we're removing)
                i += len(entry_lines)
                found = True
                continue
        
        new_lines.append(lines[i])
        i += 1
    
    # Find the Archive section
    archive_index = -1
    for i, line in enumerate(new_lines):
        if line.strip() == "## *Archive*":
            archive_index = i
            break
    
    if archive_index != -1 and found:
        # Insert the note after the Archive heading
        archive_note_lines = formatted_note.split('\n')
        new_lines = new_lines[:archive_index+1] + [''] + archive_note_lines + [''] + new_lines[archive_index+1:]
        
        # Write the updated content back to the file
        with open(note_file_path, "w") as f:
            f.write('\n'.join(new_lines))
        
        return True
    
    return False


def remove_note_from_file(client_id, mods):
    """Remove a note from the client file."""
    note_file_path = os.path.join(CLIENT_DIR, f"{client_id}.md")
    
    # Let user select which note to delete
    choices = []
    for i, note in enumerate(mods):
        summary_preview = note["summary"][:40] + "..." if len(note["summary"]) > 40 else note["summary"]
        choices.append((f"[{note['updated']}] {note['action']}: {summary_preview}", i))
        
    questions = [
        inquirer.List(
            "note_index",
            message="Select a note to delete",
            choices=choices,
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return False

    note_index = answers["note_index"]
    note = mods[note_index]

    # Format the note to find and remove it
    entry_to_remove = f"- Started: {note['started']}\n  Updated: {note['updated']}\n  Action: {note['action']}\n  Summary: {note['summary']}"
    
    # Read the file as lines for better handling
    with open(note_file_path, "r") as f:
        lines = f.read().split('\n')
    
    # Find and remove the note
    entry_lines = entry_to_remove.split('\n')
    new_lines = []
    i = 0
    found = False
    
    while i < len(lines):
        if i+len(entry_lines)-1 < len(lines) and lines[i] == entry_lines[0]:
            # Check if this is our note
            match = True
            for j in range(1, len(entry_lines)):
                if i+j >= len(lines) or lines[i+j] != entry_lines[j]:
                    match = False
                    break
            
            if match:
                # Skip these lines (the note we're removing)
                i += len(entry_lines)
                found = True
                continue
        
        new_lines.append(lines[i])
        i += 1
    
    if found:
        # Clean up consecutive empty lines
        clean_lines = []
        prev_empty = False
        for line in new_lines:
            if not line.strip():
                if not prev_empty:
                    clean_lines.append(line)
                prev_empty = True
            else:
                clean_lines.append(line)
                prev_empty = False
        
        # Write the updated content back to the file
        with open(note_file_path, "w") as f:
            f.write('\n'.join(clean_lines))
        
        logger.info(f"Note '{note['summary'][:40]}...' removed successfully.")
        return True
    
    logger.error("Could not find the note to delete.")
    return False

def main():
    # Main function to run the client notes manager
    clients = get_client_list()
    if not clients:
        logger.error("No client files found!")
        return
    logger.info("\n=== Client Notes Manager ===\n")

    while True:
        selected = select_client(clients)
        if not selected:
            logger.info("Exiting program.")
            break
        
        # selected client and note file
        client_id, client_name = selected
        logger.info(f"\nSelected: {client_name}")
        current_note_file = os.path.join(CLIENT_DIR, f"{client_id}.md")
        
        if not os.path.exists(current_note_file):
            logger.error(f"Client file '{current_note_file}' does not exist.")
            continue

        with open(current_note_file, "r") as f:
            content = f.read()
            if not content.strip():
                logger.warning(f"Client file '{current_note_file}' is empty.")

        # Get and display client modifications
        mods = get_client_mods(current_note_file)
        if mods:
            logger.info("\nExisting notes:")
            for i, note in enumerate(mods, 1):
                logger.info(f"{i}. [{note['updated']}] {note['action']}: {note['summary'][:50]}...")

        # Ask whether to add a new note or update an existing one
        questions = [
            inquirer.List(
                "action",
                message="What would you like to do?",
                choices=[
                    ("Add a new note", "add"),
                    ("Update an existing note", "update"),
                    ("Delete an existing note", "delete"),
                    ("Archive an existing note", "archive"),
                    ("Go back", "back"),
                ],
            )
        ]
        action = inquirer.prompt(questions)["action"]

        # Handle user action
        if action == "back":
            continue
        elif action == "add":
            # Get section to add note to
            section = select_section()
            if not section:
                logger.info("Operation canceled.")
                continue

            # Get action type
            action_type = get_mod_action()
            
            # Get note content
            summary = get_user_content()

            if summary:
                success = add_note_to_file(client_id, section, action_type, summary)
                if success:
                    logger.info(f"\nNote added successfully for {client_name}!")
                else:
                    logger.error(f"\nFailed to add note. Section '{section}' not found in the file.")
            else:
                logger.warning("\nNo note content provided. Note was not added.")
                
        elif action == "update":
            if not mods:
                logger.warning("No existing notes to update.")
                continue

            success = update_existing_note(current_note_file, mods)
            if success:
                logger.info("\nNote updated successfully!")
            else:
                logger.error("\nFailed to update note.")
        
        elif action == "delete":
            if not mods:
                logger.error("No existing notes to delete.")
                continue

            success = remove_note_from_file(client_id, mods)
            if success:
                logger.info("\nNote deleted successfully!")
            else:
                logger.error("\nFailed to delete note.")
           
        elif action == "archive":
            if not mods:
                logger.error("No existing notes to archive.")
                continue

            success = archive_note(client_id, mods)
            if success:
                logger.info("\nNote archived successfully!")
            else:
                logger.error("\nFailed to archive note.")

if __name__ == "__main__":
    main()