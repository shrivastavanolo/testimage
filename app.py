from typing import List, Dict
import pymupdf  # PyMuPDF
import re
import json
from pathlib import Path


class PDFQuestionExtractor:
    """
    Extracts structured question data (text + images) from a PDF file.
    Saves extracted question text and associated images to an output directory.
    """

    def __init__(self, pdf_path: str, output_dir: str):
        """
        Initialize the extractor with the PDF path and output directory.
        
        Args:
            pdf_path (str): Path to the input PDF file.
            output_dir (str): Path to the output directory where images and JSON will be saved.
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.image_dir = self.output_dir / "images"
        self.json_path = self.output_dir / "questions_structured.json"
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def extract(self) -> Path:
        """
        Orchestrates the full extraction pipeline: text, images, structuring, and saving.
        
        Returns:
            Path: Path to the saved JSON file containing structured questions.
        """
        pages_text, image_data = self._extract_text_and_images()
        questions = self._structure_questions(pages_text, image_data)
        self._save_json(questions)
        return self.json_path

    def _extract_text_and_images(self) -> (str, List[Dict]):
        """
        Extracts text and image data from the PDF.
        
        Returns:
            Tuple[str, List[Dict]]: Combined text of all pages and a list of image metadata.
        """
        doc = pymupdf.open(self.pdf_path)
        self.doc = doc  # Retain reference for context if needed
        all_text = []
        image_data = []
        prev = 0  # 0 if last text was question, 1 if option
        ques = 1
        option = '[A]'
        img_count = 0

        for page_number, page in enumerate(doc, start=1):
            content = page.get_text("dict", sort=True)
            for i in range(len(content["blocks"]) - 1):
                block = content["blocks"][i]

                if block["type"] == 0:  # Text block
                    for line in block['lines']:
                        text = line['spans'][0]['text']
                        if len(line) == 0 or len(text) == 0:
                            continue
                        all_text.append(text)
                        # Detect if it's a new question
                        matches_ques = re.search(r'\b(\d+)\.(?!\n)', text)
                        matches_option = re.search(r'\[[A-D]\]', text)
                        if matches_ques:
                            prev = 0
                            ques = matches_ques.string[:2]
                            
                        if matches_option:
                            prev = 1
                            option = matches_option.string[1]

                elif block["type"] == 1:  # Image block
                    img_bytes = block['image']
                    # Name based on whether it’s a question image or option image
                    if prev == 1:
                        img_name = f'q{ques}_option{option}_{img_count}.{block["ext"]}'
                    else:
                        img_name = f'img_q{ques}_{img_count}.{block["ext"]}'
                    img_count += 1
                    image_data.append({
                        "data": img_bytes,
                        "page": page_number,
                        "name": img_name,
                    })
                    

        return "\n".join(all_text), image_data

    def _structure_questions(self, combined_text: str, image_data: List[Dict]) -> List[Dict]:
        """
        Structures the extracted text and images into a list of question dictionaries.
        
        Args:
            combined_text (str): Combined textual content of all pages.
            image_data (List[Dict]): Metadata and binary data of extracted images.

        Returns:
            List[Dict]: Structured question data.
        """
        questions = []
        img_index = 0
        parts = re.split(r'(?:^|\n)(\d{1,2})\.\s', combined_text)
        q_number = 1

        for i in range(1, len(parts), 2):
            q_text = parts[i + 1].strip()
            
            question_images = []
            option_images = []

            while img_index < len(image_data):
                img_name = image_data[img_index]['name']
                img_path = self.image_dir / img_name
                with open(img_path, "wb") as f:
                    f.write(image_data[img_index]["data"])

                if f'img_q{q_number}' in img_name:
                    question_images.append(str(img_path))
                elif f'q{q_number}' in img_name:
                    option_images.append(str(img_path))

                # Stop scanning images if we reached the next question
                if f'q{q_number}' not in img_name:
                    break

                img_index += 1
            questions.append({
                "question_number": q_number,
                "question": re.sub(
                    r'Ans\s*\[[A-D]\]|\[[A-D]\].*|Ans.*|SECTION.*|\n\n.*|\n',
                    '', q_text
                ).strip(),
                "question_images": question_images,
                "option_images": option_images
            })

            q_number += 1

        return questions

    def _save_json(self, data: List[Dict]):
        """
        Saves the structured question data to a JSON file.
        
        Args:
            data (List[Dict]): The structured question list.
        """
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ==================== main =====================

if __name__ == "__main__":
    pdf_file_path = "testcontent.pdf"     # Path to the input PDF
    output_directory = ""                 # Directory to save images and JSON

    extractor = PDFQuestionExtractor(pdf_file_path, output_directory)
    output_json_path = extractor.extract()

    print(f"✅ Structured question data saved to: {output_json_path}")
