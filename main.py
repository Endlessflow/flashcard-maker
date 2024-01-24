import os
import glob
import shutil
from src.fileUtils import convert_pdfs_pages_in_folder
from src.gptHandler import generate_question_per_page_in_folder
from src.aggregator import process_text_files
from src.clean_up import clean_up


def main():
    input_dir = 'input/'
    pdf_dir = 'data/pdf'
    txt_pages_dir = 'data/txt_pages'
    gpt3_replies_dir = 'data/gpt3_replies'
    fact_export_dir = 'data/fact_export'
    output_dir = 'output'
    archive_dir = 'archive'

    # if /data exists, run the usual process once
    if os.path.exists('data/'):
        convert_pdfs_pages_in_folder(pdf_dir, txt_pages_dir)
        generate_question_per_page_in_folder(txt_pages_dir, gpt3_replies_dir)
        process_text_files(gpt3_replies_dir, fact_export_dir)
        clean_up('data', output_dir, archive_dir)

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    # Get all the pdf files in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, '*.pdf'))

    # if pdf_files is empty, exit
    if not pdf_files:
        print('No pdf files found in input directory')
        exit()

    for pdf_file in pdf_files:
        base_name = os.path.basename(pdf_file)
        dest_pdf_file = os.path.join(pdf_dir, base_name)
        # make the pdf_dir if it doesn't exist
        os.makedirs(pdf_dir, exist_ok=True)
        shutil.move(pdf_file, dest_pdf_file)

        convert_pdfs_pages_in_folder(pdf_dir, txt_pages_dir)
        generate_question_per_page_in_folder(txt_pages_dir, gpt3_replies_dir)
        process_text_files(gpt3_replies_dir, fact_export_dir)
        clean_up('data', output_dir, archive_dir)



if __name__ == '__main__':
    main()
