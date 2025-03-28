import os
import re

def find_readme_files(directory):
    readme_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            readme_files.append(os.path.join(root, file))
    return readme_files

def extract_mods_in_progress(readme_file):
    mods_in_progress = []
    with open(readme_file, 'r') as file:
        for line in file:
            if re.match(r'## \*Que\*', line, re.IGNORECASE):
                break
            if 'in progress' in line.lower():
                mods_in_progress.append(line.strip())
    return mods_in_progress

def create_summary_readme(mods_summary, output_file):
    with open(output_file, 'w') as file:
        file.write("# Modifications In Progress\n\n")
        for mod in mods_summary:
            file.write(f"- {mod}\n")

def main():
    repo_directory = '/home/gsacs/client_notes/docs/clients'  # Set this to the root directory of your repository
    output_file = '/home/gsacs/client_notes/docs/in_progress_mods.md'
    
    readme_files = find_readme_files(repo_directory)
    mods_summary = []
    
    for readme_file in readme_files:
        mods = extract_mods_in_progress(readme_file)
        mods_summary.extend(mods)
    
    create_summary_readme(mods_summary, output_file)
    print(f"Summary of modifications in progress has been created in {output_file}")

if __name__ == "__main__":
    main()
