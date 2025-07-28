#!/bin/bash

# Set root directory (defaults to current directory)
ROOT_DIR="${1:-.}"

# Define archive folder and zip file
ARCHIVE_DIR="$ROOT_DIR/Archived_Images"
ZIP_FILE="$ROOT_DIR/Archived_Images.zip"

# Create archive folder if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

# Find and process all JPEG and PNG files
find "$ROOT_DIR" -type f \( -iname "*.jpg" -o -iname "*.webp" -o -iname "*.png" \) | while read -r file; do
  dir=$(dirname "$file")
  base=$(basename "$file")
  name="${base%.*}"
  output="$dir/$name.webp"

  # Skip if WebP already exists
  if [[ -f "$output" ]]; then
    echo "⏭️  Skipping (already converted): $output"
    continue
  fi

  # Convert to WebP
  echo "🔄 Converting: $file → $output"
  cwebp "$file" -o "$output" >/dev/null 2>&1

  # Move original file to archive folder
  echo "📦 Archiving: $file"
  mv "$file" "$ARCHIVE_DIR/"
done

# Zip the archive folder (create or update)
if [[ -f "$ZIP_FILE" ]]; then
  echo "📦 Updating existing zip archive..."
  cd "$ARCHIVE_DIR" && zip -ru "$ZIP_FILE" . >/dev/null
else
  echo "📦 Creating new zip archive..."
  zip -r "$ZIP_FILE" "$ARCHIVE_DIR" >/dev/null
fi

echo "✅ Done! PNGs and JPEGs converted, archived, and zipped."

