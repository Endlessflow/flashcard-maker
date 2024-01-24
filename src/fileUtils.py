import os
import pdfplumber

"""
General Methodes
"""


def open_file(src_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


"""
Get Files from Directory
"""


def get_pdf_files(src_dir):
    files = os.listdir(src_dir)
    pdf_files = [file for file in files if file.endswith('.pdf')]
    return pdf_files


def get_text_files(src_dir):
    text_files = []
    for subdir, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.txt'):
                text_files.append(os.path.join(subdir, file))
    return text_files


"""
Convert PDF to Text
"""


def convert_pdf_to_text(pdf_file):
    content = ''
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                content += f'\n\n\nPAGE {page.page_number}:\n'
                content += page.extract_text()
        print(f'{pdf_file} converted')
    except Exception as error:
        print(error, pdf_file)
    return content.strip()


def convert_pdfs_in_folder(src_dir, dest_dir):
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    pdf_files = get_pdf_files(src_dir)

    for pdf_file in pdf_files:
        print(f'Converting {pdf_file}')
        file_base_name = os.path.splitext(pdf_file)[0].replace(' ', '_')
        content = convert_pdf_to_text(os.path.join(src_dir, pdf_file))
        save_file(os.path.join(dest_dir, f'{file_base_name}.txt'), content)


def convert_pdf_page_to_text(page):
    content = f'PAGE {page.page_number}:\n'
    content += page.extract_text()
    return content.strip()


def convert_pdf_pages_to_text_files(pdf_file, dest_dir):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                content = convert_pdf_page_to_text(page)
                padded_page_number = str(page.page_number).zfill(2)
                page_file_name = f'{os.path.splitext(os.path.basename(pdf_file))[0]}_page{padded_page_number}.txt'
                save_file(os.path.join(dest_dir, page_file_name), content)
        print(f'{pdf_file} pages converted to individual text files')
    except Exception as error:
        print(error, pdf_file)


def convert_pdfs_pages_in_folder(src_dir, dest_dir):
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    pdf_files = get_pdf_files(src_dir)

    for pdf_file in pdf_files:
        print(f'Converting {pdf_file} pages to individual text files')
        convert_pdf_pages_to_text_files(
            os.path.join(src_dir, pdf_file), dest_dir)


"""
Split Text Files
"""


def split_text_by_delimiter(text, chunk_size, delimiter):
    chunks = []
    start_idx = 0
    while start_idx < len(text):
        end_idx = start_idx + chunk_size
        if end_idx < len(text):
            delimiter_idx = text.rfind(delimiter, start_idx, end_idx)
            if delimiter_idx != -1:
                end_idx = delimiter_idx
            else:
                end_idx = min(end_idx, len(text))
        else:
            end_idx = len(text)
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx
    return chunks


def split_text_by_size(text, chunk_size):
    num_chunks = (len(text) // chunk_size) + 1
    chunks = [text[i * chunk_size:(i + 1) * chunk_size]
              for i in range(num_chunks)]
    return chunks


def save_chunks(chunks, file_base_name, dest_dir):
    for i, chunk in enumerate(chunks):
        new_file_name = f"{file_base_name}_part{i+1:02d}.txt"
        new_file_path = os.path.join(dest_dir, new_file_name)

        save_file(new_file_path, chunk)


def split_text_file(src_file, dest_dir, chunk_size=3500, delimiter=None):
    text = open_file(src_file)
    chunks = split_text_by_delimiter(
        text, chunk_size, delimiter) if delimiter else split_text_by_size(text, chunk_size)
    file_base_name = os.path.splitext(os.path.basename(src_file))[0]
    save_chunks(chunks, file_base_name, dest_dir)


def split_text_files_in_folder(src_dir, dest_dir, split=None):
    os.makedirs(dest_dir, exist_ok=True)

    text_files = get_text_files(src_dir)

    for text_file in text_files:
        dest_subdir = os.path.join(dest_dir, os.path.relpath(
            os.path.dirname(text_file), src_dir))
        os.makedirs(dest_subdir, exist_ok=True)
        split_text_file(text_file, dest_subdir, delimiter=split)
