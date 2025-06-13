#!/bin/bash

# Set the client directory path
CLIENT_DIR="/mnt/g/clients/client_notes/docs/clients"

# Initialize counters
updated_count=0

# Check if the directory exists
if [ ! -d "$CLIENT_DIR" ]; then
    echo "Error: Directory $CLIENT_DIR does not exist."
    exit 1
fi

# Function to fix header and section levels
fix_headers_and_sections() {
    local file="$1"
    local filename=$(basename "$file")
    local modified=false

    # Change client name header from # to ##
    # Only change if it starts with a single #
    if grep -q "^# [^#]" "$file"; then
        sed -i '1s/^# /## /' "$file"
        modified=true
        echo "Changed client name header to ## in: $filename"
    fi


    # Remove only the first line starting with ##
    sed -i '0,/^##/d' "$file" && modified=true

    # Write a message if modified
    if [ "$modified" = true ]; then
        ((updated_count++))
    fi
}

# Process all markdown files
echo "Starting header/section fix for client note files..."
for file in "$CLIENT_DIR"/*.md; do
    if [ -f "$file" ]; then
        echo "Processing: $(basename "$file")..."
        fix_headers_and_sections "$file"
    fi
done

# ...existing code...

echo -e "\nDone! Updated $updated_count client files."

: '
================================================================================
Script Explanation: How This Script Finds and Replaces Markdown Headers
================================================================================

This script is designed to standardize the header structure of client note markdown files. 
It performs two main operations on each file in the specified CLIENT_DIR:

1. **Client Name Header Update**
   - The script looks for a client name header at the very top of the file that starts with a single hash (`# `).
   - It uses `grep -q "^# [^#]" "$file"` to check if the first line starts with a single hash (and not multiple hashes).
   - If found, it uses `sed -i '1s/^# /## /' "$file"` to replace the single hash with two hashes (`##`), making it a level-2 markdown header.
   - This ensures all client names are consistently formatted as `## CLIENT NAME`.

2. **Section Header Update**
   - The script searches for section headers that start with exactly two hashes followed by an asterisk (e.g., `## *In Progress*`).
   - It uses `sed -i 's/^## \*/### \*/g' "$file"` to replace all such occurrences with three hashes (`###`), making them level-3 headers.
   - This is done globally for all lines in the file, ensuring all sections like *In Progress*, *Que*, and *Archive* are consistently formatted.

3. **Tracking Changes**
   - The script keeps a count of how many files were modified using the `updated_count` variable.
   - It prints a summary and an example of the new structure at the end.

--------------------------------------------------------------------------------
How to Create Scripts to Edit the Note Structure Further
--------------------------------------------------------------------------------

- **Identify Patterns:** Use `grep` or `sed` to search for specific patterns in your markdown files. For example, to find all headers, you might use `grep "^#"`.

- **Use sed for In-Place Editing:** 
  - `sed` is a powerful stream editor for filtering and transforming text.
  - To change a header, use: `sed -i 's/old_pattern/new_pattern/g' filename`
  - For example, to change all `### *Archive*` to `#### *Archive*`, use:
    `sed -i 's/^### \*Archive\*/#### \*Archive\*/g' filename`

- **Automate Over Multiple Files:** 
  - Use a `for` loop to process all files in a directory:
    ```bash
    for file in /path/to/dir/*.md; do
        # your sed/awk/grep commands here
    done
    ```

- **Test Your Script:** 
  - Always test your script on a backup or a small subset of files to ensure it works as expected.

- **Advanced Editing:** 
  - For more complex changes, consider using `awk` for multi-line or context-aware edits.
  - For example, to insert a line after every section header:
    ```bash
    awk '/^### \*/{print; print "New line here"; next} 1' file.md > tmp && mv tmp file.md
    ```

- **Version Control:** 
  - Always use version control (like git) so you can revert changes if something goes wrong.

This approach allows you to quickly and safely standardize and update the structure of many markdown files at once. You can adapt these techniques to add, remove, or modify any part of your note structure as your needs evolve.
'


