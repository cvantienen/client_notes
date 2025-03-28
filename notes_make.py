import os
import re

"""
This script processes a README.md file to:
1. Create individual markdown files for each client listed in the file.
2. Generate a structured template for each client, including sections for project overview, meeting notes, and action items.
3. Update the README.md file to include links to these individual client files.
4. Update the mkdocs.yml file to include navigation entries for all clients.
"""

# Define paths
readme_file = "/home/gsacs/client_notes/docs/README.md"
output_dir = "/home/gsacs/client_notes/docs/clients"
mkdocs_file = "/home/gsacs/client_notes/mkdocs.yml"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to normalize client names for filenames
def normalize_name(name):
    """Normalize client names for filenames by replacing spaces with underscores and removing special characters."""
    return re.sub(r'[^a-zA-Z0-9_]', '', name.replace(" ", "_"))

# Read the README.md file
with open(readme_file, "r") as f:
    lines = f.readlines()

# Process each client name and create links
updated_readme_lines = []
client_files = []  # To store client file paths for updating mkdocs.yml

for line in lines:
    if line.startswith("### "):  # Identify client names
        client_name = line.strip("### ").strip()
        normalized_name = normalize_name(client_name)
        client_file = f"clients/{normalized_name}.md"
        client_path = os.path.join(output_dir, f"{normalized_name}.md")
        
        # Create a .md file for the client if it doesn't exist
        if not os.path.exists(client_path):
            with open(client_path, "w") as client_file_obj:
                client_file_obj.write(f"# {client_name}\n\n")
                client_file_obj.write("## Overview\n\n")
                client_file_obj.write("Status Overview\n\n")
                client_file_obj.write("## Mods\n\n")
                client_file_obj.write("### **Mod**\n")
                client_file_obj.write("- **Date**: \n")
                client_file_obj.write("- **Summary**: \n\n")
        
        # Add the client file to the list for mkdocs.yml
        client_files.append((client_name, client_file))
        
        # Replace the client name with a link in the README.md
        updated_readme_lines.append(f"### - [{client_name}]({client_file})\n -------------------\n")
    else:
        updated_readme_lines.append(line)

# Write the updated README.md file
with open(readme_file, "w") as f:
    f.writelines(updated_readme_lines)

print(f"Client notes files created in {output_dir} and README.md updated.")

# Update mkdocs.yml with navigation entries for all clients
with open(mkdocs_file, "r") as f:
    mkdocs_lines = f.readlines()

# Find the "nav:" section in mkdocs.yml
nav_start = next((i for i, line in enumerate(mkdocs_lines) if line.strip() == "nav:"), None)
if nav_start is None:
    raise ValueError("The 'nav:' section was not found in mkdocs.yml.")

# Insert the client nav entries under a "Clients" section
client_nav_entries = ["  - Clients:\n"]
for client_name, client_file in client_files:
    client_nav_entries.append(f"      - {client_name}: {client_file}\n")

# Add the client nav entries after the "nav:" line
mkdocs_lines = mkdocs_lines[:nav_start + 1] + client_nav_entries + mkdocs_lines[nav_start + 1:]

# Write the updated mkdocs.yml file
with open(mkdocs_file, "w") as f:
    f.writelines(mkdocs_lines)

print(f"Navigation for {len(client_files)} clients added to {mkdocs_file}.")