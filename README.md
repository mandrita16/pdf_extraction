# 📄 PDF Extraction System

This project is designed to extract **structured content** from PDF files including **text, metadata, fonts, and images**, with robust error handling, optional image extraction, and an interactive command-line interface. It's powered by `PyMuPDF` for PDF processing, `Pillow` for image handling, and `NumPy` for efficient computations.

---

## 🚀 Project Structure

pdf_extraction_master/
│
├── README.md 
├── src/
│ ├── pdf_extraction_pipeline.py ← Core engine (EfficientPDFExtractor class)
│ ├── bulletproof_test.py ← Bulletproof test script for validation
│ ├── interactive_demo.py ← Menu-based CLI for non-dev usage
│ └── pdf_env/ ← (Optional) Local virtual environment
├── test_pdfs/ ← Place your PDFs here
├── output/ ← Extracted results (JSON + summary text)


---

## 📦 Dependencies & Libraries

| Library      | Purpose                                          |
|--------------|--------------------------------------------------|
| PyMuPDF      | High-performance PDF reading, rendering, parsing |
| Pillow       | Image manipulation and saving                    |
| NumPy        | Efficient handling of image arrays and stats     |
| json         | Saving structured output                         |
| hashlib      | Avoid reprocessing same files (via MD5 hashes)   |
| logging      | For clean status updates and debugging           |
| datetime     | Timestamped result saving                        |

---

## 🧠 What Each File Does

### ✅ `pdf_extraction_pipeline.py`
The **core processing engine**:
- Contains the `EfficientPDFExtractor` class.
- Uses `fitz` to read PDFs efficiently page-by-page.
- Extracts: text, font info, word/char counts, document metadata, images.
- Outputs results to `.json` and `.txt` formats.
- `demonstrate_usage()` lets you test single or batch processing quickly.

> This is the brain of your project.

---

### ✅ `bulletproof_test.py`
A **diagnostic script** to validate:
- Your Python version and environment
- Required libraries are installed
- Whether PDFs are readable and processable
- If extraction and saving works properly

> Use this to test everything works before pushing to production or demoing.

---

### ✅ `interactive_demo.py`
An **interactive, menu-driven CLI** for non-coders:
- Lets users list available PDFs
- Choose one for extraction
- Batch process all PDFs in `test_pdfs/`
- Opens output folder directly

> Great for testers, non-devs, or showcasing functionality.

---

## 🛠️ Installation & Setup

### ✅ Step 1: Clone the Repo & Open Terminal

```bash
cd pdf_extraction_master/src

### ✅ Step 2: Create Virtual Environment
python -m venv pdf_env

### ✅ Step 3: Activate Environment
Windows:

.\pdf_env\Scripts\activate

macOS/Linux:

source pdf_env/bin/activate

✅ Step 4: Install Required Libraries

pip install PyMuPDF Pillow numpy requests

✅ Optional :

pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers opencv-python pdf-extract-kit docling

✅ Step 5: Verify Install 

python -c "import fitz; print('PyMuPDF works!')"
python -c "import PIL; print('Pillow works!')"
python -c "import numpy; print('NumPy works!')"

🧪 Test Your Setup

python bulletproof_test.py
Expected:

✅ Metadata shown

✅ Page count, word/image stats

✅ JSON saved in /output

💻 Run the Interactive Demo

python interactive_demo.py

Menu lets you:

📄 List PDFs in /test_pdfs/

🔄 Run extraction on selected file

📊 Batch process all PDFs

📁 Open output folder

📥 Using Your Own PDFs
Drop any .pdf files into test_pdfs/

 Run either:

python bulletproof_test.py
or

python interactive_demo.py

Results will be saved as:

output/filename_timestamp.json

output/filename_timestamp_summary.txt

📬 Contact
Developed by Mandrita Dasgupta
For queries or contributions, open an issue or reach out on GitHub.

