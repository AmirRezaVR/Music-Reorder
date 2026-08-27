import os
import re
import shutil
import heapq
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD
from mutagen import File

# -------------------------------------------------
# پسوندهای فایل‌های موسیقی که بررسی می‌شوند
# -------------------------------------------------

MUSIC_EXTENSIONS = (
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".wav",
    ".wma",
)


# -------------------------------------------------
# گرفتن نام خواننده از اطلاعات داخلی فایل
# -------------------------------------------------


def get_artist(file_path):
    """
    تلاش می‌کند نام خواننده را از metadata فایل پیدا کند.
    اگر پیدا نشد، آن را Unknown Artist قرار می‌دهد.
    """

    try:
        audio = File(file_path, easy=True)

        if audio is not None:
            artists = audio.get("artist")

            if artists:
                artist = artists[0].strip()

                if artist:
                    return artist

    except Exception as e:
        print(f"خطا در خواندن اطلاعات فایل:")
        print(file_path)
        print(e)

    return "Unknown Artist"


# -------------------------------------------------
# حذف شماره‌گذاری قبلی از ابتدای نام فایل
# -------------------------------------------------


def remove_old_number(filename):
    """
    اگر فایل قبلاً شماره‌گذاری شده باشد،
    شماره ابتدای آن را حذف می‌کند.

    مثال:
    001 - Song.mp3  -> Song.mp3
    12_Song.mp3     -> Song.mp3
    """

    pattern = r"^\s*\d+\s*[-_. ]+\s*"

    return re.sub(pattern, "", filename)


# -------------------------------------------------
# پیدا کردن تمام آهنگ‌های پوشه
# -------------------------------------------------


def find_music_files(folder_path):

    music_files = []

    for filename in os.listdir(folder_path):

        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        extension = os.path.splitext(filename)[1].lower()

        if extension in MUSIC_EXTENSIONS:
            music_files.append(file_path)

    return music_files


# -------------------------------------------------
# ساخت ترتیب مناسب
# -------------------------------------------------


def create_balanced_order(files_by_artist):
    """
    آهنگ‌ها را به ترتیبی قرار می‌دهد که
    یک خواننده تا حد ممکن پشت سر هم قرار نگیرد.

    از Priority Queue استفاده می‌شود.
    """

    heap = []

    # هر خواننده و تعداد آهنگ‌هایش وارد heap می‌شود
    for artist, files in files_by_artist.items():

        # مرتب کردن فایل‌های هر خواننده
        files = sorted(files)

        # heapq کوچک‌ترین مقدار را اول می‌دهد،
        # بنابراین تعداد را منفی می‌کنیم
        heapq.heappush(heap, (-len(files), artist, files))

    result = []

    previous_artist = None
    previous_files = None
    previous_count = 0

    while heap or previous_files:

        # اگر فقط آهنگ‌های خواننده قبلی باقی مانده باشند،
        # ناچار هستیم همان خواننده دوباره انتخاب شود
        if not heap:

            artist = previous_artist
            files = previous_files
            count = previous_count

            previous_artist = None
            previous_files = None
            previous_count = 0

        else:

            count, artist, files = heapq.heappop(heap)

        # یک آهنگ از این خواننده انتخاب می‌کنیم
        song = files.pop(0)

        result.append((artist, song))

        # خواننده قبلی را دوباره وارد heap می‌کنیم
        # تا آهنگ بعدی از خواننده دیگری انتخاب شود
        if previous_files:
            heapq.heappush(heap, (previous_count, previous_artist, previous_files))

        # اگر از خواننده فعلی آهنگ باقی مانده،
        # آن را برای دور بعد نگه می‌داریم
        if files:

            previous_artist = artist
            previous_files = files
            previous_count = count + 1

        else:

            previous_artist = None
            previous_files = None
            previous_count = 0

    return result


# -------------------------------------------------
# پردازش اصلی
# -------------------------------------------------


