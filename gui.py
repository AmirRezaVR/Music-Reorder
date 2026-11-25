import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD

from core import MusicReorderError, process_music_folder

# Fonts that exist on Windows and have full Persian glyphs
FONTS = {
    "English": {
        "body": ("Segoe UI", 10),
        "title": ("Segoe UI Semibold", 18),
        "button": ("Segoe UI", 10),
        "start": ("Segoe UI Semibold", 11),
        "status": ("Segoe UI", 9),
    },
    "فارسی": {
        "body": ("Segoe UI", 10),
        "title": ("Segoe UI", 16, "bold"),
        "button": ("Segoe UI", 10),
        "start": ("Segoe UI", 11, "bold"),
        "status": ("Segoe UI", 9),
    },
}

TEXT = {
    "English": {
        "window_title": "Music Reorder",
        "title": "Music Reorder",
        "description": (
            "Select your music folder or drag and drop it onto this window.\n"
            "Your songs will be copied to a new folder and rearranged "
            "so that songs from the same artist are kept apart whenever possible."
        ),
        "browse": "Browse...",
        "start": "Reorder and Copy Music",
        "ready": "Ready",
        "processing": "Reading your music and creating a new order...",
        "done": "Done! {count} songs have been processed.",
        "select_folder_title": "Select Your Music Folder",
        "no_folder_title": "No Folder Selected",
        "no_folder_message": (
            "Please select your music folder or drag and drop it onto this window."
        ),
        "finished_title": "All Done",
        "finished_message": (
            "{count} songs have been successfully processed.\n\n"
            "Output folder:\n{folder}"
        ),
        "error_title": "Something Went Wrong",
        "error_status": "Something went wrong.",
        "invalid_folder": "The selected folder could not be found.",
        "no_music_files": "No supported music files were found in this folder.",
        "unknown_artist": "Unknown Artist",
    },
    "فارسی": {
        "window_title": "تغییر ترتیب آهنگ‌ها",
        "title": "تغییر ترتیب آهنگ‌ها",
        "description": (
            "پوشه‌ی آهنگ‌ها را انتخاب کنید، یا آن را به این پنجره بکشید و رها کنید.\n"
            "آهنگ‌ها در یک پوشه‌ی جدید کپی می‌شوند و ترتیبشان طوری تغییر می‌کند "
            "که تا حد امکان آهنگ‌های یک خواننده پشت سر هم پخش نشوند."
        ),
        "browse": "انتخاب پوشه",
        "start": "تغییر ترتیب و کپی آهنگ‌ها",
        "ready": "آماده",
        "processing": "در حال خواندن اطلاعات آهنگ‌ها و ساخت ترتیب جدید…",
        "done": "انجام شد! {count} آهنگ پردازش شد.",
        "select_folder_title": "پوشه‌ی آهنگ‌ها را انتخاب کنید",
        "no_folder_title": "پوشه‌ای انتخاب نشده است",
        "no_folder_message": (
            "لطفاً پوشه‌ی آهنگ‌ها را انتخاب کنید، یا آن را به این پنجره بکشید و رها کنید."
        ),
        "finished_title": "اتمام عملیات",
        "finished_message": (
            "{count} آهنگ با موفقیت پردازش شد.\n\n" "پوشه‌ی خروجی:\n{folder}"
        ),
        "error_title": "خطا",
        "error_status": "خطایی رخ داد.",
        "invalid_folder": "پوشه‌ی انتخاب‌شده پیدا نشد.",
        "no_music_files": "هیچ فایل صوتی قابل پردازشی در این پوشه پیدا نشد.",
        "unknown_artist": "خواننده‌ی نامشخص",
    },
}


