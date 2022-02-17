from typing import Union, List, Set, Dict, Tuple, Optional
import os
import argparse
import pathlib
from PIL import Image, ImageOps, ImageFont, ImageDraw
from PyPDF2 import PdfFileMerger
from datetime import date

# Todos:
# - Separieren bei mehreren Aufgaben
# - Zusammensetzten mehrere PDFs wenn keine Bilder vorhanden sind.
# - Gemischte Ordner Manuelles Mergen ... (vllt dryrun mit warnings?)
# - Log schreiben
# - typing Image
# - better print info
# - input arg für rerun mit liste bestimmer matrk nummern
# - titelseiten (auch für einzelne aufgaben)
# - refractor
# - additional ghostscript compression für finale pdf
# - mehr cmd argumente um alles zu steuern

class dynexite_parser:

    dpi : int = 200
    a4_h : int = 297 # mm
    a4_w : int = 210 #mm
    a4_lr_border : int  = 10 #left right border in mm
    a4_t_border : int = 10
    a4_b_border : int = 15
    inch_to_mm_fac : int  = 25.40
    a4_h_px : int = round(a4_h / inch_to_mm_fac * dpi)
    a4_w_px : int = round(a4_w / inch_to_mm_fac * dpi)
    a4_lr_border_px : int = round(a4_lr_border / inch_to_mm_fac * dpi)
    a4_t_border_px : int = round(a4_t_border / inch_to_mm_fac * dpi)
    a4_b_border_px : int = round(a4_b_border / inch_to_mm_fac * dpi)
    im_max_w : int = a4_w_px - 2 * a4_lr_border_px
    im_max_h : int = a4_h_px - a4_t_border_px - a4_b_border_px

    def __init__(self, folder : Union[str, pathlib.Path]):
        assert(folder.exists())

        gen_submissions_folder = folder / "gen_pdf_submissions"
        gen_submissions_folder.mkdir(exist_ok=True)

        for child in folder.iterdir(): 
            if child.is_dir() and child.name[:5].isdigit() and child.name[6] == "-":
                print(child.name + ":")
                # make temporary path
                tmppath = child / "tmp"
                tmppath.mkdir(exist_ok=True)

                pdfs = []
                pdfs_raw = []

                for child2 in child.iterdir():
                    # print("\t" + child2.name)
                    if child2.name.endswith((".jpg", ".png", ".jpeg")):
                        # print("\t" + child2.name
                        im = Image.open(child2)
                        # print(type(im))
                        # print(im.size)  

                        output_pdf_name = child2.with_suffix(".pdf")
                        output_pdf_name = output_pdf_name.name
                        output_im_pdf = tmppath / output_pdf_name

                        im_scaled = self.image_scale(im)
                        a4im = Image.new('RGB',(self.a4_w_px, self.a4_h_px),(255, 255, 255)) 

                        a4im.paste(im_scaled, box=(self.a4_lr_border_px, self.a4_t_border_px))
                        draw = ImageDraw.Draw(a4im)
                        font = ImageFont.truetype("./assets/fonts/arial.ttf", 36)
                        # draw.text((x, y),"Sample Text",(r,g,b))
                        draw.text((10, 10), str(child2.name), (199,221,242), font=font)
                        a4im.save(output_im_pdf, 'PDF', quality=75)
                        pdfs.append(output_im_pdf)

                    if child2.name.endswith((".pdf")):
                        pdfs.append(child2)
                        pdfs_raw.append(child2.name)

                if pdfs_raw:
                    offset = 20
                    fontsize = 36
                    a4im = Image.new('RGB',(self.a4_w_px, self.a4_h_px),(255, 255, 255)) 
                    draw = ImageDraw.Draw(a4im)
                    font = ImageFont.truetype("./assets/fonts/arial.ttf", 36)
                    draw.text((10, 10), "Raw PDFS appended to this file:", (199,221,242), font=font)

                    for i,pdf_raw in enumerate(pdfs_raw):
                        draw.text((10, (offset+fontsize) * (i+1)), pdf_raw, (199,221,242), font=font)
                    
                    output_im_pdf = tmppath / "pdf_summary.pdf"

                    a4im.save(output_im_pdf, 'PDF', quality=75)
                    pdfs.append(output_im_pdf)

                if pdfs:
                    merger = PdfFileMerger(strict=False)

                    for pdf in pdfs:
                        print(pdf.as_posix())
                        merger.append(pdf.as_posix())

                    respath = gen_submissions_folder / (child.name[:5] + "_result.pdf")

                    merger.write(respath.as_posix())
                    merger.close()
                
                self.rmdir(tmppath.as_posix())



    def image_scale(self, im):
            im_w = im.size[0]
            im_h = im.size[0]
            
            h_scale = self.im_max_h / im_h
            w_scale = self.im_max_w / im_w

            scale = min(h_scale,w_scale)

            return ImageOps.scale(im, scale, resample=3)


    def rmdir(self,directory):
        directory = pathlib.Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                self.rmdir(item)
            else:
                item.unlink()
        directory.rmdir()


parser = argparse.ArgumentParser(description='Parse Input Options')
parser.add_argument('--dynexite-archive', metavar='YXZ', type=pathlib.Path, nargs=1,
                    help='Absolute or relative path to dynexite archive',
                    required=True)
# parser.add_argument('--after-corr-mode', metavar='true/false', type=bool, nargs=1, 
#                     const=False, default=False,
#                     help='Only concats pdfs for same mat no i.e. when seperated for correction via uploadfield no',
#                     required=False)
# parser.add_argument('--corr-folder', metavar='YXZ', type=pathlib.Path, nargs=1
#                     help='Path to corrected pdfs folder',
#                     required='--after-corr-mode')
# parser.add_argument('--compress-pdfs', metavar='true/false', type=bool, nargs=1, 
#                     const=True, default=False,
#                     help='Additional pdf compression via ghostscript after pdf/image concatination',
#                     required=False)
# parser.add_argument('--compress-dpi', metavar='dpival', type=int, nargs=1, 
#                     const=150, default=150,
#                     help='DPI Value for compression',
#                     required=False)
# parser.add_argument('--seperate-upload-fields', metavar='true/false', type=bool, nargs=1, 
#                     const=False, default=False,
#                     help='Multiple PDFs per user per Dynexite uploadfield',
#                     required=False)
# parser.add_argument('--make-title-page', metavar='true/false', type=bool, nargs=1, 
#                     const=False, default=False,
#                     help='Generate title page with title, date and mat no',
#                     required=False)
# parser.add_argument('--title', metavar='TITLE', type=str, nargs=1, 
#                     const="Klausur", default="Klausur",
#                     help='Title for title page',
#                     required=False)
# parser.add_argument('--exam-date', metavar='DATE', type=str, nargs=1, 
#                     const=date.today().strftime("%d.%m.%Y"), 
#                     default=date.today().strftime("%d.%m.%Y"),
#                     help='Exam date for title page(s) and other information',
#                     required=False)
# parser.add_argument('--seperate-upload-fields', metavar='true/false', type=bool, nargs=1, 
#                     const=False, default=False,
#                     help='Multiple PDFs per user per Dynexite uploadfield')
# parser.add_argument('--make-sub-title-pages', metavar='true/false', type=bool, nargs=1, 
#                     const=False, default=False,
#                     help='Generate sub title page(s) with title, date, partno (uploadfield) and mat no',
#                     required=False)
# parser.add_argument('--parse-mat-nums', metavar='123456, ...', type=int, nargs='N',
#                     help='List of matrikel numbers to parse',
#                     required=False)

args = parser.parse_args()

dynexite_parser(args.dynexite_archive[0])
