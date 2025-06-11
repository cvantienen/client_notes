import time
import os
import re
from datetime import datetime

CLIENT_DIR = "/mnt/g/clients/client_notes/docs/clients"
MASTER_FILE = "/mnt/g/clients/client_notes/docs/mods.md"
DAILY_FILE = "/mnt/g/clients/client_notes/docs/daily.md"

def extract_section_content(content, section_name):
    """Extract content from a specific section of the markdown file."""
    pattern = f"## \\*{section_name}\\*\n\n(.*?)(?=\n----|----|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_content = match.group(1).strip()
        if section_content:
            return section_content
    return None

def get_client_data():
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
        in_progress = extract_section_content(content, "In Progress")
        que = extract_section_content(content, "Que")
        
        # Only include clients with active items
        if in_progress or que:
            clients_data.append({
                'name': client_name,
                'in_progress': in_progress,
                'que': que
            })
    
    return clients_data

def generate_master_list(clients_data):
    """Generate a master markdown file with all client progress data."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    with open(MASTER_FILE, 'w') as f:
        # Write header
        f.write(f"# Modifications in Progress\n\n")
        
        # Write client sections
        for client in clients_data:
            f.write(f"## {client['name']}\n")

            if client['in_progress']:
                f.write(f"### In Progress\n\n")
                f.write(f"{client['in_progress']}\n\n")
            
            if client['que']:
                f.write(f"### Queued\n\n")
                f.write(f"{client['que']}\n\n")
            
            f.write("---\n\n")

    with open(DAILY_FILE, 'w') as f:
        # Write client sections
        for client in clients_data:
            f.write(f"## {client['name']}\n")

            if client['in_progress']:
                f.write(f"### In Progress\n\n")
                f.write(f"{client['in_progress']}\n\n")
            
            if client['que']:
                f.write(f"### Queued\n\n")
                f.write(f"{client['que']}\n\n")

def main():
    print("Generating master progress list...")
    
    # Get data from all client files
    clients_data = get_client_data()
   
    if not clients_data:
        print("No active tasks found in any client files.")
        return
    
    # Generate the master list
    generate_master_list(clients_data)
    
    print(f"Master list generated successfully: {MASTER_FILE}")
    print(f"Found {len(clients_data)} clients with active tasks.")

if __name__ == "__main__":
    while True:
        try:
            print(f"Checking for updates....")
            main()
            sleep_time = 60 * 1  # 1 minutes
            time.sleep(sleep_time)
        except Exception as e:
            print(f"Error occurred: {e}")
            break
