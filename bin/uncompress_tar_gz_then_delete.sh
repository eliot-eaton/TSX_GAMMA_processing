#!/bin/bash

# Create the dims directory if it doesn't exist
mkdir -p dims

# Loop through each tar.gz file in the current directory
for tar_file in ./*.tar.gz; do
  # If no files match, the glob stays literal
  [ -e "$tar_file" ] || { echo "No tar.gz files found."; break; }

  echo "Extracting $tar_file into dims/..."

  # Extract into dims directory
  if tar -xzf "$tar_file" -C dims; then
    rm "$tar_file"
    echo "Deleted $tar_file"
  else
    echo "Failed to extract $tar_file — not deleting."
  fi
done

echo "Done."
