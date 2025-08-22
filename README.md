# 🧠 Adobe India Hackathon 2025 – Challenge 1A Solution

## 📌 Problem Statement

Automatically extract a structured representation of headings (like H1, H2, etc.) from diverse PDF documents, including the document's title and a hierarchical section outline, and output the result in a specific JSON format.

---

## 🚀 Our Approach

This solution programmatically processes PDF files and extracts:

- 📘 The main **title**
- 🧱 All **headings**, organized hierarchically (H1–H4)
- 📄 Corresponding **0-based page numbers**

Our logic combines **font size clustering**, **prefix-based hierarchy detection**, and **text heuristics** to ensure robustness across varied PDFs.

---

## 🧰 Technologies & Libraries Used

| Purpose              | Library             |
|----------------------|---------------------|
| PDF parsing          | PyMuPDF (`fitz`)    |
| Data handling        | `collections`, `os`, `re`, `json` |
| Output generation    | Built-in `json`     |
| Containerization     | Docker              |

All dependencies are open source and compliant with Adobe’s constraints (≤200MB size, CPU-only, offline execution, etc.).

---

## 📁 Folder Structure

```
adobe_round1a/
├── input/         # Folder for all input PDF files
├── output/        # Folder where JSON outputs are saved
├── main.py        # Core PDF processing script
├── Dockerfile     # For building the container
└── README.md      # This documentation file
```

---

## ⚙️ How It Works

### 🏷️ Title Extraction
- The **largest font size** on the first page is assumed to represent the **title**.
- All text lines matching the top font size are combined to form the title.

### 🧩 Heading Detection Logic
- Each PDF page is parsed using PyMuPDF’s `get_text("dict")`.
- Lines are evaluated based on **font size** and filtered using a custom `is_probable_heading()` function to eliminate noise.
- Multi-line headings are merged, and levels are determined by:
  - **Numbered prefixes** (e.g., `1.`, `1.2`, etc.)
  - **Relative font size ranking** (`H1` = largest size, and so on)
- Special handling is applied to prevent false positives in slides or styled PDFs.

### 📌 Page Numbering
- Each heading includes the **0-based page number** in the final JSON output.

---

## 🧪 Build & Run Instructions

### ✅ Step 1: Build Docker Image

From the project root, run:

```bash
docker build --platform linux/amd64 -t adobe-solution:round1a .
```

### ✅ Step 2: Run the Container

```bash
docker run --rm   -v "$(pwd)/input:/app/input:ro"   -v "$(pwd)/output:/app/output"   --network none   adobe-solution:round1a
```

---

## 📤 Output Format

For every input `filename.pdf`, the tool generates `output/filename.json` with the structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 0
    },
    {
      "level": "H2",
      "text": "1.1 Background",
      "page": 1
    }
  ]
}
```

---

## 📋 Adobe Compliance Checklist

| ✅ Item                                 | Status |
|----------------------------------------|--------|
| Processes all PDFs in `/app/input`     | ✅ Yes |
| Produces JSON outputs in `/app/output` | ✅ Yes |
| JSON format matches Adobe schema       | ✅ Yes |
| Runs under 10s for 50-page PDFs        | ✅ Yes |
| No internet used during runtime        | ✅ Yes |
| Dockerized using AMD64 + CPU-only      | ✅ Yes |
| Model size ≤ 200MB                     | ✅ Yes |
| Memory usage under 16GB                | ✅ Yes |

---

## 🧪 Testing Strategy

- ✅ Validated against Adobe’s expected JSON outputs for 5 sample PDFs (`file01.json` to `file05.json`)
- ✅ Handles variations in heading styles, font sizes, and layouts
- ✅ Ignores non-heading elements such as footers, dates, and decorative text
