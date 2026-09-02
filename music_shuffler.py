import os
import re
import shutil
import heapq
import random


from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD
from mutagen import File

# Supported music file formats
MUSIC_EXTENSIONS = (
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".wav",
    ".wma",
)


# Application translations
TEXT = {
    "English": {
        "window_title": "Music Reorder",
        "title": "Music Reorder",
        "language": "Language",
        "description": (
            "Select your music folder or drag and drop it here.\n"
            "Your songs will be copied to a new folder and rearranged "
            "to keep songs from the same artist apart whenever possible."
        ),
        "browse": "Browse...",
        "start": "Reorder and Copy Music",
        "ready": "Ready",
        "processing": "Reading your music and creating a new order...",
        "done": "Done! {count} songs have been processed.",
        "select_folder_title": "Select Your Music Folder",
        "no_folder_title": "No Folder Selected",
        "no_folder_message": (
            "Please select your music folder or drag and drop it here."
        ),
        "finished_title": "All Done",
        "finished_message": (
            "{count} songs have been successfully processed.\n\n"
            "Output folder:\n{folder}"
        ),
        "error_title": "Something Went Wrong",
        "error_status": "Something went wrong.",
        "invalid_folder": ("The selected folder could not be found."),
        "no_music_files": ("No supported music files were found in this folder."),
        "unknown_artist": "Unknown Artist",
    },
    "فارسی": {
        "window_title": "تغییر ترتیب آهنگ‌ها",
        "title": "تغییر ترتیب آهنگ‌ها",
        "language": "زبان",
        "description": (
            "کنید Drag & Drop پوشه آهنگ‌ها را انتخاب یا آن را "
            "\n"
            "آهنگ‌ها در پوشه‌ای جدید کپی شده و ترتیب آنها "
            "تغییر می‌کند تا حد امکان دو آهنگ "
            "از یک خواننده پشت هم نباشند"
        ),
        "browse": "...انتخاب پوشه",
        "start": "تغییر ترتیب و کپی آهنگ‌ها",
        "ready": "آماده",
        "processing": "...در حال خواندن اطلاعات آهنگ‌ها و ایجاد ترتیب جدید",
        "done": "انجام شد! تعداد {count} آهنگ پردازش شد",
        "select_folder_title": "پوشه آهنگ‌ها را انتخاب کنید",
        "no_folder_title": "پوشه‌ای انتخاب نشده است",
        "no_folder_message": "کنید Drag & Drop پوشه آهنگ‌ها را انتخاب یا آن را ",
        "finished_title": "اتمام عملیات",
        "finished_message": (
            "تعداد {count} آهنگ با موفقیت پردازش شد\n\n" "پوشه خروجی:\n{folder}"
        ),
        "error_title": "خطا",
        "error_status": "خطایی رخ داد",
        "invalid_folder": "پوشه انتخاب‌شده وجود ندارد",
        "no_music_files": "هیچ فایل صوتی قابل پردازشی در این پوشه پیدا نشد",
        "unknown_artist": "خواننده نامشخص",
    },
}


def get_artist(file_path, unknown_artist):
    """
    Read the artist name from the music file metadata.
    If no artist information is available,
    return the selected language's "Unknown Artist" value.
    """

    try:
        audio = File(file_path, easy=True)

        if audio:
            artist = audio.get("artist")

            if artist and artist[0].strip():
                return artist[0].strip()

    except Exception as error:
        print(f"Could not read metadata: {file_path}")
        print(error)

    return unknown_artist


def remove_existing_numbers(filename):
    """
    Remove all existing numbering prefixes from the beginning
    of a filename.
    Examples:
        '001 - Song.mp3' -> 'Song.mp3'
        '001 - 002 - Song.mp3' -> 'Song.mp3'
        '001-001-Song.mp3' -> 'Song.mp3'
        '001_002_015_Song.mp3' -> 'Song.mp3'
    """

    name, extension = os.path.splitext(filename)

    while True:

        cleaned_name = re.sub(
            r"^\s*\d+\s*[-_.]+\s*",
            "",
            name,
            count=1,
        )

        if cleaned_name == name:
            break

        name = cleaned_name

    return f"{name.strip()}{extension}"


