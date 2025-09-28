#!/bin/bash
# CORTEX v2.1 Migration Script - Clean Eyes to 1%
# Date: 2025-09-28
# Purpose: Move autosaves to cortex-memory, keep only essential files

echo "🧠 CORTEX v2.1 - Cleaning super-system-eyes to 1%"
echo "================================================="

# Files to KEEP in super-system-eyes (critical only)
KEEP_FILES=(
  "README.md"
  ".gitignore"
  "BRAIN-INDEX.md"
  "CURRENT-STATE.md"
  "CORTEX-ARCHITECTURE.md"
  "userPreferences-CORTEX-v2.md"
  "package.json"
)

# Files to DELETE (deprecated)
DELETE_FILES=(
  "boris-userPreferences.md"
  "userPreferences-STABLE.md"
  "userPreferences-UNIVERSAL.md"
  "MIGRATION_CHECKPOINT.md"
  "cortex_production_migration.py"
  "cortex_safe_migration.py"
)

# Folders to MOVE to cortex-memory
MOVE_FOLDERS=(
  "autosaves"
  "research"
  "architecture"
  "cortex"
)

echo "📋 Migration Plan:"
echo "- Keep: ${#KEEP_FILES[@]} essential files"
echo "- Delete: ${#DELETE_FILES[@]} deprecated files"
echo "- Move: ${#MOVE_FOLDERS[@]} folders to cortex-memory"
echo ""

# This is a dry-run script showing what would be done
echo "⚠️  DRY RUN - Showing what would be done:"
echo ""

echo "1️⃣ Files to DELETE:"
for file in "${DELETE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "   ❌ $file"
  fi
done

echo ""
echo "2️⃣ Folders to MOVE to cortex-memory:"
for folder in "${MOVE_FOLDERS[@]}"; do
  if [ -d "$folder" ]; then
    echo "   📦 $folder/ → cortex-memory/$folder/"
  fi
done

echo ""
echo "3️⃣ Files to KEEP (eyes core):"
for file in "${KEEP_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "   ✅ $file"
  fi
done

echo ""
echo "================================================="
echo "After migration, super-system-eyes will be ~1% size"
echo "All history preserved in cortex-memory repository"
echo ""
echo "To execute migration, run with --execute flag"
