import os
import shutil
import sys
from pathlib import Path


# Keeping the extension groups in one place makes it easy to add or adjust
# categories without changing the file-moving logic.
EXTENSION_FOLDERS = {
    "Documents": {".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".html",
        ".css",
        ".json",
        ".xml",
    },
}


def get_category(filename):
    """Choose a destination category from a file's lowercase extension."""

    extension = Path(filename).suffix.lower()

    for category, extensions in EXTENSION_FOLDERS.items():
        if extension in extensions:
            return category

    # Unknown extensions are kept together rather than left in an unrecognized state.
    return "Other"


def get_available_destination(destination_directory, filename):
    """Find a free destination name so an existing file is never overwritten."""

    candidate = destination_directory / filename
    original = Path(filename)
    number = 1

    while candidate.exists():
        # Appending a number preserves both the base name and original extension.
        candidate = destination_directory / (
            f"{original.stem}_{number}{original.suffix}"
        )
        number += 1

    return candidate


def find_files(directory):
    """Walk through a directory and yield files, excluding existing category folders."""

    category_names = set(EXTENSION_FOLDERS)
    category_names.add("Other")

    for root, directories, filenames in os.walk(directory):
        # Category folders are already organized, and hidden folders are left alone.
        directories[:] = [
            name
            for name in directories
            if name not in category_names and not name.startswith(".")
        ]

        for filename in filenames:
            yield os.path.join(root, filename)


def organize_directory(directory):
    """Organize a directory tree and print a formatted execution summary."""

    directory = Path(directory).expanduser().resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    inspected = 0
    relocated = 0
    skipped = 0
    script_path = Path(__file__).resolve()

    for source_name in find_files(directory):
        source = Path(source_name)

        # Count and track every file we encounter, including one that cannot be moved.
        inspected += 1

        if source.resolve() == script_path:
            skipped += 1
            print(f"Skipped organizer script: {source}")
            continue

        category = get_category(source.name)
        destination_directory = directory / category
        destination_directory.mkdir(exist_ok=True)

        destination = get_available_destination(destination_directory, source.name)

        try:
            # shutil.move can also move a file when the source and destination
            # are on different drives or file systems.
            shutil.move(str(source), str(destination))
            relocated += 1
            print(f"Moved: {source} -> {destination}")
        except FileExistsError:
            skipped += 1
            print(f"Skipped existing file: {source}")
        except PermissionError:
            skipped += 1
            print(f"Permission denied: {source}")
        except OSError as error:
            skipped += 1
            print(f"Could not move {source}: {error}")

    print("\n" + "=" * 38)
    print("EXECUTION SUMMARY")
    print("=" * 38)
    print(f"Total files inspected : {inspected}")
    print(f"Files relocated       : {relocated}")
    print(f"Files skipped         : {skipped}")


def main():
    """Read the optional command-line directory and run the organizer."""

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Downloads is the sensible default for a desktop automation utility.
        directory = os.path.join(os.path.expanduser("~"), "Downloads")

    print(f"Organizing directory: {directory}")

    try:
        organize_directory(directory)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
    except PermissionError as error:
        print(f"Permission denied while accessing the directory: {error}")


if __name__ == "__main__":
    main()