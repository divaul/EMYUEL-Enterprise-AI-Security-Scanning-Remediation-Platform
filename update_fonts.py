"""
Script to update all Arial fonts to Segoe UI in emyuel_gui.py
"""
import re

# Read the GUI file
with open('gui/emyuel_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all Arial fonts with Segoe UI
updated = content.replace("font=('Arial'", "font=('Segoe UI'")

# Write back
with open('gui/emyuel_gui.py', 'w', encoding='utf-8') as f:
    f.write(updated)

print("✅ Successfully updated all Arial fonts to Segoe UI")
print(f"Total replacements: {content.count(\"font=('Arial'\")}")
