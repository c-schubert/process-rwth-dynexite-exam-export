import subprocess
import pathlib

# can be used to remove OCR generated Text in PDF which may make trouble with the
# prep_dynexite.py script.

# ghostscipt needed!

# Copy script to folder with faulted pdfs and run:
# $python3 remove_pdf_text.py

# Check and remove original pdfs and script from that folder
# rerun prep_dynexite.py script for that folder (matno)


mypath = pathlib.Path(".")

for file in mypath.iterdir():
    if file.is_file() and file.suffix == ".pdf":
        subprocess.run(["gs", "-o", (file.name+"_no_text.pdf"), "-sDEVICE=pdfwrite", "-dFILTERTEXT",  file.name ])