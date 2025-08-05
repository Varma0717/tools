#!/usr/bin/env python3
"""
Batch update tools to use the new tools_base.html layout with ads
"""

import os
import glob


def update_tool_template(file_path):
    """Update a single tool template to use the new layout"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if already using tools_base
        if "tools/tools_base.html" in content:
            return f"✓ {os.path.basename(file_path)}: Already using tools_base"

        # Skip if not extending base.html
        if '{% extends "base.html" %}' not in content:
            return f"⚠ {os.path.basename(file_path)}: Not extending base.html"

        # Update extends
        content = content.replace(
            '{% extends "base.html" %}', '{% extends "tools/tools_base.html" %}'
        )

        # Update content block to tool_content
        content = content.replace("{% block content %}", "{% block tool_content %}")

        # Remove the container div if present
        lines = content.split("\n")
        updated_lines = []
        skip_container = False

        for line in lines:
            # Look for container div after tool_content block
            if "{% block tool_content %}" in line:
                updated_lines.append(line)
                skip_container = True
                continue
            elif skip_container and '<div class="max-w-' in line and "mx-auto" in line:
                # Skip this container div
                continue
            elif skip_container and line.strip() == "</div>" and len(updated_lines) > 0:
                # Check if this is the closing div for container
                # We'll look for the pattern where it's likely the main container
                recent_lines = "\n".join(updated_lines[-10:])
                if "<div class=" not in recent_lines or "mx-auto" in recent_lines:
                    # This is likely the container closing div, skip it
                    skip_container = False
                    continue

            updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return f"✅ {os.path.basename(file_path)}: Updated successfully"

    except Exception as e:
        return f"❌ {os.path.basename(file_path)}: Error - {str(e)}"


def main():
    print("Batch Tool Template Updater")
    print("=" * 50)

    # Get all tool templates
    tool_templates = glob.glob("templates/tools/*.html")

    # Exclude the base template and other special templates
    exclude_files = ["tools_base.html", "category_page.html", "index.html"]
    tool_templates = [
        t for t in tool_templates if not any(ex in t for ex in exclude_files)
    ]

    print(f"Found {len(tool_templates)} tool templates to update...")
    print()

    results = []
    for template_path in tool_templates:
        result = update_tool_template(template_path)
        results.append(result)
        print(result)

    print("\n" + "=" * 50)
    print("UPDATE SUMMARY")
    print("=" * 50)

    successful = len([r for r in results if r.startswith("✅")])
    already_updated = len([r for r in results if r.startswith("✓")])
    errors = len([r for r in results if r.startswith("❌")])
    warnings = len([r for r in results if r.startswith("⚠")])

    print(f"✅ Successfully updated: {successful}")
    print(f"✓ Already using tools_base: {already_updated}")
    print(f"⚠ Warnings: {warnings}")
    print(f"❌ Errors: {errors}")
    print(f"📊 Total templates: {len(tool_templates)}")

    if successful > 0:
        print(f"\n🎉 Updated {successful} templates to use the new ad-enabled layout!")

    return 0


if __name__ == "__main__":
    os.chdir("c:/xampp/htdocs/app")
    exit(main())
