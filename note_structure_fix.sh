#!/bin/bash
# filepath: g:\clients\client_notes\add_archive_section.sh

# Set the client directory path
CLIENT_DIR="/mnt/g/clients/client_notes/docs/clients"

# Initialize counter for updated files
updated_count=0

# Check if the directory exists
if [ ! -d "$CLIENT_DIR" ]; then
    echo "Error: Directory $CLIENT_DIR does not exist."
    exit 1
fi

# Loop through all markdown files in the directory
for file in "$CLIENT_DIR"/*.md; do
    # Check if the file exists and is a regular file
    if [ -f "$file" ]; then
        # Check if Archive section already exists
        if ! grep -q "## \*Archive\*" "$file"; then
            # Archive section doesn't exist, add it
            echo -e "## *Archive*\n\n-----------------------------------\n" >> "$file"
            
            echo "Added Archive section to: $(basename "$file")"
            ((updated_count++))
        fi
    fi
done

# Print summary
echo -e "\nDone! Added Archive section to $updated_count client files."