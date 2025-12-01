import speech_recognition as sr
import os


def _env_mic_index():
    """Ambil device index dari environment variable jika ada."""
    value = os.getenv("MIC_DEVICE_INDEX")
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def mendengar(listen_mode="wake", mic_device=None):
    """
    Mendengarkan suara dan convert ke teks.
    
    Args:
        listen_mode: "wake" = continuous listening tanpa timeout, 
                     "command" = listen dengan durasi tertentu
        mic_device: Device index untuk microphone (None = default)
    
    Returns:
        str: Teks yang terdeteksi, atau None jika tidak ada
    """
    recognizer = sr.Recognizer()
    
    # Konfigurasi dasar - akan di-adjust per mode
    recognizer.dynamic_energy_threshold = True
    recognizer.phrase_threshold = 0.3
    
    device_index = _env_mic_index() if mic_device is None else mic_device
    
    try:
        with sr.Microphone(device_index=device_index) as source:
            if listen_mode == "wake":
                # Konfigurasi untuk wake mode
                recognizer.energy_threshold = 400
                recognizer.pause_threshold = 0.8
                recognizer.non_speaking_duration = 0.5
                
                # Kalibrasi ambient noise hanya sekali di awal
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except sr.WaitTimeoutError:
                    pass  # Skip jika tidak ada suara latar
                # Continuous listening - loop terus sampai ada suara terdeteksi
                print("👂 Mendengarkan terus menerus... (ucapkan 'Gapin' untuk memanggil)")
                
                while True:
                    try:
                        # Listen dengan timeout pendek per iterasi untuk continuous listening
                        # Timeout 1 detik = cepat detect suara baru, phrase_time_limit 3 = max durasi per phrase
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        # Coba recognize
                        try:
                            text = recognizer.recognize_google(audio, language='id-ID')
                            if text and text.strip():
                                print(f"🗣️ Terdengar: {text}")
                                return text.strip()
                        except sr.UnknownValueError:
                            # Suara tidak jelas/tidak ada suara, lanjut loop (continuous listening)
                            continue
                        except sr.RequestError as e:
                            print(f"❌ Error koneksi: {e}")
                            return None
                            
                    except sr.WaitTimeoutError:
                        # Timeout = tidak ada suara, lanjut loop (ini yang membuat continuous listening)
                        continue
                        
            else:  # command mode - responsive, mulai saat ada suara terdeteksi
                # Konfigurasi optimal untuk command mode (lebih responsive)
                recognizer.energy_threshold = 300  # Lebih sensitif untuk detect suara cepat
                recognizer.pause_threshold = 0.5   # Lebih pendek = lebih cepat stop setelah silence
                recognizer.non_speaking_duration = 0.3  # Durasi silence lebih pendek
                
                # Kalibrasi ambient noise dengan cepat untuk command mode
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                except sr.WaitTimeoutError:
                    pass
                
                # Best practice: Wait for speech detection - mulai listening hanya saat ada suara
                # listen() otomatis wait sampai ada suara yang melewati energy_threshold
                print("👂 Menunggu perintah Anda...")
                
                try:
                    # Listen() akan otomatis:
                    # 1. Wait for speech activity (tunggu sampai energy threshold tercapai)
                    # 2. Record audio mulai dari saat suara terdeteksi
                    # 3. Stop setelah pause_threshold + non_speaking_duration
                    # Ini membuatnya sangat responsive - mulai record tepat saat ada suara
                    audio = recognizer.listen(
                        source, 
                        timeout=5,  # Max waktu menunggu sebelum ada suara
                        phrase_time_limit=4  # Max durasi rekaman
                    )
                    
                    # Process audio yang sudah terekam (mulai dari saat suara terdeteksi)
                    text = recognizer.recognize_google(audio, language='id-ID')
                    if text and text.strip():
                        print(f"🗣️ Anda bilang: {text}")
                        return text.strip()
                    else:
                        print("❌ Suara tidak jelas.")
                        return None
                    
                except sr.WaitTimeoutError:
                    print("⏱️ Timeout: Tidak ada perintah terdeteksi.")
                    return None
                except sr.UnknownValueError:
                    print("❌ Suara tidak jelas atau tidak ada suara terdeteksi.")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Koneksi internet putus: {e}")
                    return None
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("Testing wake mode (continuous listening)...")
    result = mendengar("wake")
    print(f"Hasil: {result}")
