# Dynexite Preparation

Python Script to merge students uploads from RWTH Dynexite export. 
Changes in export folder structure may break this.

# Deps

Disclaimer:
> Only tested on Ubuntu 20.04 (Linux)

## Third party deps

- Python3 (should come with every modern Linux distribution)
- Pip
- Poppler Utils
- Ghoscript

Install dependencies with (command may vary on other Linux distributions)
```shell
sudo apt install python3-pip
sudo apt install poppler-utils
sudo apt install ghostscript
```

Install python packages from project folder with:
```shell
pip install -r requirements.txt
```

# Example usage

```shell
python3 prep_dynexite.py --dynexite-archive "./dynexite/archive-path/..." --make-title-page y --exam-title "Exam Python Fundamentals WS21_22" --exam-date "22.02.2022" > log.txt 2>&1
```


# Help
```
$python3 prep_dynexite.py -h

optional arguments:
  -h, --help            show this help message and exit
  --dynexite-archive YXZ
                        Absolute or relative path to dynexite archive
  --dryrun true/false   Perform dryrun
  --after-corr-mode AFTER_CORR_MODE
                        Only concats pdfs for same matrikel number i.e. when seperated for
                        correction via uploadfield no
  --corr-folder YXZ     Path to corrected pdfs folder
  --dpi dpival          DPI value for compression
  --seperate-upload-fields true/false
                        Multiple PDFs per user per Dynexite uploadfield
  --make-title-page true/false
                        Generate title page with title, date and matrikel number
  --exam-title TITLE    Title for title page
  --exam-date DATE      Exam date for title page(s) and other information
  --make-sub-title-pages true/false
                        Generate sub title page(s) with title, date, partno (uploadfield) and
                        matrikel numbers
  --parse-mat-nums 123456 234567 ... [123456 234567 ... ...]
                        Specify a list of matrikel numbers to parse
```




