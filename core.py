import os
import re
import shutil
import heapq
import random

from collections import defaultdict
from mutagen import File

MUSIC_EXTENSIONS = (
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".wav",
    ".wma",
)

# Matches a track number at the start of a filename, such as:
#   "001 - ", "01 ", "01. ", "1-01 "
# It does not match "1979 - ..." or "10.000 ..." because the number
# is followed by digits, not by a separator and a non-digit.
TRACK_PREFIX_PATTERN = re.compile(
    r"^\s*(?:\d{1,2}\s*-\s*)?\d{1,3}(?:\s*[-_.]\s*(?=\D)|\s+(?=\D))"
)


class MusicReorderError(Exception):
    """Error with a message key that the interface can translate."""


def get_artist(file_path, unknown_artist):
    """Return the artist from metadata, or the fallback value."""
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
    Remove track number prefixes from the start of a filename,
    without touching numbers that are part of the title.
    """
    name, extension = os.path.splitext(filename)

    while True:
        cleaned_name = TRACK_PREFIX_PATTERN.sub("", name, count=1)

        if cleaned_name == name:
            break

        name = cleaned_name

    name = name.strip()

    if not name:
        return filename

    return f"{name}{extension}"


def find_music_files(folder_path):
    """Return supported music files directly inside the folder."""
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
    Return a new order of (artist, file) pairs.
    Songs from the same artist are kept apart whenever possible.
    """
    artist_queue = []

    for artist, songs in files_by_artist.items():
        shuffled_songs = songs.copy()
        random.shuffle(shuffled_songs)

        heapq.heappush(
            artist_queue,
            (-len(shuffled_songs), random.random(), artist, shuffled_songs),
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
            heapq.heappush(artist_queue, previous_artist_data)

        if songs:
            previous_artist_data = (count + 1, random.random(), artist, songs)
        else:
            previous_artist_data = None

    return ordered_songs


def get_output_folder_path(source_folder):
    """Example: 'Music' -> 'Music_Shuffled'."""
    parent_folder = os.path.dirname(os.path.normpath(source_folder))
    folder_name = os.path.basename(os.path.normpath(source_folder))
    return os.path.join(parent_folder, f"{folder_name}_Shuffled")


def get_unique_filename(file_path):
    """Avoid overwriting when two songs end up with the same name."""
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
    Read, reorder and copy all songs from source_folder into a new folder.
    The previous output folder is replaced only after the copy succeeds.
    Returns (output_folder, copied_songs).
    Raises MusicReorderError with a message key on expected failures.
    """
    if not os.path.isdir(source_folder):
        raise MusicReorderError("invalid_folder")

    music_files = find_music_files(source_folder)

    if not music_files:
        raise MusicReorderError("no_music_files")

    files_by_artist = defaultdict(list)

    for file_path in music_files:
        artist = get_artist(file_path, unknown_artist)
        files_by_artist[artist].append(file_path)

    ordered_songs = create_shuffled_order(files_by_artist)

    output_folder = get_output_folder_path(source_folder)
    temp_folder = f"{output_folder}_tmp"
    backup_folder = f"{output_folder}_old"

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)

    os.makedirs(temp_folder)

    number_width = max(3, len(str(len(ordered_songs))))
    copied_songs = []

    try:
        for index, (artist, source_file) in enumerate(ordered_songs, start=1):
            clean_filename = remove_existing_numbers(os.path.basename(source_file))
            number = str(index).zfill(number_width)
            new_filename = f"{number} - {clean_filename}"

            destination_file = get_unique_filename(
                os.path.join(temp_folder, new_filename)
            )

            shutil.copy2(source_file, destination_file)

            copied_songs.append(
                {
                    "number": index,
                    "artist": artist,
                    "filename": os.path.basename(destination_file),
                }
            )

        if os.path.exists(output_folder):
            if os.path.exists(backup_folder):
                shutil.rmtree(backup_folder)
            os.rename(output_folder, backup_folder)

        os.rename(temp_folder, output_folder)

    except Exception:
        shutil.rmtree(temp_folder, ignore_errors=True)

        if not os.path.exists(output_folder) and os.path.exists(backup_folder):
            os.rename(backup_folder, output_folder)

        raise

    if os.path.exists(backup_folder):
        shutil.rmtree(backup_folder)

    return output_folder, copied_songs
