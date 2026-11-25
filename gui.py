import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD

from core import MusicReorderError, process_music_folder

TEXT = {
    "English": {
        "window_title": "Music Reorder",
        "title": "Music Reorder",
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
        "invalid_folder": "The selected folder could not be found.",
        "no_music_files": "No supported music files were found in this folder.",
        "unknown_artist": "Unknown Artist",
    },
    "فارسی": {
        "window_title": "تغییر ترتیب آهنگ‌ها",
        "title": "تغییر ترتیب آهنگ‌ها",
        "description": (
            "پوشه‌ی آهنگ‌هایتان را انتخاب کنید یا آن را همین‌جا رها کنید (Drag & Drop).\n"
            "آهنگ‌ها در پوشه‌ای جدید کپی می‌شوند و ترتیبشان طوری تغییر می‌کند "
            "که تا حد امکان آهنگ‌های یک خواننده پشت هم نباشند."
        ),
        "browse": "...انتخاب پوشه",
        "start": "تغییر ترتیب و کپی آهنگ‌ها",
        "ready": "آماده",
        "processing": "...در حال خواندن اطلاعات آهنگ‌ها و ایجاد ترتیب جدید",
        "done": "انجام شد! تعداد {count} آهنگ پردازش شد.",
        "select_folder_title": "پوشه‌ی آهنگ‌ها را انتخاب کنید",
        "no_folder_title": "پوشه‌ای انتخاب نشده است",
        "no_folder_message": (
            "لطفاً پوشه‌ی آهنگ‌ها را انتخاب کنید یا آن را همین‌جا رها کنید (Drag & Drop)."
        ),
        "finished_title": "اتمام عملیات",
        "finished_message": (
            "تعداد {count} آهنگ با موفقیت پردازش شد.\n\n" "پوشه‌ی خروجی:\n{folder}"
        ),
        "error_title": "خطا",
        "error_status": "خطایی رخ داد",
        "invalid_folder": "پوشه‌ی انتخاب‌شده وجود ندارد",
        "no_music_files": "هیچ فایل صوتی قابل پردازشی در این پوشه پیدا نشد",
        "unknown_artist": "خواننده نامشخص",
    },
}


class MusicReorderApp:

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
        return text.format(**kwargs) if kwargs else text

    def create_interface(self):
        self.language_button = tk.Button(
            self.root, command=self.toggle_language, width=10
        )
        self.language_button.pack(anchor="ne", padx=20, pady=(15, 0))

        self.title_label = tk.Label(self.root, font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(15, 5))

        self.description_label = tk.Label(self.root, justify="center", wraplength=650)
        self.description_label.pack(pady=(0, 20))

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(padx=20, fill="x")

        self.path_entry = tk.Entry(folder_frame, textvariable=self.folder_path)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_button = tk.Button(
            folder_frame, command=self.browse_folder, width=15
        )
        self.browse_button.pack(side="right")

        self.path_entry.drop_target_register(DND_FILES)
        self.path_entry.dnd_bind("<<Drop>>", self.handle_drop)

        self.start_button = tk.Button(
            self.root,
            command=self.start_processing,
            font=("Arial", 11, "bold"),
            width=28,
            height=2,
        )
        self.start_button.pack(pady=25)

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
                self.get_text("no_folder_title"),
                self.get_text("no_folder_message"),
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
                    "finished_message",
                    count=len(copied_songs),
                    folder=output_folder,
                ),
            )

        except MusicReorderError as error:
            error_key = str(error)
            self.status_label.config(text=self.get_text("error_status"))
            messagebox.showerror(self.get_text("error_title"), self.get_text(error_key))

        except Exception as error:
            self.status_label.config(text=self.get_text("error_status"))
            messagebox.showerror(self.get_text("error_title"), str(error))


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MusicReorderApp(root)
    root.mainloop()
