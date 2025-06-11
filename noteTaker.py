import os
import re
import inquirer
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

CLIENT_DIR = "/mnt/g/clients/client_notes/docs/clients"


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

    print("Start typing to search for a client (Tab for completion, Enter to select):")
    try:
        # Use prompt_toolkit's prompt with autocomplete
        client_name = prompt("Client: ", completer=client_completer)

        # Verify the selected client exists
        # and print current notes
        if client_name in client_dict:
            current_file = os.path.join(CLIENT_DIR, f"{client_dict[client_name]}.md")
            if os.path.exists(current_file):
                with open(current_file, "r") as f:
                    current_notes = f.read()
                    if not current_notes.strip():
                        print(f"Client file '{current_file}' is empty.")
                    return (client_dict[client_name], client_name)
                return (client_dict[client_name], client_name)
        else:
            print(f"Client '{client_name}' not found. Please try again.")
            return select_client(clients)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return None


def get_client_mods(note):
    """Get a list of all modifications for a specific client note."""
    mods = []
    with open(note, "r") as f:
        content = f.read()
        # Find all modifications using regex
        matches = re.findall(r"- (\d{4}-\d{2}-\d{2}): (.+)", content)
        for date, mod in matches:
            mods.append((date, mod))
    return mods


def update_existing_note(file_path, mods):
    """Update an existing note in the client file."""
    if not mods:
        return False

    # Let user select which note to update
    questions = [
        inquirer.List(
            "note_index",
            message="Select a note to update",
            choices=[
                (f"[{date}] {note[:50]}{'...' if len(note) > 50 else ''}", i)
                for i, (date, note) in enumerate(mods)
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return False

    note_index = answers["note_index"]
    date, old_note = mods[note_index]

    print(f"\nCurrent note: {old_note}")
    print("\nEnter the updated note content (press Enter twice to finish):")

    lines = []
    while True:
        line = input()
        if not line and (not lines or not lines[-1]):
            break
        lines.append(line)

    new_note = "\n".join(lines)
    if not new_note:
        print("No content provided. Update cancelled.")
        return False

    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()

    # Replace the old note with the new one
    old_entry = f"- {date}: {old_note}"
    new_entry = f"- {date}: {new_note}"

    if old_entry in content:
        new_content = content.replace(old_entry, new_entry)

        # Write the updated content back to the file
        with open(file_path, "w") as f:
            f.write(new_content)

        return True

    return False


def select_section():
    """Let user select which section to add the note to using a dropdown."""
    questions = [
        inquirer.List(
            "section",
            message="Select a section",
            choices=[
                ("In Progress", "In Progress"),
                ("Que", "Que"),
                ("Update", "Update"),
                ("Archive", "Archive"),
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    return answers["section"] if answers else None


def get_note_content():
    """Get the note content from the user."""
    print("\nEnter note content (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line and (not lines or not lines[-1]):
            break
        lines.append(line)
    return "\n".join(lines)


def add_note_to_file(client_id, section, note):
    """Add the note to the appropriate section in the client file."""
    file_path = os.path.join(CLIENT_DIR, f"{client_id}.md")

    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()

    # Format the note with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    formatted_note = f"- {timestamp}: {note}"

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


def main():
    print("\n=== Client Notes Manager ===\n")

    clients = get_client_list()
    if not clients:
        print("No client files found!")
        return

    while True:
        selected = select_client(clients)

        if not selected:
            print("Exiting program.")
            break

        client_id, client_name = selected
        print(f"\nSelected: {client_name}")
        current_file = os.path.join(CLIENT_DIR, f"{client_id}.md")
        if not os.path.exists(current_file):
            print(f"Client file '{current_file}' does not exist.")
            continue

        with open(current_file, "r") as f:
            content = f.read()
            if not content.strip():
                print(f"Client file '{current_file}' is empty.")

        # Get and display client modifications
        mods = get_client_mods(current_file)
        if mods:
            print("\nExisting modifications:")
            for i, (date, note) in enumerate(mods, 1):
                print(f"{i}. [{date}] {note}")

        # Ask whether to add a new note or update an existing one
        questions = [
            inquirer.List(
                "action",
                message="What would you like to do?",
                choices=[
                    ("Add a new note", "add"),
                    ("Update an existing note", "update"),
                    ("Delete an existing note", "delete"),
                    ("Move note to Archive", "archive"),
                    ("Go back", "back"),
                ],
            )
        ]
        action = inquirer.prompt(questions)["action"]

        if action == "back":
            continue
        elif action == "add":
            # Existing flow for adding a new note
            section = select_section()
            if not section:
                print("Operation canceled.")
                continue

            note = get_note_content()

            if note:
                success = add_note_to_file(client_id, section, note)
                if success:
                    print(
                        f"\nNote added successfully to {client_name}'s {section} section!"
                    )
                else:
                    print(
                        f"\nFailed to add note. Section '{section}' not found in the file."
                    )
            else:
                print("\nNo note content provided. Note was not added.")
        elif action == "update":
            # New flow for updating an existing note
            if not mods:
                print("No existing notes to update.")
                continue

            success = update_existing_note(current_file, mods)
            if success:
                print("\nNote updated successfully!")
            else:
                print("\nFailed to update note.")


if __name__ == "__main__":
    main()
