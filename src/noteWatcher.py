import time
import os
import logging

from note import get_active_mods

CLIENT_DIR = "/mnt/g/clients/client_notes/docs/clients"
MOD_FILE = "/mnt/g/clients/client_notes/docs/index.md"


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def format_notes_for_md(notes:list):
    """Format Note objects for display in the markdown files."""
    if not notes:
        return ""
    return "\n\n".join(note.to_markdown() for note in notes)

def format_notes_for_display(notes:list):
    """Format parsed notes for display in the console."""
    if not notes:
        return ""
    return "".join(note.to_display() for note in notes)
    

def get_all_active_mods():
    """Process all client files and extract their progress data."""
    all_client_mods = []
    # Get all client files in the directory
    for filename in sorted(os.listdir(CLIENT_DIR)):
        if not filename.endswith('.md'):
            continue
        
        # Get Client Name    
        client_id = filename[:-3]  # Remove .md extension
        client_name = client_id.replace('_', ' ').replace('  ', ' & ')
        file_path = os.path.join(CLIENT_DIR, filename)
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
            client_mods = get_active_mods(content, client_name)
            all_client_mods.extend(client_mods)
            
    return all_client_mods


def generate_mod_md(client_notes):
    """Generate a master markdown file with all client mods."""
    with open(MOD_FILE, 'w') as f:
        # Write header
        f.write(f"# Modifications in Progress\n\n")
        
        # Write client sections
        for client in client_notes:
            f.write(f"### {client['name']}\n")

            if client['in_progress']:
                note = (client)
                f.write(f"{format_notes_for_md(client['in_progress'])}\n")
            if client['que']:
                f.write(f"{format_notes_for_md(client['que'])}\n")

            f.write("---\n")

def display_mods_to_console(client_notes):
    """Log the generated markdown file."""
        # Log information about what was found
    for client in client_notes:
        logger.info(f"\n{client['name']}")
        
        if client['in_progress']:
            for note in client['in_progress']:
                logger.info(f"{format_notes_for_display([note])}")

        if client['que']:
            for note in client['que']:
                logger.info(f"{format_notes_for_display([note])}")
                

def main():
    logger.info("Generating mods status list...")
    # Get data from all client files
    all_client_mods = get_all_active_mods()
    if not all_client_mods:
        logger.warning("No active tasks found in any client files.")
        return
    # Generate the master list
    generate_mod_md(all_client_mods)
    # Display the modifications in the console
    display_mods_to_console(all_client_mods)
    
    logger.info(f"Active client tasks found: {len(all_client_mods)}")

if __name__ == "__main__":
    while True:
        try:
            main()
            sleep_time = 60 * 1  # 1 minute
            time.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            break
