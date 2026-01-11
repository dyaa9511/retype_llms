# Retype → llms.txt Exporter

Convert your [Retype](https://retype.com/) documentation into a single, LLM-friendly file that AI assistants can actually understand.

![image](/image.png)

## Why This Exists

Documentation is great for humans browsing your site, but terrible for AI assistants trying to help your users. This tool bridges that gap by compiling your Retype markdown files into `llms.txt` - a structured format that LLMs can parse and reference accurately.

The script respects your Retype configuration, preserves your routing structure, and converts relative links to absolute URLs so AI assistants can cite your docs properly.

## What You Get

- **XML-structured output** that LLMs parse reliably
- **Accurate routing** matching your Retype site (permalink, route, default files)
- **Absolute URLs** for all images and links when you set a base URL
- **Clean content** with front-matter stripped out
- **Smart filtering** that skips static assets, node_modules, and git files

The generated file lands in your `static/` folder, ready to serve alongside your docs.

## Quick Start

### As a Python Script

```bash
# Clone and install
git clone https://github.com/zakaria-chahboun/retype_llms.git
cd retype_llms
pip install pyyaml

# Run from your Retype project root
python llms.py

# Or specify your docs folder
python llms.py docs
```

You'll see output like this:

```
🔍 Checking for Retype project...
📂 Retype input directory from retype.yml: source
📚 Processing markdown files:
  → source/getting-started.md
  → source/api/authentication.md
  → source/guides/webhooks.md
✅ Done!
📖 Total files: 24
📝 Total words: 12,847
🤖 Estimated tokens: 16,701
🚀 Saved to: source/static/llms.txt
```

### As a GitHub Action

Drop this into `.github/workflows/llms.yml`:

```yaml
name: Generate llms.txt
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate llms.txt
        uses: zakaria-chahboun/retype_llms@v2.0.0
      
      - name: Commit changes
        run: |
          git config user.name 'github-actions[bot]'
          git config user.email 'github-actions[bot]@users.noreply.github.com'
          git add -A
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "Update llms.txt" && git push)
```

The action runs on every push and keeps your `llms.txt` in sync automatically.

### With Your Retype Build

Combine it with your existing Retype workflow:

```yaml
name: Publish Documentation
on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate llms.txt
        uses: zakaria-chahboun/retype_llms@v2.0.0
      
      - name: Build Retype
        uses: retypeapp/action-build@latest
      
      - name: Deploy to GitHub Pages
        uses: retypeapp/action-github-pages@latest
        with:
          update-branch: true
```

## Configuration

The script reads your `retype.yml` to figure out where things are:

```yaml
input: docs        # Where your markdown lives
url: https://docs.example.com  # Your site's base URL (optional but recommended)
```

**Base URL Benefits:** When you provide a URL, the script converts all relative links and images to absolute ones. This means AI assistants can reference `https://docs.example.com/static/diagram.png` instead of just `static/diagram.png`.

### Custom Input Directory

Override the input directory if needed:

**CLI:**
```bash
python llms.py source
```

**GitHub Action:**
```yaml
- uses: zakaria-chahboun/retype_llms@v2.0.0
  with:
    source: docs
```

Priority order: CLI/Action input → retype.yml → current directory

## Output Format

The generated `llms.txt` uses clean XML structure:

```xml
<document>
<title>Getting Started</title>
<url>https://docs.example.com/getting-started/</url>
<content>

# Getting Started

Your markdown content here, exactly as written.

Images and links are converted to absolute URLs.

</content>
</document>

<document>
<title>API Reference</title>
<url>https://docs.example.com/api/</url>
<content>

# API Reference

More content...

</content>
</document>
```

**What happens to your content:**
- Front-matter (YAML between `---`) gets stripped
- Document title comes from front-matter `title:` or filename
- Relative links become absolute when base URL is set
- Everything else stays exactly as you wrote it

## How Routing Works

The script matches Retype's routing logic:

1. **Explicit routes win:** Files with `permalink` or `route` in front-matter use those values
2. **Special files become indexes:** `index.md`, `readme.md`, `welcome.md` map to their directory (`/docs/` not `/docs/readme/`)
3. **Everything else gets slugified:** Spaces become dashes, special chars get stripped, just like Retype does it

Examples:
- `docs/Getting Started.md` → `/docs/getting-started/`
- `docs/api/index.md` → `/docs/api/`
- `docs/Advanced Topics.md` with `permalink: /advanced/` → `/advanced/`

## Requirements

- Python 3.6 or newer
- PyYAML (`pip install pyyaml`)
- A Retype project with `retype.yml`

## Repository

[github.com/zakaria-chahboun/retype_llms](https://github.com/zakaria-chahboun/retype_llms)

---

*Found a bug? Have an idea? Open an issue or PR.*