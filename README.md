# Example Usage

```shell
python3 prep_dynexite.py --dynexite-archive "./tests/archive-c7olpq0ol3qvagd65aig-2022-02-11"
```

# Simulationstechnik


## Verteilen
```shell
python3 prep_dynexite.py --dynexite-archive "./tests/archive-c7olpq0ol3qvagd65aig-2022-02-11" --make-title-page y --make-sub-title-pages y --seperate-upload-fields y --exam-title "PR Simulationtechnik WS21_22" --exam-date "11.02.2022" 2>&1 > log_dynexite_pdf_concat.txt
```

## Mergen
```shell
python3 prep_dynexite.py --after-corr-mode y --corr-folder "./tests/archive-c7olpq0ol3qvagd65aig-2022-02-11/gen_pdf_submissions" 2>&1 > log_dynexite_corrected_pdfs_concat.txt
```


## Wasserzeichen und PW