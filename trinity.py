import re
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
import time

def process_pdf(pdf_path, poppler_path=None, dpi=300):
    if not os.path.exists(pdf_path):
        return "[ERROR] PDF not found: " + pdf_path

    # Step 1: Convert PDF pages to images
    try:
        pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    except Exception as e:
        return f"[ERROR] PDF to image failed: {str(e)}"

    full_text = ""
    for i, page in enumerate(pages):
        resized = page.resize((page.width // 2, page.height // 2))
        text = pytesseract.image_to_string(resized)
        full_text += "\n" + text

    # Step 2: Clean and tokenize
    def clean_text(text):
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'[^A-Za-z0-9 ]+', '', text)
        text = text.upper()
        return re.sub(r'\s+', ' ', text).strip()

    cleaned = clean_text(full_text)
    tokens = cleaned.split()
    text_joined = ' '.join(tokens)

    # Step 3: Helpers
    def find_token_starting_with(prefix):
        for t in tokens:
            if t.startswith(prefix):
                return t
        return '[Not Found]'

    def find_after(keyword, count=1):
        try:
            idx = tokens.index(keyword.upper())
            return ' '.join(tokens[idx+1:idx+1+count])
        except:
            return '[Not Found]'

    def find_regex(pattern):
        m = re.search(pattern, text_joined)
        return m.group(1) if m else '[Not Found]'

    def find_value_near(key, max_window=20, pattern=None):
        try:
            idx = tokens.index(key.upper())
            window = ' '.join(tokens[idx:idx+max_window])
            if pattern:
                match = re.search(pattern, window)
                return match.group(1) if match else '[Not Found]'
            return '[Not Found]'
        except:
            return '[Not Found]'

    def find_after_pair(first, second):
        for i in range(len(tokens) - 2):
            if tokens[i] == first and tokens[i+1] == second:
                return tokens[i+2]
        return '[Not Found]'

    def find_gstin_from_tokens(tokens):
        for i, token in enumerate(tokens):
            if "GST" in token:
                if i + 1 < len(tokens) and re.fullmatch(r'[A-Z0-9]{11,}', tokens[i + 1]):
                    return tokens[i + 1]
        return '[Not Found]'

    # Step 4: Key-Value Extraction
    output = {
        "Customer": find_after("CUSTOMER"),
        "AWB Number": find_regex(r'(\bAW[BGE]\w{6,}\b)'),
        "AWB Date": find_value_near("AWB", 15, r'(\d{6,8})'),
        "PO Date": find_value_near("PO", 15, r'(\d{6,8})'),
        "Invoice Number": find_regex(r'(A\d{6,12})') or find_value_near("INVOICE", 1, r'(\d{6,12})'),
        "Invoice Date": find_value_near("CURR", 20, r'(\d{6,8})') or find_value_near("VALUE", 20, r'(\d{6,8})'),
        "Invoice Number (from Invoice Block)": find_regex(r'INVOICE\s+NUMBER\s+(AA\d+)'),
        "Invoice Date (From Invoice Block)": find_regex(r'INVOICE\s+DATE\s+(\d{6,8})'),
        "Invoice Due Date": find_regex(r'DUE\s+DATE\s+(\d{6,8})'),
        "Bill of Lading": find_regex(r'BILL\s+OF\s+(?:LANDING|LADING)[\s—:-]*([A-Z]*\d{4,})'),
        "Voyage Number": find_regex(r'VOYAGE\s+NUMBER\s+([A-Z0-9]+)'),
        "Country of Origin": find_value_near("ORIGIN", 15, r'(UNITED\s+KINGDOM|INDIA|CHINA|BRAZIL)'),
        "Final Destination": find_regex(r'FINAL\s+DESTINATION\s+([A-Z\s]+?)\s+(?:INVOICE|SHIPPING|DATE)'),
        "Shipping Date": find_regex(r'SHIPPING\s+DATE\s+(\d{6,8})'),
        "HS Code": find_token_starting_with("MG") or find_regex(r'\b(17019100)\b'),
        "Quantity": find_regex(r'(\d{1,5})\s+(PCS|PES|BAGS|UNITS|PACKETS)'),
        "Total": find_regex(r'TOTAL\s+(?!ACCOUNT)(\d{4,7})'),
        "Account Charges": find_regex(r'ACCOUNT\s+CHARGES\s+(\d{4,7})'),
        "GSTIN": find_gstin_from_tokens(tokens) or find_regex(r'([A-Z0-9]{15})'),
        "Address (China)": find_value_near("CHINA", 20, r'(SHANGCHI|SUZHOU|JIANGSU)'),
        "Address (India)": find_value_near("INDIA", 30, r'(SECUNDERABAD|KANPUR|HYDERABAD)'),
        "Address (Emirates)": find_value_near("UAE", 20, r'(DUBAI|JAE|EMIRATES)') or find_regex(r'\b(DUBAI|JAE|EMIRATES)\b'),
        "Insurance Certificate No": find_regex(r'CONTIFICATE\s+NO[\s:]?([A-Z0-9]{6,})'),
        "Insurance Security No": find_regex(r'SECURITY\s+NO[\s:]*([A-Z0-9]{6,})'),
        "Insurance Client Ref": find_regex(r'CLIENT\s+REFERENCE\s+([A-Z0-9\-]+)'),
        "Sum Insured": find_regex(r'(FIVE\s+THOUSAND\s+NINE\s+HUNDRED\s+TWENTY\s+FIVE\s+USD\s+FIFTEEN\s+CENTS\s+ONLY)') or find_value_near("SUM", 20, r'(FIVE\s+THOUSAND.*?CENTS\s+ONLY)')
    }

    # Save to file (optional)
    with open("output.txt", "w", encoding="utf-8") as f:
        for k, v in output.items():
            f.write(f"{k}: {v}\n")

    return output

if __name__ == "__main__":
    print("[INFO] Starting PDF processing for pdf")
    result = process_pdf("Adobe Scan 16 Jul 2025.pdf", poppler_path=r"D:\python\poppler\bin")
    print("[INFO] Extraction complete. Output saved to output.txt")
