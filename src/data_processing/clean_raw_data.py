import os
import configparser


def find_empty_directories(root_dir):
    '''
    Find empty directories in the given root directory.

    Args:
        root_dir (str): The root directory to search for empty directories.

    Returns:
        A list of empty directories found in the root directory.
    '''
    empty_dirs = []

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            empty_dirs.append(dirpath)

    return empty_dirs


def delete_empty_directories(empty_dirs):
    '''
    Deletes the empty directories specified in the input list.

    Parameters:
    empty_dirs (list of str): A list of paths to empty directories.

    Returns:
    None
    '''
    for dir_path in empty_dirs:
        try:
            os.rmdir(dir_path)
            print(f"Deleted empty directory: {dir_path}")
        except OSError as e:
            print(f"Error deleting directory {dir_path}: {e}")


def main():
    '''
    This function searches for empty directories in a specified directory and deletes them.
    It reads the directory path from a configuration file named 'config.ini' located in the same directory as this script.
    The directory path should be specified under the 'PATHS' section with the key 'csv_dir'.
    '''
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


if __name__ == "__main__":
    main()
