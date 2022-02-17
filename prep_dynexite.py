from typing import Union, List, Set, Dict, Tuple, Optional
import os
import argparse
import pathlib
from PIL import Image, ImageOps, ImageFont, ImageDraw
from wand.image import Image as wimage
from wand.color import Color
from PyPDF2 import PdfFileMerger
from datetime import date
from dynexite_item import dynexite_item
import io
import numpy as np

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

    dynexite_folder : Union[str, pathlib.Path] = "" 
    submission_folder_name : str = "gen_pdf_submissions"
    
    make_title_page : bool = True
    make_subtitle_pages : bool = True
    split_upload_parts : bool = True
    dryrun : bool  = False
    exam_name : str = "Dummy Name"
    exam_date : str = "11.11.1111"

    concat_corr_mode : bool = False
    concat_corr_folder  : Union[str, pathlib.Path] = "" 

    ############################################################################
    # pillow settings:
    # settings for image handling and pdf gen with pillow

    pil_dpi : int = 150
    pil_quality : int = 75 # best quality (default 75)
    pil_a4_h : int = 297 # mm
    pil_a4_w : int = 210 #mm
    pil_a4_lr_border : int  = 10 #left right border in mm
    pil_a4_t_border : int = 10
    pil_a4_b_border : int = 15
    inch_to_mm_fac : float  = 25.40
    pil_a4_h_px : int = round((pil_a4_h / inch_to_mm_fac) * pil_dpi)
    pil_a4_w_px : int = round((pil_a4_w / inch_to_mm_fac) * pil_dpi)
    pil_a4_lr_border_px : int = round((pil_a4_lr_border / inch_to_mm_fac) * pil_dpi)
    pil_a4_t_border_px : int = round((pil_a4_t_border / inch_to_mm_fac) * pil_dpi)
    pil_a4_b_border_px : int = round((pil_a4_b_border / inch_to_mm_fac) * pil_dpi)
    pil_im_max_w : int = pil_a4_w_px - 2 * pil_a4_lr_border_px
    pil_im_max_h : int = pil_a4_h_px - pil_a4_t_border_px - pil_a4_b_border_px

    # default pillow fontsizes
    pil_fontsize_def : int = 24
    pil_fontoffset_def : int = 15
    pil_fontsize_h1 : int = 48
    pil_fontsize_h2 : int = 36

    pil_font_def = ImageFont.truetype("./assets/fonts/arial.ttf", pil_fontsize_def)
    pil_font_h1 = ImageFont.truetype("./assets/fonts/arial.ttf", pil_fontsize_h1)
    pil_font_h2 = ImageFont.truetype("./assets/fonts/arial.ttf", pil_fontsize_h2)

    pil_page_bg_col = (255, 255, 255)
    pil_font_col1 = (199,221,242)
    pil_font_col_b = (0,0,0)
    # pillow settings end
    ############################################################################

    def __init__(self, args):

        if args.dynexite_archive != pathlib.Path(''):
            self.dynexite_folder = args.dynexite_archive[0]

        self.dryrun = self.set_bool_from_str_arg(args.dryrun[0], self.dryrun)

        self.concat_corr_mode = self.set_bool_from_str_arg(args.after_corr_mode[0], 
                self.concat_corr_mode)
    
        if self.concat_corr_mode and args.corr_folder == pathlib.Path(''):
            assert(1==2)
        elif self.concat_corr_mode:
            self.concat_corr_folder = args.corr_folder[0]

        self.exam_name = args.exam_title[0]
        self.exam_date = args.exam_date[0]
        self.make_title_page = self.set_bool_from_str_arg(args.make_title_page[0],
                self.make_title_page)
        self.make_subtitle_pages = self.set_bool_from_str_arg(args.make_sub_title_pages[0],
                self.make_subtitle_pages)
        self.split_upload_parts = self.set_bool_from_str_arg(args.seperate_upload_fields[0],
                self.split_upload_parts)
        self.pil_dpi = args.dpi


    def main(self):
        if self.concat_corr_mode:
            self.concat_results_pdfs()
        else:
            self.dynexite_concat_pdf_export()


    def concat_results_pdfs(self):
        assert(self.concat_corr_folder.exists() and self.concat_corr_folder.is_dir())
        print("After corr mode (--after-corr-mode yes) enabled. Tyring to concatinate pdfs in folder: " + self.concat_corr_folder.as_posix())
        
        concat_dir = self.concat_corr_folder / "pdf_concats"
        if not self.dryrun:
            concat_dir.mkdir(exist_ok=True)
        
        i = 0
        mat_no = ""
        pdfs_to_merge_stack = []
 
        for file in self.concat_corr_folder.iterdir():
            if file.is_file() and file.name[:6].isdigit() and file.name.endswith(".pdf"):
            
                print("Processing: " + file.name + "...")
                if i > 0 and mat_no != file.name[:6]:
                    self.py2pdf_merge_list_of_pdfs(mat_no, pdfs_to_merge_stack, concat_dir )
                    pdfs_to_merge_stack.clear()
                    i = 0

                mat_no = file.name[:6]
                pdfs_to_merge_stack.append(file)
        
                i = i+1
                    
        if pdfs_to_merge_stack:
            self.py2pdf_merge_list_of_pdfs(mat_no, pdfs_to_merge_stack, concat_dir)


    def dynexite_concat_pdf_export(self):
        assert(self.dynexite_folder.exists())
        print("Starting dynexite export to (single) pdf in folder: " 
                + self.dynexite_folder.as_posix() + "\n")

        gen_submissions_folder = self.dynexite_folder / self.submission_folder_name
        if not self.dryrun:
            gen_submissions_folder.mkdir(exist_ok=True)

        for child in self.dynexite_folder.iterdir(): 
            if child.is_dir() and child.name[:6].isdigit() and child.name[6] == "-":

                student_subfolder = child
                mat_no = student_subfolder.name[:6]

                print("Processing: " + student_subfolder.name + "...")
                # make temporary path
                tmppath = student_subfolder / "tmp"

                if not self.dryrun:
                    tmppath.mkdir(exist_ok=True)

                print("\tGenerated .tmp folder inside " + student_subfolder.as_posix())

                pdfs = []
                pdfs_raw = []
                item_upload_no = []
                item_desc = []

                if self.make_title_page:
                    item_upload_no.append(0)
                    item_desc.append("Title-page")
                    pdfs.append(self.pil_title_page(mat_no, self.exam_name, self.exam_date, tmppath))

                for student_item in student_subfolder.iterdir():

                    if student_item.is_file():
                        di = dynexite_item(student_item)

                        if (di.upload_field_no not in item_upload_no) and self.make_subtitle_pages:
                            item_desc.append("Sub-title-page")
                            pdfs.append(self.pil_title_page(mat_no, self.exam_name, self.exam_date, tmppath, "Upload field "+ str(di.upload_field_no)))
                            item_upload_no.append(di.upload_field_no)
    

                    if student_item.is_file() and student_item.name.endswith((".jpg", ".png", ".jpeg")):
                        output_tmp_pdf_name = student_item.with_suffix(".pdf")
                        output_tmp_pdf_name = output_tmp_pdf_name.name
                        output_tmp_im_pdf = tmppath / output_tmp_pdf_name

                        self.pil_image_to_pdf(student_item, output_tmp_im_pdf)

                        pdfs.append(output_tmp_im_pdf)
                        item_upload_no.append(di.upload_field_no)
                        item_desc.append("Item")

                    if student_item.is_file() and student_item.name.endswith((".pdf")):

                        PDFfile = wimage(filename = student_item, resolution = 300)
                        i = 0
                        print("\tConverting "+str(len(PDFfile.sequence)) + " pages of PDF " + student_item.name + " to imgPDF: ")
                        for (img_id, img) in enumerate(PDFfile.sequence):
                            wimg = wimage(image = img)
                            wimg.background_color = Color("white")
                            wimg.alpha_channel = False
                            blob = wimg.make_blob(format="jpg")
                            img_buffer = np.asarray(bytearray(blob), dtype='uint8')
                            bytesio = io.BytesIO(img_buffer)
                            pil_img = Image.open(bytesio)
                            pil_im_scaled = self.pil_image_scale(pil_img)
                            pil_a4im = Image.new('RGB',(self.pil_a4_w_px, self.pil_a4_h_px), 
                                    self.pil_page_bg_col) 

                            pil_a4im.paste(pil_im_scaled, box=(self.pil_a4_lr_border_px, self.pil_a4_t_border_px))
                            pil_draw = ImageDraw.Draw(pil_a4im)
                            
                            # draw.text((x, y),"Sample Text",(r,g,b))
                            pil_draw.text((10, 10), "from: " +str(student_item.name) + " Page: "  + str(img_id+1), self.pil_font_col1, font=self.pil_font_def)

                            output_tmp_im_pdf = tmppath / (student_item.with_suffix("").name + "_" + str(img_id) + ".pdf")
                            pil_a4im.save(output_tmp_im_pdf, 'PDF', quality=self.pil_quality)

                            pdfs.append(output_tmp_im_pdf)
                            item_upload_no.append(di.upload_field_no)
                            item_desc.append("Item")

                            print("\t\t" + str(img_id+1) + ". Writing: .../tmp/",output_tmp_im_pdf.name)
                            i+=1


                if pdfs and not self.split_upload_parts:
                    self.py2pdf_merge_list_of_pdfs(mat_no, pdfs, gen_submissions_folder)

                elif pdfs and self.split_upload_parts:
                    stack_print_pdfs =  []
                    current_no = item_upload_no[0]
                    assert(len(pdfs) == len(item_upload_no))
                    assert(len(pdfs) == len(item_desc))

                    for (i_pdf, pdf) in enumerate(pdfs):
                        if item_upload_no[i_pdf] == current_no:
                            stack_print_pdfs.append(pdf)
                        else:
                            self.py2pdf_merge_list_of_pdfs(mat_no, stack_print_pdfs, gen_submissions_folder, current_no)
                            stack_print_pdfs.clear()
                            stack_print_pdfs.append(pdf)
                            current_no = item_upload_no[i_pdf]
                
                    self.py2pdf_merge_list_of_pdfs(mat_no, stack_print_pdfs, gen_submissions_folder, current_no)

                if not self.dryrun:
                    self.rmdir(tmppath.as_posix())
                print("\tTemp dir (.../tmp) " + tmppath.as_posix() + " removed")


    def set_bool_from_str_arg(self, str_arg : str, defval : bool):
        if str_arg.lower() in {'yes', 'true', 'y'}:
            return True
        elif str_arg.lower() in {'no', 'false', 'n'}:
            return False
        else:
            return defval

    def pil_image_to_pdf(self, image_file : Union[str, pathlib.Path], 
            output_pdf : Union[str, pathlib.Path]):

        if not self.dryrun:
            pil_im = Image.open(image_file)
            pil_im = self.remove_transparency(pil_im)
            pil_im_scaled = self.pil_image_scale(pil_im)
            pil_a4im = Image.new('RGB',(self.pil_a4_w_px, self.pil_a4_h_px), 
                    self.pil_page_bg_col) 

            pil_a4im.paste(pil_im_scaled, box=(self.pil_a4_lr_border_px, self.pil_a4_t_border_px))
            pil_draw = ImageDraw.Draw(pil_a4im)
            
            # draw.text((x, y),"Sample Text",(r,g,b))
            pil_draw.text((10, 10), str(image_file.name), self.pil_font_col1, font=self.pil_font_def)
            pil_a4im.save(output_pdf, 'PDF', quality=self.pil_quality)
        
        print("\tWritten tmp pdf: .../tmp/" + output_pdf.name + 
                "\n\t\tfrom image: " + image_file.name)


    def pil_student_pdf_summary(self, raw_pdf_list : List[str], 
            output_path : Union[str, pathlib.Path]):
    
        output_im_pdf = output_path / "pdf_summary.pdf"

        if not self.dryrun:
            pil_a4im = Image.new('RGB',(self.pil_a4_w_px, self.pil_a4_h_px), 
                    self.pil_page_bg_col) 
            draw = ImageDraw.Draw(pil_a4im)
            draw.text((10, 10), "Raw PDFS appended to this file:", self.pil_font_col1, 
            font=self.pil_font_def)

            for i,pdf_raw in enumerate(raw_pdf_list):
                draw.text((10, (self.pil_fontoffset_def+self.pil_fontsize_def) * (i+1)),
                        pdf_raw, self.pil_font_col1, font=self.pil_font_def)

            pil_a4im.save(output_im_pdf, 'PDF', quality=self.pil_quality)
        
        print("\tGenerated pdf concat summary: .../tmp/" + output_im_pdf.name)
        return output_im_pdf

    def pil_title_page(self, mat_no : str, title : str, date : str,
        output_path : Union[str, pathlib.Path], subtitle : str = ""):

        title_file = str(title.replace(' ','_') + subtitle.replace(' ','_'))
        output_im_pdf = output_path / str("pdf_" + title_file + "_title_page.pdf")

        if not self.dryrun:
            pil_a4im = Image.new('RGB',(self.pil_a4_w_px, self.pil_a4_h_px), 
                    self.pil_page_bg_col) 
            draw = ImageDraw.Draw(pil_a4im)
            offset = round(self.pil_a4_h_px / 2 - self.pil_fontoffset_def - 1.5 * self.pil_fontsize_h1)
            draw.text((self.pil_a4_lr_border_px, offset), 
                    title, self.pil_font_col_b, font=self.pil_font_h1)
            offset = offset + self.pil_fontsize_h1 + self.pil_fontoffset_def
            draw.text((self.pil_a4_lr_border_px, offset), 
                    subtitle, self.pil_font_col_b, font=self.pil_font_h2)
            offset = offset + self.pil_fontsize_h2 + self.pil_fontoffset_def
            draw.text((self.pil_a4_lr_border_px, offset), 
                    date, self.pil_font_col_b, font=self.pil_font_h2)
            offset = offset + self.pil_fontsize_h2 + self.pil_fontoffset_def
            draw.text((self.pil_a4_lr_border_px, offset), 
                    mat_no, self.pil_font_col_b, font=self.pil_font_def)

            pil_a4im.save(output_im_pdf, 'PDF', quality=self.pil_quality)
        
        print("\tGenerated pdf titlepage: .../tmp/" + output_im_pdf.name)
        return output_im_pdf

    def pil_image_scale(self, im):
        im_w = im.size[0]
        im_h = im.size[0]
        
        h_scale = self.pil_im_max_h / im_h
        w_scale = self.pil_im_max_w / im_w

        scale = min(h_scale,w_scale)

        return ImageOps.scale(im, scale, resample=Image.LANCZOS)


    def py2pdf_merge_list_of_pdfs(self, 
            filename_pref : str, 
            list_of_pdfs : List[Union[str, pathlib.Path]],
            output_path : Union[str, pathlib.Path],
            splitpart : int = -1):
        print("\tNow merging all (tmp) pdf files:")

        if not self.dryrun:
            py2pdf_merger = PdfFileMerger(strict=False)

        for pdf in list_of_pdfs:
            print("\t\t" + pdf.as_posix())
            if not self.dryrun:
                py2pdf_merger.append(pdf.as_posix())

        if splitpart  == -1:
            output_pdf = output_path / (filename_pref + "_result.pdf")
        else:
            output_pdf = output_path / (filename_pref + "_result_"+str(splitpart)+".pdf")

        if not self.dryrun:
            py2pdf_merger.write(output_pdf.as_posix())
            py2pdf_merger.close()
    
        print("\tMerged pdf " + output_pdf.as_posix() + " written")


    def rmdir(self,directory):
        directory = pathlib.Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                self.rmdir(item)
            else:
                item.unlink()
        directory.rmdir()


    def remove_transparency(self, pil_im, bg_colour=pil_page_bg_col):
        """
        from RWTH exam scan
        Correct transparent image turning black issue

        Args:
            im (PIL.Image.Image): pdf page image
            bg_colour (tuple): background color white code

        Returns:
            PIL.Image.Image: corrected image when the image is transparent
            else just return the pdf page image
        """

        if (pil_im.mode in ('RGBA', 'LA')) or (pil_im.mode == 'P' and
                                        'transparency' in im.info):
            alpha = pil_im.convert('RGBA').split()[-1]
            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format
            bg = Image.new("RGBA", pil_im.size, bg_colour + (255,))
            bg.paste(pil_im, mask=alpha)
            return bg
        else:
            return pil_im



