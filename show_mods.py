import os
import re

def find_markdown_files(directory):
    """Recursively find all markdown files in the given directory."""
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def extract_mods_in_progress(file_path):
    """Extract modifications in progress from a markdown file."""
    mods_in_progress = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    client_name = None
    in_progress_section = False
    current_mod = {}

    for line in lines:
        client_match = re.match(r"^# \*\*(.*)\*\*$", line)
        if client_match:
            client_name = client_match.group(1).strip()

        if "## *In Progress*" in line:
            in_progress_section = True
            continue

        if "## *Que*" in line:
            in_progress_section = False
            continue

        if in_progress_section:
            mod_type_match = re.match(r"^### \*(.*)\*$", line)
            if mod_type_match:
                if current_mod:
                    mods_in_progress.append(current_mod)
                current_mod = {
                    "client": client_name,
                    "mod_type": mod_type_match.group(1).strip(),
                    "summary": "",
                    "date_received": "",
                    "submitted": "",
                    "status": ""
                }
            elif "Date Received:" in line:
                current_mod["date_received"] = line.split(":", 1)[-1].strip()
            elif "Summary:" in line:
                current_mod["summary"] = line.split(":", 1)[-1].strip()
            elif "Submitted:" in line:
                current_mod["submitted"] = line.split(":", 1)[-1].strip()
            elif "Status:" in line:
                current_mod["status"] = line.split(":", 1)[-1].strip()

    if current_mod:
        mods_in_progress.append(current_mod)

    return mods_in_progress

def log_mods_in_progress(directory, log_file='docs/mod_status.md'):
    """Log all modifications in progress from all markdown files in the directory."""
    markdown_files = find_markdown_files(directory)
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("# Modifications in Progress\n\n")

        for md_file in markdown_files:
            mods = extract_mods_in_progress(md_file)
            for mod in mods:
                log.write(f"## Client: {mod['client']}\n")
                log.write(f"### Modification Type: {mod['mod_type']}\n")
                log.write(f"- **Summary**: {mod['summary']}\n")
                log.write(f"- **Date Received**: {mod['date_received']}\n")
                log.write(f"- **Submitted**: {mod['submitted']}\n")
                log.write(f"- **Status**: {mod['status']}\n")
                log.write("\n---\n\n")

if __name__ == '__main__':
    client_directory = '/docs/clients'
    log_mods_in_progress(client_directory)
    print("Mod status has been logged in mod_status.md")