class MusicReorderApp:

    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)

        self.style = ttk.Style(self.root)
        self.set_theme()

        self.current_language = tk.StringVar(value="English")
        self.folder_path = tk.StringVar()

        self.create_interface()
        self.update_language()

    def set_theme(self):
        # "vista" gives native Windows buttons; fall back to "clam" elsewhere
        for theme in ("vista", "clam"):
            try:
                self.style.theme_use(theme)
                return
            except tk.TclError:
                continue

    def get_text(self, key, **kwargs):
        text = TEXT[self.current_language.get()][key]
        return text.format(**kwargs) if kwargs else text

    def create_interface(self):
        self.main = ttk.Frame(self.root, padding=(28, 20))
        self.main.pack(fill="both", expand=True)
        self.main.columnconfigure(0, weight=1)

        # Language toggle (top right)
        self.language_button = ttk.Button(
            self.main, command=self.toggle_language, width=10
        )
        self.language_button.grid(row=0, column=0, sticky="e")

        # Title
        self.title_label = ttk.Label(self.main, style="Title.TLabel")
        self.title_label.grid(row=1, column=0, pady=(10, 6))

        # Description
        self.description_label = ttk.Label(self.main, justify="center", wraplength=640)
        self.description_label.grid(row=2, column=0, pady=(0, 22))

        # Folder selection
        folder_frame = ttk.Frame(self.main)
        folder_frame.grid(row=3, column=0, sticky="ew")
        folder_frame.columnconfigure(0, weight=1)

        self.path_entry = ttk.Entry(folder_frame, textvariable=self.folder_path)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=3)

        self.browse_button = ttk.Button(
            folder_frame, command=self.browse_folder, width=14
        )
        self.browse_button.grid(row=0, column=1)

        # Drag and drop
        self.path_entry.drop_target_register(DND_FILES)
        self.path_entry.dnd_bind("<<Drop>>", self.handle_drop)

        # Start button
        self.start_button = ttk.Button(
            self.main,
            command=self.start_processing,
            style="Start.TButton",
            width=30,
        )
        self.start_button.grid(row=4, column=0, pady=(26, 14), ipady=6)

        # Status
        self.status_label = ttk.Label(
            self.main, style="Status.TLabel", justify="center"
        )
        self.status_label.grid(row=5, column=0)

    def apply_fonts(self, language):
        fonts = FONTS[language]

        self.style.configure("TLabel", font=fonts["body"])
        self.style.configure("Title.TLabel", font=fonts["title"])
        self.style.configure(
            "Status.TLabel", font=fonts["status"], foreground="#555555"
        )
        self.style.configure("TButton", font=fonts["button"])
        self.style.configure("Start.TButton", font=fonts["start"])

        self.path_entry.configure(font=fonts["body"])

    def toggle_language(self):
        if self.current_language.get() == "English":
            self.current_language.set("فارسی")
        else:
            self.current_language.set("English")

        self.update_language()

    def update_language(self):
        language = self.current_language.get()

        self.apply_fonts(language)

        self.root.title(self.get_text("window_title"))
        self.title_label.config(text=self.get_text("title"))
        self.description_label.config(text=self.get_text("description"))
        self.browse_button.config(text=self.get_text("browse"))
        self.start_button.config(text=self.get_text("start"))
        self.status_label.config(text=self.get_text("ready"))

        # Show the language the user can switch to
        self.language_button.config(
            text="فارسی" if language == "English" else "English"
        )

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
                self.get_text("no_folder_title"),
                self.get_text("no_folder_message"),
            )
            return

        self.start_button.state(["disabled"])
        self.status_label.config(text=self.get_text("processing"))
        self.root.update()

        try:
            output_folder, copied_songs = process_music_folder(
                source_folder, self.get_text("unknown_artist")
            )

            self.status_label.config(
                text=self.get_text("done", count=len(copied_songs))
            )

            messagebox.showinfo(
                self.get_text("finished_title"),
                self.get_text(
                    "finished_message",
                    count=len(copied_songs),
                    folder=output_folder,
                ),
            )

        except MusicReorderError as error:
            self.status_label.config(text=self.get_text("error_status"))
            messagebox.showerror(
                self.get_text("error_title"), self.get_text(str(error))
            )

        except Exception as error:
            self.status_label.config(text=self.get_text("error_status"))
            messagebox.showerror(self.get_text("error_title"), str(error))

        finally:
            self.start_button.state(["!disabled"])


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MusicReorderApp(root)
    root.mainloop()
