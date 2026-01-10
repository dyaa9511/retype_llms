#!/usr/bin/env bash
set -e

echo "🔍 Checking for Retype project..."

# Check Retype project
if [ ! -f "retype.yml" ]; then
  echo "❌ Not a Retype project (retype.yml not found)."
  exit 0
fi

# Use argument if passed
if [ -n "$1" ]; then
  INPUT_OVERRIDE="$1"
else
  INPUT_OVERRIDE=""
fi

# Detect input folder
if [ -n "$INPUT_OVERRIDE" ]; then
  INPUT_DIR="$INPUT_OVERRIDE"
else
  INPUT_DIR=$(grep '^input:' retype.yml | awk '{print $2}')
  if [ -z "$INPUT_DIR" ]; then
    INPUT_DIR="."
  fi
fi

if [ ! -d "$INPUT_DIR" ]; then
  echo "❌ Retype input directory '$INPUT_DIR' does not exist."
  exit 1
fi

# Detect base URL (optional)
BASE_URL=$(grep '^url:' retype.yml | awk '{print $2}')

STATIC_DIR="$INPUT_DIR/static"
OUTPUT="$STATIC_DIR/llms.txt"
mkdir -p "$STATIC_DIR"

echo "📁 Retype input directory: $INPUT_DIR"
echo "📚 Processing markdown files:"

# Collect markdown files (exclude README.md and static, node_modules, .git)
mapfile -t FILES < <(find "$INPUT_DIR" -type f -name "*.md" \
  ! -path "*/static/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  | sort)

COUNT=0
> "$OUTPUT"

# Add AI context note at the top
if [ -n "$BASE_URL" ]; then
  echo "# Note for AI:" >> "$OUTPUT"
  echo "- All images in markdown are relative to: $BASE_URL" >> "$OUTPUT"
  echo "- If a markdown image is like ![alt](path/to/image.png) or ![alt](/path/to/image.png), the absolute URL is $BASE_URL/path/to/image.png" >> "$OUTPUT"
  echo "----" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
fi

# Process each markdown file
for FILE in "${FILES[@]}"; do
  REL_PATH=$(realpath --relative-to="." "$FILE")
  echo "  → $REL_PATH"

  {
    echo "file: \"$REL_PATH\""
    awk '
      BEGIN { skip=0 }
      /^---$/ { skip = !skip; next }
      !skip { print }
    ' "$FILE"
  } >> "$OUTPUT"

  COUNT=$((COUNT + 1))

  # Separator unless last file
  if [ "$FILE" != "${FILES[-1]}" ]; then
    echo "----" >> "$OUTPUT"
  fi
done

# Final Stats Calculation
TOTAL_WORDS=$(wc -w < "$OUTPUT")
# Using awk for floating point math: Words * 1.3
TOTAL_TOKENS=$(awk "BEGIN {print int($TOTAL_WORDS * 1.3)}")

echo "✅ Done!"
echo "📖 Total files count: $COUNT"
echo "📝 Total Words: $TOTAL_WORDS"
echo "🤖 Estimated Tokens (Words * 1.3): $TOTAL_TOKENS"
echo "🚀 File saved to: $OUTPUT"

