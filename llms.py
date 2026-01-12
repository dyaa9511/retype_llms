import os
import re
import yaml
import pathlib
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

def slugify_to_title(slug):
    """Convert slug back to title format (replace - with space, capitalize)"""
    return slug.replace("-", " ").title()

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
    
    if "permalink" in fm: 
        return fm["permalink"], content, fm
    if "route" in fm: 
        return fm["route"], content, fm

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
    return route, content, fm

def get_document_title(file_path, front_matter):
    """Get title from front matter or generate from filename"""
    if "title" in front_matter:
        return front_matter["title"]
    
    # Generate title from filename
    filename_stem = pathlib.Path(file_path).stem
    slugged = retype_slugify(filename_stem)
    return slugify_to_title(slugged)

def replace_relative_links(content, base_url):
    """Replace relative markdown links and images with absolute URLs"""
    if not base_url:
        return content
    
    # Parse base URL to extract domain and base path
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    base_path = parsed.path.rstrip('/')
    
    # Pattern for markdown images: ![alt](path)
    # Matches relative paths (starting with / or not starting with http:// or https://)
    def replace_image(match):
        alt_text = match.group(1)
        path = match.group(2)
        
        # Skip if already absolute URL
        if path.startswith('http://') or path.startswith('https://'):
            return match.group(0)
        
        # Handle paths starting with /
        if path.startswith('/'):
            # Check if path already contains the base_path to avoid duplication
            if base_path and path.startswith(base_path):
                return f'![{alt_text}]({domain}{path})'
            else:
                return f'![{alt_text}]({domain}{base_path}{path})'
        else:
            # Handle relative paths without leading /
            return f'![{alt_text}]({domain}{base_path}/{path})'
    
    # Pattern for markdown links: [text](path)
    def replace_link(match):
        link_text = match.group(1)
        path = match.group(2)
        
        # Skip if already absolute URL
        if path.startswith('http://') or path.startswith('https://'):
            return match.group(0)
        
        # Skip anchors
        if path.startswith('#'):
            return match.group(0)
        
        # Handle paths starting with /
        if path.startswith('/'):
            # Check if path already contains the base_path to avoid duplication
            if base_path and path.startswith(base_path):
                return f'[{link_text}]({domain}{path})'
            else:
                return f'[{link_text}]({domain}{base_path}{path})'
        else:
            # Handle relative paths without leading /
            return f'[{link_text}]({domain}{base_path}/{path})'
    
    # Replace images first
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
    
    # Replace links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    
    return content

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

    print(f"📂 Retype input directory from {input_dir_from}: {input_dir}")
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
        for i, file_path in enumerate(markdown_files):
            rel_display = os.path.relpath(file_path, ".")
            print(f"  → {rel_display}")
            
            route, content, fm = generate_route(file_path, input_dir)
            full_url = f"{base_url}{route}" if base_url else route
            title = get_document_title(file_path, fm)
            
            # Replace relative links with absolute URLs if base_url exists
            if base_url:
                content = replace_relative_links(content, base_url)
            
            # XML structure
            f.write("<document>\n")
            f.write(f"<title>{title}</title>\n")
            f.write(f"<url>{full_url}</url>\n")
            f.write("<content>\n\n")
            
            clean_content = content.strip()
            f.write(clean_content)
            
            f.write("\n\n</content>\n")
            f.write("</document>\n")
            
            # Calculate word count for the stats
            total_words += len(title.split())
            total_words += len(full_url.split())
            total_words += len(clean_content.split())
            
            if i < len(markdown_files) - 1:
                f.write("\n")

    total_tokens = int(total_words * 1.3)
    print("✅ Done!")
    print(f"📖 Total files count: {len(markdown_files)}")
    print(f"📝 Total Words: {total_words}")
    print(f"🤖 Estimated Tokens (Words * 1.3): {total_tokens}")
    print(f"🚀 File saved to: {output_file}")

if __name__ == "__main__":
    main()