def find_music_files(folder_path):
    """
    Return all supported music files inside the selected folder.
    Subfolders are ignored.
    """

    music_files = []

    for filename in os.listdir(folder_path):

        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        extension = os.path.splitext(filename)[1].lower()

        if extension in MUSIC_EXTENSIONS:
            music_files.append(file_path)

    return music_files


def create_shuffled_order(files_by_artist):
    """
    Create a new order for all songs from scratch.
    Songs from the same artist are kept apart whenever possible.
    The order of songs inside each artist group is randomized.
    """

    artist_queue = []

    for artist, songs in files_by_artist.items():

        shuffled_songs = songs.copy()

        random.shuffle(shuffled_songs)

        heapq.heappush(
            artist_queue,
            (
                -len(shuffled_songs),
                random.random(),
                artist,
                shuffled_songs,
            ),
        )

    ordered_songs = []

    previous_artist_data = None

    while artist_queue or previous_artist_data:

        if not artist_queue:

            count, random_value, artist, songs = previous_artist_data

            previous_artist_data = None

        else:

            count, random_value, artist, songs = heapq.heappop(artist_queue)

        song = songs.pop()

        ordered_songs.append((artist, song))

        if previous_artist_data:

            heapq.heappush(
                artist_queue,
                previous_artist_data,
            )

        if songs:

            previous_artist_data = (
                count + 1,
                random.random(),
                artist,
                songs,
            )

        else:

            previous_artist_data = None

    return ordered_songs


def create_output_folder(source_folder):
    """
    Create a fresh output folder next to the source folder.
    If the previous output folder exists, it is removed
    before creating the new result.
    """

    parent_folder = os.path.dirname(os.path.normpath(source_folder))

    folder_name = os.path.basename(os.path.normpath(source_folder))

    output_folder = os.path.join(parent_folder, f"{folder_name}_Shuffled")

    if os.path.exists(output_folder):

        shutil.rmtree(output_folder)

    os.makedirs(output_folder)

    return output_folder


def get_unique_filename(file_path):
    """
    Prevent overwriting files when two songs
    have the same filename.
    """

    if not os.path.exists(file_path):
        return file_path

    base_name, extension = os.path.splitext(file_path)

    counter = 1

    while True:

        new_path = f"{base_name} ({counter}){extension}"

        if not os.path.exists(new_path):
            return new_path

        counter += 1


def process_music_folder(source_folder, unknown_artist):
    """
    On every run:
    - All songs are scanned again
    - Artists are read again
    - Previous numbering is removed
    - A new order is created for all songs
    - A fresh output folder is created
    - All songs receive new numbering
    """

    if not os.path.isdir(source_folder):
        raise ValueError("invalid_folder")

    music_files = find_music_files(source_folder)

    if not music_files:
        raise ValueError("no_music_files")

    files_by_artist = defaultdict(list)

    # Read all songs again and group them by artist
    for file_path in music_files:

        artist = get_artist(
            file_path,
            unknown_artist,
        )

        files_by_artist[artist].append(file_path)

    # Create a completely new order for all songs
    ordered_songs = create_shuffled_order(files_by_artist)

    output_folder = create_output_folder(source_folder)

    total_songs = len(ordered_songs)

    number_width = max(
        3,
        len(str(total_songs)),
    )

    copied_songs = []

    for index, (artist, source_file) in enumerate(
        ordered_songs,
        start=1,
    ):

        original_filename = os.path.basename(source_file)

        # Remove all previous numbering prefixes
        clean_filename = remove_existing_numbers(original_filename)

        number = str(index).zfill(number_width)

        new_filename = f"{number} - {clean_filename}"

        destination_file = os.path.join(output_folder, new_filename)

        destination_file = get_unique_filename(destination_file)

        shutil.copy2(
            source_file,
            destination_file,
        )

        copied_songs.append(
            {
                "number": index,
                "artist": artist,
                "filename": os.path.basename(destination_file),
            }
        )

    return output_folder, copied_songs


