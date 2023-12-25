import sys
import scan_folders
import shutil
import normalize
from pathlib import Path


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize.normalize(path.name))
    

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    # ext = path.suffix
    new_name = normalize.normalize(path.name.split('.')[0])

    # print(path.name, path.name.split('.'), new_name)

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        # print(f'{path} ReadError')
        path.unlink()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        # print(f'{path} FileNotFoundError')
        path.unlink()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            # print(f"  try delete {item}")

            try:
                item.rmdir()
                # print(f'{item} deleted')
            except OSError:
                # print(f'{item} not deleted')
                pass


def main(folder_path):
    
    scan_folders.scan_folder(folder_path)

    for item in scan_folders.result:

        if item not in ('FOLDERS', 'EXT', 'EXT_UNKNOWN', 'ARCHIVES'):
            for file in scan_folders.result[item]:
                handle_file(file, folder_path, item.lower())

    for file in scan_folders.result['ARCHIVES']:
        handle_archive(file, folder_path, 'ARCHIVES'.lower())
    
    remove_empty_folders(folder_path)

    scan_folders.out_log_folder(folder_path)
    

if __name__ == '__main__':
    path = sys.argv[1]
    print(f'Start in {path}')

    folder = Path(path)
    
    main(folder.resolve())
