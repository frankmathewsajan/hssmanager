# backend/students/services.py
import pdfplumber
import io


def extract_hscap_allotment(file_bytes: bytes) -> dict:
    """
    Extracts student allotment data natively from a DGE Kerala HSCAP PDF document.
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page = pdf.pages[0]
            tables = page.find_tables()

            if not tables:
                return {
                    "error": "CRITICAL FAILURE: No explicit table grid detected in the document."
                }

            table_bbox = tables[0].bbox
            table_top_y = table_bbox[1]

            # Extract the top text to capture School and Course Context
            top_crop = page.within_bbox((0, 0, page.width, table_top_y))
            top_text = top_crop.extract_text()
            course_info = (
                top_text.split("\n")[0] if top_text else "Unknown Course Context"
            )

            # Extract tabular data
            raw_table_data = tables[0].extract()
            if not raw_table_data or len(raw_table_data) < 2:
                return {"error": "Table extraction yielded insufficient data rows."}

            parsed_students = []

            # Skip the header row (index 0)
            for row in raw_table_data[1:]:
                if not row or len(row) < 12 or not row[1]:
                    continue

                parsed_students.append(
                    {
                        "app_num": str(row[1]).replace("\n", "").strip(),
                        "rank": str(row[2]).replace("\n", "").strip(),  # NEW: Index 2
                        "option": str(row[3]).replace("\n", "").strip(),  # NEW: Index 3
                        "name": str(row[4]).replace("\n", "").strip().title(),
                        "reg_num": str(row[5]).replace("\n", "").strip(),
                        "dob": str(row[6]).replace("\n", "").strip(),
                        "gender": str(row[7]).replace("\n", "").strip().title(),
                        "second_language": str(row[10])
                        .replace("\n", "")
                        .strip()
                        .title(),
                        "fee_status": str(row[11])
                        .replace("\n", " ")
                        .strip()
                        .title(),  # NEW: Index 11 (e.g., "Fee Paid")
                    }
                )

            return {"course_info": course_info, "students": parsed_students}

    except Exception as e:
        return {"error": f"PDF parsing failure: {str(e)}"}
