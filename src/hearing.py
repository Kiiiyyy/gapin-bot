import speech_recognition as sr

def mendengar():
    r = sr.Recognizer()
    
    # List microphone yang tersedia (opsional, buat debug)
    print(sr.Microphone.list_microphone_names())

    with sr.Microphone() as source:
        print("\n🎤 Silakan bicara...")
        
        # Kalibrasi noise ruangan otomatis (penting buat RPi)
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Robot mendengarkan (timeout 5 detik kalau hening)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳ Sedang mencerna suara...")
            
            # Ubah suara ke teks (pakai Google Speech Recognition - Gratis)
            # language='id-ID' biar paham logat Indonesia
            text = r.recognize_google(audio, language='id-ID')
            
            print(f"🗣️ Anda bilang: {text}")
            return text

        except sr.WaitTimeoutError:
            print("timeout: Tidak ada suara terdeteksi.")
            return None
        except sr.UnknownValueError:
            print("error: Suara tidak jelas.")
            return None
        except sr.RequestError:
            print("error: Koneksi internet putus (Google SR butuh internet).")
            return None