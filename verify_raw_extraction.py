import os
import glob
import pdfplumber

def verify_extraction():
    # Locate the existing downloaded file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "downloads", "real")
    pdf_files = glob.glob(os.path.join(download_dir, "*.pdf"))
    
    if not pdf_files:
        print("No PDF found to verify.")
        return

    # Use the most recent one
    target_pdf = pdf_files[0]
    print(f"Verifying File: {target_pdf}")
    print("-" * 50)

    try:
        with pdfplumber.open(target_pdf) as pdf:
            # Extract text from first 2 pages to prove content
            for i, page in enumerate(pdf.pages[:2]):
                text = page.extract_text()
                print(f"--- Page {i+1} Raw Content ---")
                print(text[:500] + "..." if text else "[No Text Found]")
                print("\n")
                
            # Extract tables if any
            print("--- Table Extraction Check ---")
            tables = pdf.pages[0].extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on Page 1.")
                print("First row of first table:", tables[0][0])
            else:
                print("No tables found on Page 1.")
                
    except Exception as e:
        print(f"Parsing Failed: {e}")

if __name__ == "__main__":
    verify_extraction()
