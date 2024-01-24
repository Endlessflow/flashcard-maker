import os
import shutil
import zipfile


def get_base_name(fact_export_dir):
    for file_name in os.listdir(fact_export_dir):
        if file_name.endswith('_anki.txt'):
            return file_name.rsplit('_anki.txt', 1)[0]
    return None


def copy_anki_file_to_output(fact_export_dir, output_dir, base_name):
    anki_file_name = f'{base_name}_anki.txt'
    input_file_path = os.path.join(fact_export_dir, anki_file_name)
    output_file_path = os.path.join(output_dir, anki_file_name)
    shutil.copy(input_file_path, output_file_path)


def rename_backup_pickle(data_dir, base_name):
    input_file_path = os.path.join(data_dir, 'backup.pickle')
    output_file_path = os.path.join(data_dir, f'{base_name}.pickle')
    try:
        shutil.move(input_file_path, output_file_path)
    except FileNotFoundError:
        print("No backup.pickle file found.")
        pass


def compress_data_folder(data_dir, archive_dir, base_name):
    output_file_path = os.path.join(archive_dir, f'{base_name}.zip')
    with zipfile.ZipFile(output_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, data_dir)
                zipf.write(file_path, arcname)


def clean_up(data_dir, output_dir, archive_dir):
    fact_export_dir = os.path.join(data_dir, 'fact_export')
    base_name = get_base_name(fact_export_dir)

    if base_name is not None:
        copy_anki_file_to_output(fact_export_dir, output_dir, base_name)
        rename_backup_pickle(data_dir, base_name)
        compress_data_folder(data_dir, archive_dir, base_name)
    
        # if archivefile successfully created, delete data folder
        if os.path.exists(os.path.join(archive_dir, f'{base_name}.zip')):
            shutil.rmtree(data_dir)
    else:
        print("No base_name found. Cleanup process aborted.")
