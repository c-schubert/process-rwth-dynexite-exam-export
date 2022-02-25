# Dynexite Preparation

Python Script to merge students uploads from RWTH Dynexite export. 
Changes in export folder structure may break this.

# Deps

Disclaimer:
> Tested with Ubuntu 20.04 (Linux/WSL)

## Third party deps

- Python3 (should come with every modern Linux distribution)
- Pip
- Poppler Utils
- Ghoscript
- ImageMagick
- (Python3-venc)

# Install deps

0. Use recent Version of Ubuntu i.e. with WSL on Windows

1. Install dependencies with (command may vary on other Linux distributions)
```shell
sudo apt install python3-pip
sudo apt install poppler-utils
sudo apt install ghostscript
sudo apt install libmagickwand-dev
sudo apt install python3-venv
```

2. (if necessary) Fix potential Imagemagick bug:

Replace line `<policy domain="coder" rights="none" pattern="PDF"/>` in file `/etc/ImageMagick-6/policy.xml` by `<policy domain="coder" rights="read|write" pattern="PDF" />`


3. (optional) Switch to project folder and make virtual environment:
```shell
python3 -m venv "env"
```

4. Install python packages from project folder with:
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

usage: prep_dynexite.py [-h] --dynexite-archive YXZ [--dryrun true/false]
                        [--after-corr-mode AFTER_CORR_MODE] [--corr-folder YXZ]      
                        [--dpi dpival] [--separate-upload-fields true/false]
                        [--make-title-page true/false] [--exam-title TITLE]
                        [--exam-date DATE] [--make-sub-title-pages true/false]       
                        [--parse-mat-nums 123456 234567 ... [123456 234567 ... ...]] 
                        [--exclude-mat-nums 123456 234567 ... [123456 234567 ... ...]]
                        [--rotate 90]

Parse Input Options

required arguments:
  --dynexite-archive YXZ
                        Absolute or relative path to dynexite archive

optional arguments:
  -h, --help            show this help message and exit

  --dryrun true/false   Perform dryrun
  --after-corr-mode AFTER_CORR_MODE
                        Only concats pdfs for same matrikel number i.e. when
                        separated for correction via upload field no (Default =      
                        False)
  --corr-folder YXZ     Path to corrected pdfs folder (Must be defined for after-    
                        corr-mode == True)
  --dpi dpival          DPI value for compression (Default = 150)
  --separate-upload-fields true/false
                        Multiple PDFs per user per Dynexite upload field (Default =  
                        False)
  --make-title-page true/false
                        Generate title page with title, date and matrikel number     
                        (Default = False)
  --exam-title TITLE    Title for title page (Default = PA Dummy)
  --exam-date DATE      Exam date for title page(s) and other information (Default   
                        = Today ...)
  --make-sub-title-pages true/false
                        Generate sub title page(s) with title, date, partno
                        (uploadfield) and matrikel numbers (Default = False)
  --parse-mat-nums 123456 234567 ... [123456 234567 ... ...]
                        Specify a list of matrikel numbers to parse
  --exclude-mat-nums 123456 234567 ... [123456 234567 ... ...]
                        Specify a list of matrikel numbers to exclude from parsing   
  --rotate 90           Specify a rotation for images/pdfs to parse (90/180/270      
                        only, Default = 0)
```




