import sys
from pathlib import Path
import param


result = None

def init_result():
    result = {}
    result['FOLDERS'] = []
    result['EXT'] = set()
    result['EXT_UNKNOWN'] = set()
    for item in param.WORK_FOLDERS:
        result[item] = []

init_result()

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan_folder(folder):
    for item in folder.iterdir():
        
        if item.is_dir():
           
            if item.name.upper() not in param.WORK_FOLDERS:
                result['FOLDERS'].append(item)
                scan_folder(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            result['OTHER'].append(new_name)
        else:
            try:
                result[param.WORK_EXTENTIONS[extension]].append(new_name)
                result['EXT'].add(extension)
            except KeyError:
                result['OTHER'].append(new_name)
                result['EXT_UNKNOWN'].add(extension)


def scan_new_folder(folder):
    init_result()
    for item in param.WORK_FOLDERS:
        ...
    for item in folder.iterdir():
        
        if item.is_dir():
           
            if item.name.upper() in param.WORK_FOLDERS:
                result['FOLDERS'].append(item)
                scan_folder(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            result['OTHER'].append(new_name)
        else:
            try:
                result[param.WORK_EXTENTIONS[extension]].append(new_name)
                result['EXT'].add(extension)
            except KeyError:
                result['OTHER'].append(new_name)
                result['EXT_UNKNOWN'].add(extension)


if __name__ == '__main__':

    path = sys.argv[1]
    print(f"Start in {path}")
    folder = Path(path)

    scan_folder(folder)
    for key, res in result.items():
        print(f'{key}:{res}')

    