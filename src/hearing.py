import subprocess
import speech_recognition as sr
import os
import tempfile

def mendengar(duration=8, mic_device='hw:3,0'):
    """Merekam audio pakai arecord, lalu convert ke teks dengan Google SR"""
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        filename = tmpfile.name

    # Rekam audio pakai arecord
    print(f"🎤 Merekam suara {duration} detik...")
    cmd = ['arecord', '-D', mic_device, '-f', 'S16_LE', '-r', '44100', '-c', '1', '-d', str(duration), filename]
    subprocess.run(cmd, check=True)
    print("✅ Rekaman selesai. Memproses suara...")

    # Pakai SpeechRecognition untuk konversi ke teks
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    
    try:
        text = r.recognize_google(audio, language='id-ID')
        print(f"🗣️ Anda bilang: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Suara tidak jelas.")
        return None
    except sr.RequestError:
        print("❌ Koneksi internet putus (Google SR butuh internet).")
        return None
    finally:
        os.remove(filename)

if __name__ == "__main__":
    mendengar()
