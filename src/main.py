import tkinter as tk
from tkinter import filedialog
import subprocess
import shutil
import os

def selectRepository():
    repo_path = filedialog.askdirectory()
    if repo_path:
        print("Selected repository:", repo_path)
        try:
            cli_output = subprocess.run(["git", "status"], cwd=repo_path, capture_output=True, text=True)
            changes = filterChanges(cli_output.stdout)
            storeChanges(changes, repo_path)
        except FileNotFoundError:
            print("Git is not installed or not in the system PATH.")
    else:
        print("No repository selected.")

def filterChanges(status_output):
    lines = status_output.split('\n')
    modified_section = False
    added_section = False
    changes = {}

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("Changes not staged for commit:"):
            modified_section = True
        elif stripped_line.startswith("Untracked files:"):
            modified_section = False
            added_section = True
        elif stripped_line.startswith("no changes added to commit (use"):
            added_section = False
        elif modified_section and stripped_line and not stripped_line.startswith("(use"):
            stripped_line = stripped_line.split()
            changes[stripped_line[1]] = stripped_line[0]
        elif added_section and stripped_line and not stripped_line.startswith("(use"):
            changes[stripped_line] = "added:"

    return changes

def storeChanges(changes, base_path):
    changes_dir = os.path.join(os.getcwd(), "changes")
    os.makedirs(changes_dir, exist_ok=True)
    deleted_files = []

    for relative_file_path in changes:
        if changes[relative_file_path] == "deleted:":
            deleted_files.append(relative_file_path)
            continue
        
        source_file_path = os.path.join(base_path, relative_file_path)
        if os.path.exists(source_file_path):

            if changes[relative_file_path] == "added:":
                try:
                    shutil.copytree(source_file_path, os.path.join(changes_dir, relative_file_path))
                    print(f"Folder '{source_file_path}' copied to '{changes_dir}' successfully.")
                except Exception as e:
                    print(f"An error occurred: {e}")

            elif changes[relative_file_path] == "modified:":
                directory_path = os.path.dirname(relative_file_path)
                store_path = os.path.join(changes_dir, os.path.relpath(directory_path))
                os.makedirs(store_path, exist_ok=True)
                shutil.copy2(source_file_path, store_path)
                print(f"Copied {relative_file_path} to {store_path}")
        else:
            print(f"Error: File {source_file_path} does not exist.")

    with open("dan.txt", "w") as f:
        f.write(base_path + "\n\n Deleted Changes: \n")
        for deleted_file in deleted_files:
            f.write(deleted_file + "\n")

def restoreChanges():
    changes_dir = os.path.join(os.getcwd(), "changes\\")
    restore_dir = ""
    with open("dan.txt", "r") as f:
        restore_dir = f.readline()
        restore_dir = restore_dir.rstrip("\n")
    if os.path.exists(changes_dir):
        try:
            changes_contents = os.listdir(changes_dir)
            if changes_contents:
                source_to_restore = changes_contents[0]
                source_path = os.path.join(changes_dir, source_to_restore)
                destination_path = restore_dir + os.path.relpath(source_path).lstrip("changes")
                shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                print("Changes restored successfully.")
            else:
                print("No changes to restore.")
        except Exception as e:
            print(f"An error occurred while restoring changes: {e}")
    else:
        print("No changes to restore.")

root = tk.Tk()
root.title("Github-Conflict-Resolver")

select_btn = tk.Button(root, text="Select Repository", command=selectRepository)
select_btn.pack(pady=10)

restore_btn = tk.Button(root, text="Restore Changes", command=restoreChanges)
restore_btn.pack(pady=5)

root.mainloop()