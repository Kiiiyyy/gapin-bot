import os
import time
import collections
import speech_recognition as sr
import webrtcvad

MODE_CONFIG = {
    "wake": {
        "ambient_duration": 0.8,
        "phrase_time_limit": 4,
        "max_duration": 4,
        "silence_duration": 0.5,
        "vad_aggressiveness": 2,
        "energy_threshold": 400,
        "dynamic_energy": True,
    },
    "command": {
        "ambient_duration": 0.4,
        "phrase_time_limit": 3,
        "max_duration": 3,
        "silence_duration": 0.35,
        "vad_aggressiveness": 3,
        "energy_threshold": 350,
        "dynamic_energy": True,
    },
}

SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30  # ms per frame fed into VAD


def _env_mic_index():
    value = os.getenv("MIC_DEVICE_INDEX")
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _capture_with_vad(recognizer, source, config):
    vad = webrtcvad.Vad(config["vad_aggressiveness"])
    frame_bytes = int(SAMPLE_RATE * (FRAME_DURATION_MS / 1000.0) * source.SAMPLE_WIDTH)
    max_frames = int((config["max_duration"] * 1000) / FRAME_DURATION_MS)
    silence_frames = max(1, int((config["silence_duration"] * 1000) / FRAME_DURATION_MS))

    ring_buffer = collections.deque(maxlen=silence_frames)
    voiced_frames = []
    triggered = False
    start_time = time.time()

    for _ in range(max_frames):
        frame = source.stream.read(frame_bytes)
        if len(frame) == 0:
            break

        is_speech = vad.is_speech(frame, SAMPLE_RATE)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = sum(1 for _, speech in ring_buffer if speech)
            if num_voiced > 0.6 * ring_buffer.maxlen:
                triggered = True
                voiced_frames.extend(f for f, _ in ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_silence = sum(1 for _, speech in ring_buffer if not speech)
            if num_silence == ring_buffer.maxlen:
                break

        if time.time() - start_time > config["max_duration"]:
            break

    if not voiced_frames:
        return None

    raw_audio = b"".join(voiced_frames)
    return sr.AudioData(raw_audio, SAMPLE_RATE, source.SAMPLE_WIDTH)


def _recognize_text(recognizer, audio_data):
    try:
        text = recognizer.recognize_google(audio_data, language="id-ID")
        print(f"🗣️ Anda bilang: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Suara tidak jelas.")
        return None
    except sr.RequestError:
        print("❌ Koneksi internet putus (Google SR butuh internet).")
        return None


def mendengar(listen_mode="wake"):
    config = MODE_CONFIG.get(listen_mode, MODE_CONFIG["command"])
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = config["energy_threshold"]
    recognizer.dynamic_energy_threshold = config["dynamic_energy"]
    recognizer.pause_threshold = 0.6
    recognizer.phrase_threshold = 0.3
    device_index = _env_mic_index()

    print(f"🎙️ Mode dengar: {listen_mode}")

    with sr.Microphone(sample_rate=SAMPLE_RATE, device_index=device_index) as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=config["ambient_duration"])
        except sr.WaitTimeoutError:
            print("⚠️ Mic tidak menangkap suara latar.")

        audio_data = _capture_with_vad(recognizer, source, config)
        if audio_data is None:
            print("😶 Tidak ada suara yang terdeteksi.")
            return None

        return _recognize_text(recognizer, audio_data)


if __name__ == "__main__":
    hasil = mendengar("command")
    print("Hasil:", hasil)