def process_music(source_folder):

    if not os.path.isdir(source_folder):
        raise Exception("آدرس پوشه معتبر نیست.")

    # پوشه خروجی کنار پوشه اصلی ساخته می‌شود
    parent_folder = os.path.dirname(source_folder)

    folder_name = os.path.basename(os.path.normpath(source_folder))

    output_folder = os.path.join(parent_folder, folder_name + "_Shuffled")

    # اگر پوشه خروجی وجود ندارد، ایجاد شود
    os.makedirs(output_folder, exist_ok=True)

    # پیدا کردن فایل‌های موسیقی
    music_files = find_music_files(source_folder)

    if not music_files:
        raise Exception("هیچ فایل موسیقی قابل پشتیبانی در این پوشه پیدا نشد.")

    # گروه‌بندی آهنگ‌ها بر اساس خواننده
    files_by_artist = defaultdict(list)

    for file_path in music_files:

        artist = get_artist(file_path)

        files_by_artist[artist].append(file_path)

    # ساخت ترتیب جدید
    ordered_files = create_balanced_order(files_by_artist)

    total_files = len(ordered_files)

    # تعداد رقم موردنیاز برای شماره‌گذاری
    digits = max(3, len(str(total_files)))

    copied_files = []

    # کپی فایل‌ها با نام جدید
    for index, (artist, source_file) in enumerate(ordered_files, start=1):

        original_filename = os.path.basename(source_file)

        clean_filename = remove_old_number(original_filename)

        number = str(index).zfill(digits)

        new_filename = f"{number} - {clean_filename}"

        destination_file = os.path.join(output_folder, new_filename)

        # اگر نام تکراری بود
        counter = 1
        base, extension = os.path.splitext(destination_file)

        while os.path.exists(destination_file):

            destination_file = f"{base} ({counter}){extension}"

            counter += 1

        # کپی فایل با حفظ metadata
        shutil.copy2(source_file, destination_file)

        copied_files.append((index, artist, new_filename))

    return output_folder, copied_files


# -------------------------------------------------
# رابط گرافیکی
# -------------------------------------------------


class MusicShufflerApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Music Artist Shuffler")

        self.root.geometry("700x300")

        self.root.resizable(False, False)

        # عنوان
        title = tk.Label(
            root,
            text="مرتب‌سازی آهنگ‌ها به صورت پراکنده بر اساس خواننده",
            font=("Arial", 14, "bold"),
        )

        title.pack(pady=20)

        # توضیح
        description = tk.Label(
            root,
            text=(
                "پوشه آهنگ‌ها را انتخاب کنید یا آن را داخل کادر زیر Drag & Drop کنید.\n"
                "فایل‌های اصلی تغییر نمی‌کنند و یک پوشه جدید ساخته می‌شود."
            ),
            justify="center",
        )

        description.pack(pady=5)

        # فریم انتخاب مسیر
        frame = tk.Frame(root)

        frame.pack(pady=15, padx=20, fill="x")

        self.path_var = tk.StringVar()

        self.path_entry = tk.Entry(frame, textvariable=self.path_var, width=60)

        self.path_entry.pack(side="left", padx=5, fill="x", expand=True)

        browse_button = tk.Button(frame, text="Browse", command=self.browse_folder)

        browse_button.pack(side="left", padx=5)

        # Drag & Drop
        self.path_entry.drop_target_register(DND_FILES)

        self.path_entry.dnd_bind("<<Drop>>", self.drop_folder)

        # دکمه شروع
        start_button = tk.Button(
            root,
            text="شروع مرتب‌سازی و کپی آهنگ‌ها",
            font=("Arial", 11, "bold"),
            command=self.start_process,
            width=30,
            height=2,
        )

        start_button.pack(pady=20)

        # وضعیت
        self.status_label = tk.Label(root, text="", wraplength=650)

        self.status_label.pack(pady=10)

    # ---------------------------------------------

    def browse_folder(self):

        folder = filedialog.askdirectory(title="پوشه آهنگ‌ها را انتخاب کنید")

        if folder:
            self.path_var.set(folder)

    # ---------------------------------------------

    def drop_folder(self, event):

        folder = event.data

        # حذف { } که گاهی در Drag & Drop ظاهر می‌شوند
        folder = folder.strip("{}")

        self.path_var.set(folder)

    # ---------------------------------------------

    def start_process(self):

        folder = self.path_var.get().strip()

        if not folder:

            messagebox.showwarning("خطا", "ابتدا پوشه آهنگ‌ها را انتخاب کنید.")

            return

        try:

            self.status_label.config(text="در حال بررسی آهنگ‌ها و ساخت ترتیب جدید...")

            self.root.update()

            output_folder, copied_files = process_music(folder)

            self.status_label.config(
                text=(f"{len(copied_files)} آهنگ با موفقیت پردازش شد.")
            )

            messagebox.showinfo(
                "عملیات با موفقیت انجام شد",
                (
                    f"تعداد آهنگ‌ها: {len(copied_files)}\n\n"
                    f"پوشه خروجی:\n{output_folder}"
                ),
            )

        except Exception as e:

            self.status_label.config(text="")

            messagebox.showerror("خطا", str(e))


# -------------------------------------------------
# اجرای برنامه
# -------------------------------------------------

if __name__ == "__main__":

    root = TkinterDnD.Tk()

    app = MusicShufflerApp(root)

    root.mainloop()
