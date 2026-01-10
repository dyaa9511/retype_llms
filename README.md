# Retype → llms.txt Exporter

**Description:**
This project provides a lightweight GitHub Action and script to generate a `llms.txt` file from a Retype documentation project. It produces a **lossless, LLM-ready version of your markdown documentation**, with file separation, front-matter stripping, and optional context for image URLs.

The script reads `retype.yml` to determine:

* **`input:`** — the folder containing your markdown source files
* **`url:`** *(optional)* — the base URL used to resolve relative image paths for AI processing

This ensures the generated `llms.txt` accurately reflects your project structure and image references.

![image](/image.png)

---

## Features

* Detects Retype projects by reading `retype.yml`
* Automatically finds the input markdown directory from `input:`
* Optionally uses the `url:` field to provide AI context for absolute image links
* Excludes `static` folder, `node_modules`, and `.git`
* Strips YAML front-matter (`---`) from markdown files
* Adds file headers and `----` separators for clear segmentation
* Shows total files, total words, and estimated tokens for LLM integration
* Outputs `llms.txt` to `static/` folder inside the Retype input

---

## Usage as Script

```bash
# Clone repository
git clone https://github.com/zakaria-chahboun/retype_llms.git
cd retype_llms

# Make script executable
chmod +x llms.sh

# Run the script
./llms.sh
# OR
.llms.sh source_folder
```

Example output:

```
🔍 Checking for Retype project...
📁 Retype input directory: source
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

You can integrate this script as a GitHub Action workflow:

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
      - name: Run Retype llms exporter
        uses: zakaria-chahboun/retype_llms@v1.0.3
        # uses: zakaria-chahboun/retype_llms@main for latest updates
        with:
          input-dir: source  # Optional: override input directory from retype.yml
```

This will automatically generate the `llms.txt` in your Retype project's `static/` folder on each workflow run.

---

## Notes for LLMs

* Each markdown file is separated with a header and `----` for clear segmentation
* YAML front-matter is removed to avoid confusing AI models
* Relative image paths can be resolved using the `url:` field in `retype.yml` (if provided)
* The AI can use this information to convert relative image paths to absolute URLs when needed
* Total files, words, and estimated tokens are logged for LLM planning

---

**Repository:** [https://github.com/zakaria-chahboun/retype_llms](https://github.com/zakaria-chahboun/retype_llms)