class MusicShufflerApp:

    def __init__(self, root):

        self.root = root

        self.root.geometry("720x360")

        self.root.resizable(False, False)

        self.current_language = tk.StringVar(value="English")

        self.folder_path = tk.StringVar()

        self.create_interface()

        self.update_language()

    def get_text(self, key, **kwargs):

        text = TEXT[self.current_language.get()][key]

        if kwargs:
            return text.format(**kwargs)

        return text

    def create_interface(self):

        # Language toggle
        self.language_button = tk.Button(
            self.root,
            command=self.toggle_language,
            width=10,
        )

        self.language_button.pack(
            anchor="ne",
            padx=20,
            pady=(15, 0),
        )

        # Main title
        self.title_label = tk.Label(self.root, font=("Arial", 16, "bold"))

        self.title_label.pack(pady=(15, 5))

        # Description
        self.description_label = tk.Label(self.root, justify="center", wraplength=650)

        self.description_label.pack(pady=(0, 20))

        # Folder selection
        folder_frame = tk.Frame(self.root)

        folder_frame.pack(padx=20, fill="x")

        self.path_entry = tk.Entry(folder_frame, textvariable=self.folder_path)

        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_button = tk.Button(
            folder_frame, command=self.browse_folder, width=15
        )

        self.browse_button.pack(side="right")

        # Enable drag and drop
        self.path_entry.drop_target_register(DND_FILES)

        self.path_entry.dnd_bind("<<Drop>>", self.handle_drop)

        # Start button
        self.start_button = tk.Button(
            self.root,
            command=self.start_processing,
            font=("Arial", 11, "bold"),
            width=28,
            height=2,
        )

        self.start_button.pack(pady=25)

        # Status message
        self.status_label = tk.Label(self.root, wraplength=650)

        self.status_label.pack(pady=5)

    def toggle_language(self):

        if self.current_language.get() == "English":
            self.current_language.set("فارسی")
        else:
            self.current_language.set("English")

        self.update_language()

    def update_language(self):

        current_language = self.current_language.get()

        self.root.title(self.get_text("window_title"))

        self.title_label.config(text=self.get_text("title"))

        self.description_label.config(text=self.get_text("description"))

        self.browse_button.config(text=self.get_text("browse"))

        self.start_button.config(text=self.get_text("start"))

        self.status_label.config(text=self.get_text("ready"))

        # Show the language that the user can switch to
        if current_language == "English":
            self.language_button.config(text="فارسی")
        else:
            self.language_button.config(text="English")

    def browse_folder(self):

        folder = filedialog.askdirectory(title=self.get_text("select_folder_title"))

        if folder:
            self.folder_path.set(folder)

    def handle_drop(self, event):

        folder = event.data.strip("{}")

        self.folder_path.set(folder)

    def start_processing(self):

        source_folder = self.folder_path.get().strip()

        if not source_folder:

            messagebox.showwarning(
                self.get_text("no_folder_title"), self.get_text("no_folder_message")
            )

            return

        try:

            self.status_label.config(text=self.get_text("processing"))

            self.root.update()

            output_folder, copied_songs = process_music_folder(
                source_folder, self.get_text("unknown_artist")
            )

            self.status_label.config(
                text=self.get_text("done", count=len(copied_songs))
            )

            messagebox.showinfo(
                self.get_text("finished_title"),
                self.get_text(
                    "finished_message", count=len(copied_songs), folder=output_folder
                ),
            )

        except ValueError as error:

            error_key = str(error)

            if error_key in TEXT[self.current_language.get()]:

                error_message = self.get_text(error_key)

            else:

                error_message = error_key

            self.status_label.config(text=self.get_text("error_status"))

            messagebox.showerror(self.get_text("error_title"), error_message)

        except Exception as error:

            self.status_label.config(text=self.get_text("error_status"))

            messagebox.showerror(self.get_text("error_title"), str(error))


if __name__ == "__main__":

    root = TkinterDnD.Tk()

    app = MusicShufflerApp(root)

    root.mainloop()
