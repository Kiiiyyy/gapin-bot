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
from src.utils import silence_alsa # <--- Import Peredam

LAGU_DIR = Path(__file__).resolve().parents[1] / "lagu"
SUPPORTED_EXT = (".mp3", ".wav", ".ogg", ".flac", ".m4a")
_TEMP_CONVERTED_FILE: Optional[Path] = None

def _ensure_mixer():
    """Pastikan mixer pygame sudah siap (Silent Mode)"""
    try:
        if not pygame.mixer.get_init():
            with silence_alsa():
                pygame.mixer.init()
    except Exception:
        pass

def _list_song_files() -> List[Path]:
    if not LAGU_DIR.exists():
        try: LAGU_DIR.mkdir(parents=True, exist_ok=True)
        except: pass
        return []
    return sorted([p for p in LAGU_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXT])

def _best_match(keyword: str) -> Optional[Path]:
    songs = _list_song_files()
    if not songs: return None
    candidates = {song.stem.lower(): song for song in songs}
    result = process.extractOne(keyword.lower(), list(candidates.keys()), score_cutoff=60)
    if result:
        matched_stem, _ = result
        return candidates[matched_stem]
    return None

def _cleanup_temp_file():
    global _TEMP_CONVERTED_FILE
    if _TEMP_CONVERTED_FILE and _TEMP_CONVERTED_FILE.exists():
        try: os.remove(_TEMP_CONVERTED_FILE)
        except OSError: pass
    _TEMP_CONVERTED_FILE = None

def _play_song(path: Path):
    global _TEMP_CONVERTED_FILE
    _ensure_mixer()
    _cleanup_temp_file()

    target_path = path
    try:
        if path.suffix.lower() not in [".wav", ".mp3"]:
            audio = AudioSegment.from_file(path)
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            audio.export(tmp.name, format="wav")
            target_path = Path(tmp.name)
            _TEMP_CONVERTED_FILE = target_path
    except Exception:
        target_path = path

    try:
        with silence_alsa(): # Bungkam saat load lagu
            pygame.mixer.music.load(str(target_path))
            pygame.mixer.music.play()

        def _monitor():
            while pygame.mixer.music.get_busy():
                time.sleep(0.5)
            _cleanup_temp_file()

        threading.Thread(target=_monitor, daemon=True).start()
    except Exception as e:
        print(f"Gagal memutar: {e}")

def _stop_song() -> bool:
    if not pygame.mixer.get_init(): return False
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        try: pygame.mixer.music.unload()
        except: pass
        _cleanup_temp_file()
        return True
    return False

def handle_music_command(text: str) -> Tuple[bool, Optional[str], Optional[Callable[[], None]]]:
    lower_text = text.lower()

    if any(phrase in lower_text for phrase in ["stop lagu", "hentikan lagu", "stop musik", "matikan lagu"]):
        stopped = _stop_song()
        return True, "Musik dimatikan." if stopped else "Tidak ada musik.", None

    match = re.search(r"(putar|mainkan|setel|play)\s+(?:lagu|musik)?\s*(.*)", lower_text)
    if match and ("putar" in lower_text or "mainkan" in lower_text or "play" in lower_text):
        query = match.group(2).strip()
        songs = _list_song_files()
        if not songs: return True, "Folder lagu kosong.", None

        target = _best_match(query) if query else songs[0]
        if not target and query: return True, f"Lagu {query} tidak ketemu.", None
        
        song_name = target.stem
        return True, f"Memutar {song_name}.", lambda: _play_song(target)

    return False, None, None