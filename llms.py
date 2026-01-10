import os
import re
import yaml
import pathlib
import argparse

import os
import yaml
import argparse

def get_retype_config():
    # defaults
    input_dir = "."
    url = ""
    input_dir_from = "default"

    # parse CLI args first
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", help="optional source directory")
    args = parser.parse_args()

    # load retype.yml if exists
    if os.path.exists("retype.yml"):
        with open("retype.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

            # take input from yml only if CLI source not provided
            if not args.source:
                input_dir = config.get("input", input_dir)
                input_dir_from = "retype.yml"

            url = config.get("url", url).rstrip("/")

    # CLI source ALWAYS overrides input
    if args.source:
        input_dir = args.source
        input_dir_from = "CLI"

    return {
        "input": input_dir,
        "url": url,
        "input_dir_from": input_dir_from
    }

def retype_slugify(text):
    """
    Rule: remove unwanted chars, trim, to lower, replace spaces with -
    Allowed: alphanumeric, dashes, underscores, and specific punctuation like * ! ( ) 
    """
    text = text.lower()
    text = text.replace(" ", "-")
    # Keeps only alphanumeric and specific allowed symbols seen in Retype URLs
    text = re.sub(r'[^a-z0-9\-_\*\!\(\)]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text

def extract_front_matter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines or not lines[0].strip() == "---":
        return {}, "".join(lines)
    fm_lines = []
    content_start = 0
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            content_start = i + 1
            break
        fm_lines.append(line)
    else:
        return {}, "".join(lines)
    try:
        metadata = yaml.safe_load("".join(fm_lines)) or {}
        return metadata, "".join(lines[content_start:])
    except:
        return {}, "".join(lines[content_start:])

def generate_route(file_path, input_dir):
    file_path_obj = pathlib.Path(file_path)
    fm, content = extract_front_matter(file_path)
    
    if "permalink" in fm: return fm["permalink"], content
    if "route" in fm: return fm["route"], content

    rel_path = file_path_obj.relative_to(input_dir)
    slugged_parts = [retype_slugify(part) for part in rel_path.parent.parts]
    
    filename_stem = file_path_obj.stem
    slugged_filename = retype_slugify(filename_stem)
    
    parent_folder_raw = file_path_obj.parent.name
    defaults = {"index", "readme", "welcome", "default", "home", parent_folder_raw.lower()}
    
    if filename_stem.lower() in defaults:
        route = "/" + "/".join(slugged_parts) + "/"
    else:
        route = "/" + "/".join(slugged_parts + [slugged_filename]) + "/"

    route = re.sub(r'/+', '/', route)
    return route, content

def main():
    print("🔍 Checking for Retype project...")
    if not os.path.exists("retype.yml"):
        print("❌ Not a Retype project (retype.yml not found).")
        return

    config = get_retype_config()
    input_dir = config["input"]
    base_url = config["url"]
    input_dir_from = config["input_dir_from"]

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' not found.")
        return

    print(f"📁 Retype input directory from {input_dir_from}: {input_dir}")
    print("📚 Processing markdown files:")

    output_file = os.path.join(input_dir, "static", "llms.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    markdown_files = []
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if d not in ["static", "node_modules", ".git"]]
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    markdown_files.sort()

    total_words = 0
    with open(output_file, "w", encoding="utf-8") as f:
        # Improved AI Instructions
        f.write("# NOTE FOR AI CONTEXT\n")
        f.write("- This file contains multiple documentation sections concatenated into one.\n")
        f.write("- Each section begins with a '### SECTION' header containing the Source File and Public URL.\n")
        f.write("- Use the Public URL when referencing these documents to the user.\n")
        if base_url:
            f.write(f"- Absolute Image URL Base: {base_url}\n")
            f.write("- Convert relative image paths found in sections by prefixing them with the Base URL.\n")
        f.write("================================================================================\n\n")

        for i, file_path in enumerate(markdown_files):
            rel_display = os.path.relpath(file_path, ".")
            print(f"  → {rel_display}")
            
            route, content = generate_route(file_path, input_dir)
            full_url = f"{base_url}{route}" if base_url else route
            
            # Semantic headers that LLMs can easily parse
            f.write(f"### SECTION: File: {rel_display}, URL: {full_url}\n")
            f.write("--- CONTENT START ---\n")
            
            clean_content = content.strip()
            f.write(clean_content)
            
            f.write("\n--- CONTENT END ---\n")
            
            # Calculate word count for the stats
            total_words += len(f"File: {rel_display} URL: {full_url}".split())
            total_words += len(clean_content.split())
            
            if i < len(markdown_files) - 1:
                f.write("\n\n")

    total_tokens = int(total_words * 1.3)
    print("✅ Done!")
    print(f"📖 Total files count: {len(markdown_files)}")
    print(f"📝 Total Words: {total_words}")
    print(f"🤖 Estimated Tokens (Words * 1.3): {total_tokens}")
    print(f"🚀 File saved to: {output_file}")

if __name__ == "__main__":
    main()
