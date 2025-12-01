import os
import re
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Tuple, List

import pygame
from fuzzywuzzy import process
from pydub import AudioSegment

LAGU_DIR = Path(__file__).resolve().parents[1] / "lagu"
SUPPORTED_EXT = (".mp3", ".wav", ".ogg", ".flac", ".m4a")
_TEMP_CONVERTED_FILE: Optional[Path] = None


def _ensure_mixer():
    """Pastikan mixer pygame sudah siap sebelum memutar audio."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def _list_song_files() -> List[Path]:
    if not LAGU_DIR.exists():
        return []
    return sorted(
        [p for p in LAGU_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXT]
    )


def _best_match(keyword: str) -> Optional[Path]:
    songs = _list_song_files()
    if not songs:
        return None

    candidates = {song.stem.lower(): song for song in songs}
    result = process.extractOne(keyword.lower(), list(candidates.keys()), score_cutoff=65)
    if result:
        matched_stem, _ = result
        return candidates[matched_stem]
    return None


def _format_song_list() -> str:
    songs = _list_song_files()
    if not songs:
        return "Belum ada lagu di folder."

    names = [song.stem for song in songs]
    return ", ".join(names)


def _cleanup_temp_file():
    global _TEMP_CONVERTED_FILE
    if _TEMP_CONVERTED_FILE and _TEMP_CONVERTED_FILE.exists():
        try:
            os.remove(_TEMP_CONVERTED_FILE)
        except OSError:
            pass
    _TEMP_CONVERTED_FILE = None


def _play_song(path: Path):
    global _TEMP_CONVERTED_FILE
    _ensure_mixer()
    _cleanup_temp_file()

    target_path = path
    if path.suffix.lower() != ".wav":
        audio = AudioSegment.from_file(path)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        audio.export(tmp.name, format="wav")
        target_path = Path(tmp.name)
        _TEMP_CONVERTED_FILE = target_path

    pygame.mixer.music.load(str(target_path))
    pygame.mixer.music.play()

    def _monitor():
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)
        _cleanup_temp_file()

    threading.Thread(target=_monitor, daemon=True).start()


def _stop_song() -> bool:
    if not pygame.mixer.get_init():
        return False
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
        except pygame.error:
            pass
        _cleanup_temp_file()
        return True
    return False



def handle_music_command(text: str) -> Tuple[bool, Optional[str], Optional[Callable[[], None]]]:
    """
    Analisa perintah musik. Mengembalikan tuple:
    (handled, teks_balasan, aksi_setelah_balasan)
    """
    lower_text = text.lower()

    # Hentikan lagu
    if any(phrase in lower_text for phrase in ["stop lagu", "hentikan lagu", "stop musik"]):
        stopped = _stop_song()
        if stopped:
            return True, "Lagu dihentikan.", None
        return True, "Tidak ada lagu yang sedang diputar.", None

    # Daftar lagu
    if any(phrase in lower_text for phrase in ["daftar lagu", "lagu apa saja", "lagu yang ada"]):
        daftar = _format_song_list()
        return True, f"Lagu yang tersedia: {daftar}", None

    # Putar lagu
    match = re.search(r"(putar|mainkan|play)\s+lagu\s*(.*)", lower_text)
    if match:
        query = match.group(2).strip()
        songs = _list_song_files()
        if not songs:
            return True, "Folder lagu kosong.", None

        target = None
        if query:
            target = _best_match(query)
            if not target:
                return True, f"Aku tidak menemukan lagu berjudul {query}.", None
        else:
            target = songs[0]

        song_name = target.stem

        def _action():
            _play_song(target)

        return True, f"Memutar lagu {song_name}.", _action

    return False, None, None

