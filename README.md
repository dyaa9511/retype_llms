# Retype → llms.txt Exporter

This project provides a lightweight GitHub Action and Python script to generate a `llms.txt` file from a [Retype](https://retype.com/) documentation project. It produces a **lossless, LLM-ready version of your markdown documentation**, with proper file separation, front-matter handling, URL routing, and image context.

The script reads `retype.yml` to determine:

* **`input:`** — the folder containing your markdown source files
* **`url:`** *(optional)* — the base URL used to construct public URLs and resolve relative image paths for AI processing

This ensures the generated `llms.txt` accurately reflects your project structure, routes, and image references.

![image](/image.png)

---

## Features

* Detects Retype projects by reading `retype.yml`
* Automatically finds the input markdown directory from `input:`
* Generates accurate routes based on Retype's routing logic (respects `permalink`, `route` front-matter, and default file behavior)
* Uses custom slugification matching Retype's URL patterns
* Optionally uses the `url:` field to provide absolute public URLs and image context for AI
* Excludes `static`, `node_modules`, and `.git` folders
* Strips YAML front-matter (`---`) from markdown files
* Adds semantic section headers with source file path and public URL for easy LLM parsing
* Shows total files, total words, and estimated tokens for LLM integration
* Outputs `llms.txt` to `static/` folder inside the Retype input directory

---

## Usage as Script

### Requirements

* Python 3.6+
* PyYAML package

### Installation & Running

```bash
# Clone repository
git clone https://github.com/zakaria-chahboun/retype_llms.git
cd retype_llms

# Install dependencies
pip install pyyaml

# Run the script from your Retype project root
python llms.py

# Or specify a source directory
python llms.py source
python llms.py docs
```

Example output:

```
🔍 Checking for Retype project...
📂 Retype input directory from retype.yml: source
📚 Processing markdown files:
  → source/Branch Management.md
  → source/Estimation.md
  → source/Helper/Authentication Example In Code.md
  → source/Helper/xcode-decryption-guide.md
  → source/Integrator Studio/App Creation.md
  → source/Integrator Studio/Authentication.md
  → source/Order Management/Advanced Address Types.md
  → source/Order Management/Delivery.md
  → source/Webhook.md
  → source/welcome.md
✅ Done!
📖 Total files count: 10
📝 Total Words: 8561
🤖 Estimated Tokens (Words * 1.3): 11129
🚀 File saved to: source/static/llms.txt
```

---

## GitHub Actions Usage

You can integrate this as a GitHub Action in your Retype project. Simply add this workflow to `.github/workflows/llms.yml`:

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
        # Or use @main for the latest version
      
      - name: Commit and push if changed
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add -A
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update llms.txt" && git push)
```

This will automatically generate the `llms.txt` in your Retype project's `static/` folder on each workflow run.

### Using with Retype Build Action

You can run the llms.txt generator before Retype builds your site:

```yaml
name: Build Retype Documentation
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
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

### Optional: Custom Input Directory

If you need to override the input directory from `retype.yml`:

```yaml
- name: Generate llms.txt
  uses: zakaria-chahboun/retype_llms@v2.0.0
  with:
    source: docs  # Optional: overrides input from retype.yml
```

**Input Directory Priority:**
1. **GitHub Action `source` input** (highest priority)
2. **`input:` field in `retype.yml`**
3. **Default: `.`** (current directory)

---

## How It Works

### Input Directory Priority

The script determines the input directory using this priority order:

1. **CLI/Action argument** (e.g., `python llms.py source` or GitHub Action `source` input) - highest priority
2. **`input:` field in `retype.yml`**
3. **Default: `.`** (current directory) - lowest priority

The script validates that `retype.yml` exists and checks if the determined input directory is accessible.

### Routing Logic

The script generates routes that match Retype's behavior:

1. **Front-matter priority**: If a file has `permalink` or `route` in its front-matter, that value is used
2. **Default files**: Files named `index`, `readme`, `welcome`, `default`, `home`, or matching their parent folder name become directory indexes (e.g., `/folder/` instead of `/folder/filename/`)
3. **Regular files**: Other files get routes based on their path and filename (e.g., `/folder/filename/`)
4. **Slugification**: URLs are converted to lowercase with spaces replaced by hyphens, matching Retype's URL patterns

### Output Format

The generated `llms.txt` includes:

* **AI context header** explaining the file structure and image URL handling
* **Section markers** for each markdown file with:
  * Source file path relative to project root
  * Public URL (full if base URL is configured, relative otherwise)
  * Content boundaries with `--- CONTENT START ---` and `--- CONTENT END ---`
* **Statistics** showing total files processed, word count, and estimated tokens

---

## Notes for LLMs

* Each markdown file is clearly separated with `### SECTION` headers containing file path and public URL
* YAML front-matter is removed to avoid confusing AI models
* Content boundaries are marked with `--- CONTENT START ---` and `--- CONTENT END ---`
* Public URLs can be used to reference specific documentation pages
* Relative image paths can be resolved using the base URL from `retype.yml` (if provided)
* Total files, words, and estimated tokens are provided for context planning

---

**Repository:** [https://github.com/zakaria-chahboun/retype_llms](https://github.com/zakaria-chahboun/retype_llms)