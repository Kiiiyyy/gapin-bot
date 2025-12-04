import os
import sys
import time
import logging
import speech_recognition as sr
from contextlib import contextmanager

# ---------------------------------
# LOGGING CONFIG
# ---------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GaphinSpeech")

# ---------------------------------
# GLOBAL SINGLETONS
# ---------------------------------
_RECOGNIZER = None
_MIC = None

# ---------------------------------
# SILENCE ALSA ERRORS
# ---------------------------------
@contextmanager
def silence_alsa():
    """Membungkam error ALSA/JACK yang berisik"""
    try:
        stderr_fd = os.dup(sys.stderr.fileno())
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), sys.stderr.fileno())
        yield
    finally:
        os.dup2(stderr_fd, sys.stderr.fileno())

# ---------------------------------
# DEVICE RESOLUTION (PULSE ONLY)
# ---------------------------------
def _resolve_device_index(req_index=None):
    if req_index is not None:
        return req_index

    # Cek environment variable dulu
    env_idx = os.getenv("MIC_DEVICE_INDEX")
    if env_idx:
        try: return int(env_idx)
        except: pass

    # Karena Bapak PASTI pakai Pulse, kita cari device "pulse" saja
    try:
        with silence_alsa():
            names = sr.Microphone.list_microphone_names()

        for i, name in enumerate(names):
            if name.strip().lower() == "pulse":
                # logger.info(f"Found PulseAudio at index {i}")
                return i
                
    except Exception as e:
        logger.error(f"Gagal mencari mic: {e}")

    return None # Fallback ke default sistem (0)

# ---------------------------------
# INIT RESOURCES
# ---------------------------------
def _init(mic_index=None):
    global _RECOGNIZER, _MIC
    if not _RECOGNIZER:
        r = sr.Recognizer()
        r.energy_threshold = 120
        r.dynamic_energy_threshold = False
        r.operation_timeout = 4
        _RECOGNIZER = r

    if not _MIC:
        idx = _resolve_device_index(mic_index)
        try:
            with silence_alsa():
                _MIC = sr.Microphone(
                    device_index=idx,
                    sample_rate=16000,
                    chunk_size=1024
                )
            logger.info(f"Mic init success (Index: {idx})")
        except Exception as e:
            logger.error(f"Mic init FAIL: {e}")
            return None, None

    return _RECOGNIZER, _MIC

# ---------------------------------
# CONFIG PROFILES
# ---------------------------------
def _wake_config(r: sr.Recognizer):
    """Mode Cepat (Wake Word)"""
    r.pause_threshold = 0.4
    r.phrase_threshold = 0.2
    r.non_speaking_duration = 0.2

def _cmd_config(r: sr.Recognizer):
    """Mode Sabar (Command)"""
    r.pause_threshold = 0.6
    r.phrase_threshold = 0.3
    r.non_speaking_duration = 0.3

# ---------------------------------
# QUICK CALIBRATION
# ---------------------------------
def _quick_calibration(rec: sr.Recognizer, src, dur=0.2):
    try:
        rec.dynamic_energy_threshold = True
        with silence_alsa():
            rec.adjust_for_ambient_noise(src, duration=dur)
        
        if rec.energy_threshold < 300:
            rec.energy_threshold = 300
            
        rec.dynamic_energy_threshold = False
    except:
        rec.dynamic_energy_threshold = False

# ---------------------------------
# MAIN LISTENER
# ---------------------------------
def gaphin_listen(
    mode="wake", 
    quick_calib=False, 
    calib_time=0.25, 
    mic_index=None,
    on_phase_change=None # <--- Callback baru untuk kontrol Mata
):
    rec, src = _init(mic_index)
    if not rec or not src: return None

    _wake_config(rec) if mode == "wake" else _cmd_config(rec)

    with src:
        # [PHASE 1] Start Listening
        # Trigger Mata: LISTENING
        if on_phase_change: on_phase_change("LISTENING")

        status_text = "👂 Standby (Wake)..." if mode == "wake" else "🎤 Menunggu Perintah..."
        sys.stdout.write(f"\r{status_text}                           ")
        sys.stdout.flush()

        if quick_calib:
            sys.stdout.write("\r🎤 Kalibrasi Noise...                  ")
            sys.stdout.flush()
            _quick_calibration(rec, src, calib_time)
            sys.stdout.write(f"\r{status_text}                           ")
            sys.stdout.flush()

        try:
            with silence_alsa():
                audio = rec.listen(
                    src,
                    timeout=0.5 if mode == "wake" else 4,
                    phrase_time_limit=4 if mode == "wake" else 10
                )

            # [PHASE 2] Processing
            # Trigger Mata: PROCESSING (Mikir)
            if on_phase_change: on_phase_change("PROCESSING")
            
            sys.stdout.write("\r⚡ Processing...                       ")
            sys.stdout.flush()

            text = rec.recognize_google(audio, language="id-ID")
            
            # [PHASE 3] Success
            # Trigger Mata: IDLE (atau biarkan main.py yang handle speaking)
            # if on_phase_change: on_phase_change("IDLE")

            sys.stdout.write(f"\r✅ Input: {text}                         \n")
            sys.stdout.flush()
            return text.strip()

        except sr.WaitTimeoutError:
            if mode != "wake":
                sys.stdout.write("\r❌ Timeout (Tidak ada suara)          \n")
            return None
        except sr.UnknownValueError:
            if mode != "wake":
                sys.stdout.write("\r❌ Tidak jelas / Noise                \n")
            return None
        except sr.RequestError:
            sys.stdout.write("\r❌ Gangguan Koneksi                   \n")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None