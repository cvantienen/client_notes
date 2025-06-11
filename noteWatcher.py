import time
import os
import logging
import re
from datetime import datetime

CLIENT_DIR = "/mnt/g/clients/client_notes/docs/clients"
MOD_FILE = "/mnt/g/clients/client_notes/docs/mods.md"


# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("logs/note_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_section_content(content, section_name):
    """Extract content from a specific section of the markdown file."""
    pattern = f"## \\*{section_name}\\*\n\n(.*?)(?=\n----|----|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_content = match.group(1).strip()
        if section_content:
            return section_content
    return None

def parse_client_notes(section_content):
    """Parse the client note structure and return formatted notes."""
    if not section_content:
        return []
    
    # Pattern to match detailed notes
    pattern = r"- Started: (\d{4}-\d{2}-\d{2})\n\s+Updated: (\d{4}-\d{2}-\d{2})\n\s+Action: (.*?)\n\s+Summary: (.*?)(?=\n\n- Started:|\Z)"
    matches = re.findall(pattern, section_content, re.DOTALL)
    
    parsed_notes = []
    for started, updated, action, summary in matches:
        parsed_notes.append({
            'started': started,
            'updated': updated,
            'action': action.strip(),
            'summary': summary.strip()
        })
    
    return parsed_notes

def get_active_mods():
    """Process all client files and extract their progress data."""
    clients_data = []
    
    for filename in sorted(os.listdir(CLIENT_DIR)):
        if not filename.endswith('.md'):
            continue
            
        client_id = filename[:-3]  # Remove .md extension
        client_name = client_id.replace('_', ' ').replace('  ', ' & ')
        file_path = os.path.join(CLIENT_DIR, filename)
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract sections
        in_progress_content = extract_section_content(content, "In Progress")
        que_content = extract_section_content(content, "Que")
        
        # Parse the detailed notes from each section
        in_progress_notes = parse_client_notes(in_progress_content)
        que_notes = parse_client_notes(que_content)
        
        # Only include clients with active items
        if in_progress_notes or que_notes:
            clients_data.append({
                'name': client_name,
                'in_progress': in_progress_notes,
                'que': que_notes
            })
    
    return clients_data

def format_notes_for_md(notes):
    """Format parsed notes for display in the markdown files."""
    if not notes:
        return ""
    
    formatted = []
    for note in notes:
        formatted.append(f"- **[{note['updated']}]** {note['action']}\n  Summary: {note['summary']}")

    return "\n\n".join(formatted)

def format_notes_for_display(notes):
    """Format parsed notes for display in the console."""
    if not notes:
        return ""
    
    formatted = []
    for note in notes:
        summary_preview = note['summary'][:50] + "..." if len(note['summary']) > 50 else note['summary']
        formatted.append(f"[{note['updated']}] {note['action']} - {summary_preview}")

    return "\n".join(formatted)

def generate_mod_md(clients_data):
    """Generate a master markdown file with all client mods."""
    
    with open(MOD_FILE, 'w') as f:
        # Write header
        f.write(f"# Modifications in Progress\n\n")
        
        # Write client sections
        for client in clients_data:
            f.write(f"## {client['name']}\n")

            if client['in_progress']:
                f.write(f"### In Progress\n\n")
                f.write(f"{format_notes_for_md(client['in_progress'])}\n\n")
            
            if client['que']:
                f.write(f"### Queued\n\n")
                f.write(f"{format_notes_for_md(client['que'])}\n\n")
            
            f.write("---\n\n")


def main():
    logger.info("Generating mods status list...")
    # Get data from all client files
    clients_data = get_active_mods()
    if not clients_data:
        logger.warning("No active tasks found in any client files.")
        return
    
    # Generate the master list
    generate_mod_md(clients_data)
    
    # Log information about what was found
    for client in clients_data:
        logger.info(f"\n{client['name']}")
        
        if client['in_progress']:
            for note in client['in_progress']:
                logger.info(format_notes_for_display([note]))
        
        if client['que']:
            for note in client['que']:
                logger.info(format_notes_for_display([note]))

    logger.info(f"Found {len(clients_data)} clients with active tasks.")

if __name__ == "__main__":
    while True:
        try:
            main()
            sleep_time = 60 * 1  # 1 minute
            time.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            break