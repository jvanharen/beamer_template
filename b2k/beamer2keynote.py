import os
import glob
import PyPDF2
import argparse
import subprocess
import pdftotext


def recursive_walk(lst, path):
    for root, dirs, files in os.walk(path):
        for file in files:
            lst.append(os.path.join(root, file))
        for dir in dirs:
            recursive_walk(lst, os.path.join(root, dir))


def split_pdf_pages(input_pdf_path, target_dir, fname_fmt=u"{num_page:04d}.pdf"):
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


def run_scpt(scpt, args=[]):
    process = subprocess.Popen(['osascript', scpt] + args,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out, err


parser = argparse.ArgumentParser(
    description='Convert beamer pdf into Keynote.')
parser.add_argument('--in', dest='beamer',  metavar='beamer.pdf',
                    required=True, help='Beamer slides.')
parser.add_argument('--tmp-dir', dest='tmp',  metavar='Temporary directory',
                    required=True, help='Temporary directory to store extracted pdf.')
parser.add_argument('--src-dir', dest='src',  metavar='Sources directory',
                    required=True, help='Sources directory.')

args = parser.parse_args()
split_pdf_pages(args.beamer, args.tmp)
out, err = run_scpt('insert_pdf_pages.scpt', [args.tmp])

movie_list = get_movie_list(args.src)
movie_dict = get_movie_page(args.tmp, movie_list)

for k in movie_dict:
    out, err = run_scpt('insert_movie.scpt', [args.beamer.replace(
        'pdf', 'key'), os.path.join(args.src, movie_dict[k]), str(k)])
