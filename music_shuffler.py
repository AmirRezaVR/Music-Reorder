import os
import re
import shutil
import heapq

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
        "window_title": "Music Shuffler by Artist",
        "title": "Music Shuffler",
        "language": "Language",
        "description": (
            "Select or drag and drop your music folder.\n"
            "Songs will be copied into a new folder and arranged "
            "to avoid consecutive songs from the same artist."
        ),
        "browse": "Browse...",
        "start": "Shuffle and Copy Music",
        "ready": "Ready",
        "processing": ("Reading music files and creating a new order..."),
        "done": "Done! {count} songs were processed.",
        "select_folder_title": "Select your music folder",
        "no_folder_title": "No Folder Selected",
        "no_folder_message": ("Please select or drag a music folder first."),
        "finished_title": "Finished",
        "finished_message": (
            "Successfully processed {count} songs.\n\n" "Output folder:\n{folder}"
        ),
        "error_title": "Error",
        "error_status": "An error occurred.",
        "invalid_folder": ("The selected folder does not exist."),
        "no_music_files": ("No supported music files were found in this folder."),
        "unknown_artist": "Unknown Artist",
    },
    "فارسی": {
        "window_title": "مرتب‌ساز موسیقی بر اساس خواننده",
        "title": "مرتب‌ساز موسیقی",
        "language": "زبان",
        "description": (
            "پوشه آهنگ‌ها را انتخاب کنید یا آن را "
            "Drag & Drop کنید.\n"
            "آهنگ‌ها در یک پوشه جدید کپی می‌شوند و تا حد امکان "
            "دو آهنگ از یک خواننده پشت سر هم قرار نمی‌گیرند."
        ),
        "browse": "انتخاب پوشه...",
        "start": "مرتب‌سازی و کپی آهنگ‌ها",
        "ready": "آماده",
        "processing": ("در حال خواندن اطلاعات آهنگ‌ها و ایجاد ترتیب جدید..."),
        "done": ("انجام شد! تعداد {count} آهنگ پردازش شد."),
        "select_folder_title": ("پوشه آهنگ‌ها را انتخاب کنید"),
        "no_folder_title": ("پوشه‌ای انتخاب نشده است"),
        "no_folder_message": ("ابتدا یک پوشه انتخاب کنید یا آن را Drag & Drop کنید."),
        "finished_title": "عملیات تمام شد",
        "finished_message": (
            "تعداد {count} آهنگ با موفقیت پردازش شد.\n\n" "پوشه خروجی:\n{folder}"
        ),
        "error_title": "خطا",
        "error_status": "خطایی رخ داد.",
        "invalid_folder": ("پوشه انتخاب‌شده وجود ندارد."),
        "no_music_files": ("هیچ فایل موسیقی پشتیبانی‌شده‌ای در این پوشه پیدا نشد."),
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


def remove_existing_number(filename):
    """
    Remove an existing number from the beginning of a filename.
    Examples:
        '001 - Song.mp3' -> 'Song.mp3'
        '12_Song.mp3'    -> 'Song.mp3'
    """

    return re.sub(r"^\s*\d+\s*[-_. ]+\s*", "", filename)


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
    Create an order where songs from the same artist
    are kept apart as much as possible.
    """

    artist_queue = []

    for artist, songs in files_by_artist.items():

        songs = sorted(songs)

        heapq.heappush(artist_queue, (-len(songs), artist, songs))

    result = []

    previous_artist = None
    previous_songs = None
    previous_count = 0

    while artist_queue or previous_songs:

        if not artist_queue:

            count = previous_count
            artist = previous_artist
            songs = previous_songs

            previous_artist = None
            previous_songs = None
            previous_count = 0

        else:

            count, artist, songs = heapq.heappop(artist_queue)

        song = songs.pop(0)

        result.append((artist, song))

        if previous_songs:

            heapq.heappush(
                artist_queue, (previous_count, previous_artist, previous_songs)
            )

        if songs:

            previous_artist = artist
            previous_songs = songs
            previous_count = count + 1

        else:

            previous_artist = None
            previous_songs = None
            previous_count = 0

    return result


def create_output_folder(source_folder):

    parent_folder = os.path.dirname(os.path.normpath(source_folder))

    folder_name = os.path.basename(os.path.normpath(source_folder))

    output_folder = os.path.join(parent_folder, f"{folder_name}_Shuffled")

    os.makedirs(output_folder, exist_ok=True)

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
    Read music files, group them by artist,
    create a balanced order, and copy them
    into a new numbered folder.
    """

    if not os.path.isdir(source_folder):
        raise ValueError("invalid_folder")

    music_files = find_music_files(source_folder)

    if not music_files:
        raise ValueError("no_music_files")

    output_folder = create_output_folder(source_folder)

    files_by_artist = defaultdict(list)

    for file_path in music_files:

        artist = get_artist(file_path, unknown_artist)

        files_by_artist[artist].append(file_path)

    ordered_songs = create_shuffled_order(files_by_artist)

    total_songs = len(ordered_songs)

    number_width = max(3, len(str(total_songs)))

    copied_songs = []

    for index, (artist, source_file) in enumerate(ordered_songs, start=1):

        original_filename = os.path.basename(source_file)

        clean_filename = remove_existing_number(original_filename)

        number = str(index).zfill(number_width)

        new_filename = f"{number} - {clean_filename}"

        destination_file = os.path.join(output_folder, new_filename)

        destination_file = get_unique_filename(destination_file)

        shutil.copy2(source_file, destination_file)

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

        # Language selector
        language_frame = tk.Frame(self.root)

        language_frame.pack(pady=(15, 0))

        self.language_label = tk.Label(language_frame)

        self.language_label.pack(side="left", padx=(0, 8))

        language_menu = tk.OptionMenu(
            language_frame,
            self.current_language,
            "English",
            "فارسی",
            command=lambda event: self.update_language(),
        )

        language_menu.pack(side="left")

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

    def update_language(self):

        self.root.title(self.get_text("window_title"))

        self.language_label.config(text=self.get_text("language"))

        self.title_label.config(text=self.get_text("title"))

        self.description_label.config(text=self.get_text("description"))

        self.browse_button.config(text=self.get_text("browse"))

        self.start_button.config(text=self.get_text("start"))

        self.status_label.config(text=self.get_text("ready"))

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
