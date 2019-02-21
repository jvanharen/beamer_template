import os
import cv2
import glob
import shutil
import argparse
import subprocess
import PyPDF2
import pdf2image
import pdftotext
import numpy as np


def recursive_walk(lst, path):
    for root, dirs, files in os.walk(path):
        for file in files:
            lst.append(os.path.join(root, file))
        for dir in dirs:
            recursive_walk(lst, os.path.join(root, dir))


def split_pdf_pages_and_convert_jpg(input_pdf_path, target_dir, fname_fmt=u"{num_page:04d}.pdf"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(input_pdf_path, "rb") as input_stream:
        input_pdf = PyPDF2.PdfFileReader(input_stream)

        if input_pdf.flattenedPages is None:
            input_pdf.getNumPages()

        for num_page, page in enumerate(input_pdf.flattenedPages):
            output = PyPDF2.PdfFileWriter()
            output.addPage(page)

            file_name = os.path.join(
                target_dir, fname_fmt.format(num_page=num_page))
            with open(file_name, "wb") as output_stream:
                output.write(output_stream)
            pages = pdf2image.convert_from_path(file_name, 1000)
            for page in pages:
                page.save(file_name.split('.')[0] + '.jpg', 'JPEG')


def get_movie_page(input_pdf_path, movie_list):
    movie_dict = {}
    for input_pdf in glob.glob(os.path.join(input_pdf_path, '*.pdf')):
        with open(input_pdf, "rb") as input_stream:
            input_pdf_obj = pdftotext.PDF(input_stream)
            for p in input_pdf_obj:
                for j, mov in enumerate(movie_list):
                    if mov.split('/')[-1] in p:
                        movie_dict[int(input_pdf.split(
                            '/')[-1].split('.')[0]) + 1] = mov
    return movie_dict


def get_movie_list(src_dir):
    file_list, movie_list = [], []
    recursive_walk(file_list, src_dir)
    for file in file_list:
        if file.split('.')[-1] == 'tex':
            with open(file, 'r') as fid:
                for line in fid:
                    if '### PYTHON: insert movie' in line:
                        movie_list.append(line.split()[-1])
    return set(movie_list)


def create_html_slides(input_pdf_path, target_dir, src_dir, assets_dir, movie_dict):
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    nbr = 0
    for f in os.listdir(target_dir):
        if f.endswith(".jpg"):
            shutil.copyfile(os.path.join(target_dir, f),
                            os.path.join(assets_dir, f))
            nbr = np.amax([int(f.split('.')[0]), nbr])
    for m in movie_dict:
        shutil.copyfile(os.path.join(src_dir, movie_dict[m]), os.path.join(
            assets_dir, movie_dict[m].split('/')[-1]))
    html_insert = ""
    for i in range(nbr):
        html_insert += 'class: center middle\nbackground-image: url(' + assets_dir + '/' + \
            str(i).rjust(4, '0') + '.jpg)\n'
        if i+1 in movie_dict:
            mov = cv2.VideoCapture(os.path.join(
                assets_dir, movie_dict[i+1].split('/')[-1]))
            h = mov.get(cv2.CAP_PROP_FRAME_HEIGHT)
            w = mov.get(cv2.CAP_PROP_FRAME_WIDTH)
            if w/4. >= h/3.:
                html_insert += '<video preload="auto" width="100%" data-setup="{}" autoplay loop controls><source src="' + \
                    os.path.join(
                        assets_dir, movie_dict[i+1].split('/')[-1]) + '" /></video>\n'
            else:
                html_insert += '<video preload="auto" width="auto" height="' + \
                    str(768*0.7) + '"  data-setup="{}" autoplay loop controls><source src="' + \
                    os.path.join(
                        assets_dir, movie_dict[i+1].split('/')[-1]) + '" /></video>\n'

        html_insert += "---\n"
    html_insert += 'background-image: url(' + assets_dir + '/' + \
        str(nbr).rjust(4, '0') + '.jpg)\n'
    with open('template.html', 'r') as fid:
        html = fid.readlines()
    for i, l in enumerate(html):
        if "textarea" in l:
            html.insert(i+1, html_insert)
            break
    with open('remark.html', 'w') as fid:
        fid.writelines(html)


parser = argparse.ArgumentParser(
    description='Convert beamer pdf into Keynote.')
parser.add_argument('--in', dest='beamer',  metavar='beamer.pdf',
                    required=True, help='Beamer slides.')
parser.add_argument('--tmp-dir', dest='tmp',  metavar='Temporary directory',
                    required=True, help='Temporary directory to store extracted pdf.')
parser.add_argument('--src-dir', dest='src',  metavar='Sources directory',
                    required=True, help='Sources directory.')
parser.add_argument('--assets-dir', dest='assets',  metavar='Assets directory',
                    required=True, help='Assets directory.')


args = parser.parse_args()
split_pdf_pages_and_convert_jpg(args.beamer, args.tmp)
movie_list = get_movie_list(args.src)
movie_dict = get_movie_page(args.tmp, movie_list)
create_html_slides(args.beamer, args.tmp, args.src, args.assets, movie_dict)
