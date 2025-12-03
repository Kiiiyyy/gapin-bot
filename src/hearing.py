import speech_recognition as sr
import os
import sys
import time
from contextlib import contextmanager

# --- SILENCER ERROR ALSA ---
@contextmanager
def no_alsa_error():
    try:
        original_stderr = os.dup(sys.stderr.fileno())
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stderr.fileno())
        yield
    finally:
        os.dup2(original_stderr, sys.stderr.fileno())
        os.close(original_stderr)
        if 'devnull' in locals():
            os.close(devnull)

# --- GLOBAL VARIABLES ---
_SHARED_RECOGNIZER = None
_SHARED_MIC = None
# ------------------------

def _get_device_index(requested_index=None):
    if requested_index is not None:
        return requested_index

    env_val = os.getenv("MIC_DEVICE_INDEX")
    if env_val and env_val.strip():
        try:
            return int(env_val)
        except ValueError: 
            pass

    try:
        with no_alsa_error():
            mic_names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_names):
            if "pulse" == name.strip().lower(): 
                return i
        for i, name in enumerate(mic_names):
            if "default" in name.lower(): 
                return i
    except Exception:
        pass
    return None


def _init_shared_resources(mic_device=None):
    global _SHARED_RECOGNIZER, _SHARED_MIC
    
    if _SHARED_RECOGNIZER is None:
        _SHARED_RECOGNIZER = sr.Recognizer()
        _SHARED_RECOGNIZER.dynamic_energy_threshold = False
        _SHARED_RECOGNIZER.energy_threshold = 130

    if _SHARED_MIC is None:
        device_index = _get_device_index(mic_device)
        try:
            with no_alsa_error():
                _SHARED_MIC = sr.Microphone(device_index=device_index)
        except Exception as e:
            print(f"❌ Gagal init mic: {e}")
            return None, None
            
    return _SHARED_RECOGNIZER, _SHARED_MIC


# ===================================================================
#     OPTIMIZED FAST RECOGNIZER - WAKE + COMMAND MODE
# ===================================================================

def mendengar(listen_mode="wake", mic_device=None):
    recognizer, source = _init_shared_resources(mic_device)
    if not recognizer or not source:
        return None

    # ⚡ MODE PEMROSESAN CEPAT
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 130
    recognizer.pause_threshold = 0.4
    recognizer.non_speaking_duration = 0.15
    recognizer.operation_timeout = 1

    last_text = ""
    debounce_time = 0.7

    try:
        with source:
            if listen_mode == "wake":
                print("\r👂 Mode WAKE (Ultra Responsif!)", end="", flush=True)

                while True:
                    try:
                        with no_alsa_error():
                            audio = recognizer.listen(
                                source,
                                timeout=0.35,
                                phrase_time_limit=3.5
                            )

                        try:
                            text = recognizer.recognize_google(audio, language="id-ID").strip()
                            
                            if text and text != last_text:
                                last_text = text
                                print(f"\n🟢 Dengar: {text}")
                                time.sleep(debounce_time)
                                return text

                            print("\r👂 ...                                             ", end="", flush=True)

                        except sr.UnknownValueError:
                            print("\r👂 ...                                             ", end="", flush=True)
                            continue
                        except sr.RequestError:
                            time.sleep(0.3)
                            continue

                    except sr.WaitTimeoutError:
                        print("\r👂 Standby cepat...                                ", end="", flush=True)
                        continue


            else:
                print("\r🎤 Dengarkan perintah...", end="", flush=True)
                recognizer.pause_threshold = 0.45
                recognizer.non_speaking_duration = 0.2

                try:
                    with no_alsa_error():
                        audio = recognizer.listen(
                            source,
                            timeout=3,
                            phrase_time_limit=6.5
                        )

                    print("\r⏳ Memproses...", end="", flush=True)
                    text = recognizer.recognize_google(audio, language="id-ID").strip()
                    print(f"\r🟢 Perintah: {text}                ")

                    return text

                except sr.WaitTimeoutError:
                    print("\r⌛ Terlalu lama diam.           ")
                    return None
                except sr.UnknownValueError:
                    print("\r❌ Tidak terdengar/kurang jelas.")
                    return None
                except sr.RequestError:
                    print("\r⚠️ Gangguan API Google       ")
                    time.sleep(0.3)
                    return None

    except KeyboardInterrupt:
        return None
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        return None


# ===============================================================
# TESTING MODE MANDIRI
# ===============================================================

if __name__ == "__main__":
    print("Testing Ultra Fast Mode...")
    mendengar("wake")
