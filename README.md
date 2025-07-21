# PDF Question Extractor

A Python-based tool to extract structured questions and associated images from educational PDFs. It identifies questions and options, extracts related images, and outputs structured JSON data.

## 📦 Features

- Extracts **question text** and **option text** from PDF pages.
- Saves embedded **images** (diagrams, options, etc.) from the PDF.
- Maps each image to its corresponding **question** or **option**.
- Outputs a well-structured `questions_structured.json` file for downstream use (like model training or UI rendering).

---

## 🛠 Modules & Techniques Used

### Python Libraries
- **PyMuPDF (`pymupdf`)** – for parsing PDF files and extracting both text and images.
- **re (Regex)** – for pattern matching question numbers, options, and cleaning unwanted text.
- **json** – to write structured data into a `.json` file.
- **pathlib** – for clean and cross-platform file path handling.
- **typing** – for type hints to improve code readability and tooling support.

### Techniques
- **Regex-driven text splitting** to identify questions like `1.` or `15.`.
- **Heuristic tagging** of whether an image belongs to a question or an option using context.
- **Incremental image mapping** using filenames like `img_q1_0.png` and `q1_optionA_0.png`.

---

## 📂 Project Structure

```

📁 your-project/
│
├── testcontent.pdf                 # Your input PDF file
├── images/                         # Auto-created folder with saved images
├── questions\_structured.json      # Final structured output
└── app.py                   # The main Python script

````

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

### 2. Run the Script

```bash
python ./app.py
```

* Ensure your PDF file (e.g., `testcontent.pdf`) is in the same folder or update the path in app.py main().
* Output JSON and images will be saved in the current directory or the specified output folder (Can be updated in app.py).

---

## 📌 Output Example

A sample entry from the generated `questions_structured.json`:

```json
{
  "question_number": 1,
  "question": "What is the capital of France?",
  "question_images": ["images/img_q1_0.png"],
  "option_images": ["images/q1_optionA_0.png", "images/q1_optionB_0.png"]
}
```