parser = argparse.ArgumentParser(description='Parse Input Options')
parser.add_argument('--dynexite-archive', metavar='YXZ', type=pathlib.Path, nargs=1,
                    default=pathlib.Path(''),
                    help='Absolute or relative path to dynexite archive',
                    required=False)
parser.add_argument('--dryrun', metavar='true/false', type=str, nargs=1, default="No",
                    help='Perform dryrun',
                    required=False)
parser.add_argument('--after-corr-mode', type=str, nargs=1, default="No", 
                    help='Only concats pdfs for same mat no i.e. when seperated for correction via uploadfield no',
                    required=False)
parser.add_argument('--corr-folder', metavar='YXZ', type=pathlib.Path, nargs=1, 
                    default=pathlib.Path(''),
                    help='Path to corrected pdfs folder',
                    required=False)
parser.add_argument('--dpi', metavar='dpival', type=int, nargs=1, default=150,
                    help='DPI Value for compression',
                    required=False)
parser.add_argument('--seperate-upload-fields', metavar='true/false', type=str, nargs=1, default="No",
                    help='Multiple PDFs per user per Dynexite uploadfield',
                    required=False)
parser.add_argument('--make-title-page', metavar='true/false', type=str, nargs=1, default="No",
                    help='Generate title page with title, date and mat no',
                    required=False)
parser.add_argument('--exam-title', metavar='TITLE', type=str, nargs=1, default="PA Dummy",
                    help='Title for title page',
                    required=False)
parser.add_argument('--exam-date', metavar='DATE', type=str, nargs=1, 
                    default=date.today().strftime("%d.%m.%Y"),
                    help='Exam date for title page(s) and other information',
                    required=False)
parser.add_argument('--make-sub-title-pages', metavar='true/false', type=str, nargs=1, default="No",
                    help='Generate sub title page(s) with title, date, partno (uploadfield) and mat no',
                    required=False)
# parser.add_argument('--parse-mat-nums', metavar='123456, ...', type=int, nargs='N',
#                     help='List of matrikel numbers to parse',
#                     required=False)

args = parser.parse_args()

dyn = dynexite_parser(args)
dyn.main()
