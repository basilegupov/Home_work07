import re
import sys
import shutil
from pathlib import Path

# import param

UKR_SYM = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k",
               "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, val in zip(UKR_SYM, TRANSLATION):
    TRANS[ord(key)] = val
    TRANS[ord(key.upper())] = val.upper()


def normalize(name: str) -> str:
    name, *ext = name.split('.')
    name = name.translate(TRANS)
    name = re.sub(r'\W', '_', name)
    if len(ext) == 0:
        return name
    return f"{name}.{'.'.join(ext)}"


def get_params(file_ini='param.ini'):
    file_ini = Path(file_ini)
    res_out = {}
    with open(file_ini, 'r') as file:
        for line in file:

            if len(line.strip()) > 0:
                if line.strip()[0] == '#' or line.strip()[0] == ';':
                    continue
                fold, extend = line.strip().split(':')
                extend = extend.strip().split(',')

                for ext in extend:
                    res_out[ext.strip().upper()] = str(fold).strip().upper()
    return res_out


try:
    WORK_EXTENSIONS = get_params()
except FileNotFoundError:
#     WORK_EXTENSIONS = {}
#
# if len(WORK_EXTENSIONS) == 0:
    WORK_EXTENSIONS = {
        'JPEG': 'IMAGES', 'PNG': 'IMAGES', 'JPG': 'IMAGES', 'SVG': 'IMAGES',
        'AVI': 'VIDEO', 'MP4': 'VIDEO', 'MOV': 'VIDEO', 'MKV': 'VIDEO',
        'DOC': 'DOCUMENTS', 'DOCX': 'DOCUMENTS', 'TXT': 'DOCUMENTS',
        'PDF': 'DOCUMENTS', 'XLSX': 'DOCUMENTS', 'PPTX': 'DOCUMENTS',
        'MP3': 'AUDIO', 'OGG': 'AUDIO', 'WAV': 'AUDIO', 'AMR': 'AUDIO',
        'ZIP': 'ARCHIVES', 'GZ': 'ARCHIVES', 'TAR': 'ARCHIVES',
        '*': 'OTHER'}

WORK_FOLDERS = set([fold.lower() for ext, fold in WORK_EXTENSIONS.items()])

result = {}


def init_result():
    global result

    result = {'FOLDERS': [], 'EXT': set(), 'EXT_UNKNOWN': set()}
    for item in WORK_FOLDERS:
        result[item.upper()] = []
    return 'Ok'


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan_folder_rec(folder_wrk):
    for item in folder_wrk.iterdir():

        if item.is_dir():

            # if item.name.upper() not in param.WORK_FOLDERS:
            if item.name.upper() not in WORK_FOLDERS:
                result['FOLDERS'].append(item)
                scan_folder_rec(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder_wrk / item.name
        if not extension:
            result['OTHER'].append(new_name)
        else:
            try:
                result[WORK_EXTENSIONS[extension]].append(new_name)
                result['EXT'].add(extension)
            except KeyError:
                result['OTHER'].append(new_name)
                result['EXT_UNKNOWN'].add(extension)


def scan_folder(folder_wrk):
    init_result()
    scan_folder_rec(folder_wrk)


def out_log_folder_rec(folder_wrk):
    for item in folder_wrk.iterdir():

        if item.is_dir():

            if item.name in WORK_FOLDERS and item.name.upper() != 'ARCHIVES':
                result['FOLDERS'].append(item)
                out_log_folder_rec(item)

            continue

        extension = get_extensions(file_name=item.name)
        new_name = item.name

        if not extension:
            result['OTHER'].append(new_name)
        else:
            try:
                result[WORK_EXTENSIONS[extension]].append(new_name)
                result['EXT'].add(extension)
            except KeyError:
                result['OTHER'].append(new_name)
                result['EXT_UNKNOWN'].add(extension)


def out_log_folder(folder_wrk, file_log='scan.log'):
    init_result()
    out_log_folder_rec(folder_wrk)
    items = [item for item in result]
    with open(file_log, 'w') as f_out:

        for item in items:

            if item != 'ARCHIVES' and item != 'FOLDERS':

                f_out.write(f'{item}:\n')

                for file in result[item]:
                    f_out.write(f'  {file}\n')


def handle_file(path_in, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path_in.replace(target_folder / normalize(path_in.name))


def handle_archive(path_in, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    new_name = normalize(path_in.name.split('.')[0])

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path_in.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        # print(f'{path} ReadError')
        path_in.unlink()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        # print(f'{path} FileNotFoundError')
        path_in.unlink()
        return
    path_in.unlink()


def remove_empty_folders(path_in):
    for item in path_in.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            # print(f"  try delete {item}")

            try:
                item.rmdir()
                # print(f'{item} deleted')
            except OSError:
                # print(f'{item} not deleted')
                pass


def main():
    if len(sys.argv) < 2:
        print('Usage: clean-folder path')
        return
    path = sys.argv[1]
    print(f"Start clean in {path}")
    folder_path = Path(path)

    scan_folder(folder_path)

    for item in result:
        if item not in ('FOLDERS', 'EXT', 'EXT_UNKNOWN', 'ARCHIVES'):
            for file in result[item]:
                handle_file(file, folder_path, item.lower())

    for file in result['ARCHIVES']:
        handle_archive(file, folder_path, 'ARCHIVES'.lower())

    remove_empty_folders(folder_path)

    out_log_folder(folder_path)


if __name__ == '__main__':
    main()
