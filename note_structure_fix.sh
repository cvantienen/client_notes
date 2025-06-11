#!/bin/bash
# filepath: /mnt/g/clients/client_notes/note_structure_fix.sh

# Set the client directory path
CLIENT_DIR="/mnt/g/clients/client_notes/docs/clients"

# Initialize counters
updated_count=0
converted_notes=0
sections_removed=0

# Check if the directory exists
if [ ! -d "$CLIENT_DIR" ]; then
    echo "Error: Directory $CLIENT_DIR does not exist."
    exit 1
fi

# Function to ensure proper section structure
fix_file_structure() {
    local file="$1"
    local filename=$(basename "$file")
    local modified=false
    local content=$(cat "$file")
    
    # Extract client name from filename (remove extension and replace underscores with spaces)
    local client_name=$(echo "${filename%.md}" | sed 's/_/ /g' | sed 's/  / \& /g')
    
    # Check if the file has a proper header with the client name
    if ! grep -q "^# " "$file"; then
        # Add client name header if missing
        content="# ${client_name}\n--------------------\n${content}"
        modified=true
        echo "Added header to: $filename"
    fi
    
    # Check for required sections and add them if missing
    sections=("In Progress" "Que" "Archive")
    
    for section in "${sections[@]}"; do
        if ! echo "$content" | grep -q "## \*${section}\*"; then
            # Section doesn't exist, add it
            if [ "$section" == "Archive" ]; then
                # Add separator before Archive section
                content="${content}\n-----------------------------------\n## *${section}*\n\n"
            else
                content="${content}\n\n## *${section}*\n\n"
            fi
            modified=true
            echo "Added $section section to: $filename"
        fi
    done
    
    # Write back to file if modified
    if [ "$modified" = true ]; then
        echo -e "$content" > "$file"
        ((updated_count++))
    fi
    
    return 0
}

# Function to remove the Update section
remove_update_section() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Check if the file has an Update section
    if grep -q "## \*Update\*" "$file"; then
        # Use sed to remove the Update section and its content up to the next section
        # This pattern matches from "## *Update*" to the next section header or end of file
        sed -i '/## \*Update\*/,/## \*[A-Za-z]\+\*\|$/{/## \*[A-Za-z]\+\*\|$/!d}' "$file"
        # Remove the Update section header itself
        sed -i '/## \*Update\*/d' "$file"
        
        ((sections_removed++))
        echo "Removed Update section from: $filename"
        
        # Clean up any excessive blank lines (more than 2 consecutive)
        sed -i '/^$/N;/^\n$/N;/^\n\n$/d' "$file"
    fi
    
    return 0
}

# Function to convert simple notes to detailed format
convert_notes_to_detailed() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Look for simple notes pattern (- YYYY-MM-DD: text)
    if grep -q "^- [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}: " "$file"; then
        # Use sed to convert each simple note to detailed format
        sed -i -E 's/- ([0-9]{4}-[0-9]{2}-[0-9]{2}): (.*)/- Started: \1\n  Updated: \1\n  Action: Note\n  Summary: \2/g' "$file"
        
        ((converted_notes++))
        echo "Converted notes in: $filename"
    fi
    
    return 0
}

# Process all markdown files
echo "Starting structure fix for client note files..."
for file in "$CLIENT_DIR"/*.md; do
    # Check if the file exists and is a regular file
    if [ -f "$file" ]; then
        echo "Processing: $(basename "$file")..."
        
        # Remove Update section
        remove_update_section "$file"
        
        # Fix overall file structure
        fix_file_structure "$file"
        
        # Convert simple notes to detailed format
        convert_notes_to_detailed "$file"
    fi
done

# Print summary
echo -e "\nDone! Updated $updated_count client files."
echo "Removed Update section from $sections_removed files."
echo "Converted $converted_notes files with simple notes to detailed format."
echo -e "\nNew note structure format:"
echo "- Started: YYYY-MM-DD"
echo "  Updated: YYYY-MM-DD"
echo "  Action: Note"
echo "  Summary: Your detailed note text"