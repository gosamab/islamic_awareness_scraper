import os
import shutil

def find_files_with_restriction(root_dir, restriction_file='dont_copy_please.png'):
    files_to_move = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if restriction_file in filenames:
            for file in filenames:
                if file != restriction_file:
                    full_path = os.path.join(dirpath, file)
                    files_to_move.append(full_path)

    return files_to_move

def move_files(files, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for file_path in files:
        try:
            shutil.move(file_path, destination_folder)
            print(f"Moved: {file_path} to {destination_folder}")
        except Exception as e:
            print(f"Failed to move {file_path}: {e}")

if __name__ == "__main__":
    root_directory = input("Enter the path to the root directory: ")
    destination_folder = input("Enter the path to the destination folder: ")

    files_to_move = find_files_with_restriction(root_directory)

    print("\nMoving files to destination folder...")
    move_files(files_to_move, destination_folder)

    print("\nAll eligible files have been moved.")