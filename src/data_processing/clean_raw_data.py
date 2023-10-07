import os
import configparser


def find_empty_directories(root_dir):
    empty_dirs = []

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            empty_dirs.append(dirpath)

    return empty_dirs


def delete_empty_directories(empty_dirs):
    for dir_path in empty_dirs:
        try:
            os.rmdir(dir_path)
            print(f"Deleted empty directory: {dir_path}")
        except OSError as e:
            print(f"Error deleting directory {dir_path}: {e}")


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Replace with the directory you want to search
    directory_to_search = config.get('PATHS', 'csv_dir')
    empty_directories = find_empty_directories(directory_to_search)

    if empty_directories:
        for dir_path in empty_directories:
            print(dir_path)

        delete_empty_directories(empty_directories)
    else:
        print("No empty directories found.")
