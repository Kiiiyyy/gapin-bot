import speech_recognition as sr
import os
import sys


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
    Mendengarkan suara dan convert ke teks dengan optimasi untuk capture penuh.
    
    Args:
        listen_mode: "wake" = continuous listening tanpa timeout, 
                     "command" = listen dengan durasi tertentu
        mic_device: Device index untuk microphone (None = default)
    
    Returns:
        str: Teks yang terdeteksi, atau None jika tidak ada
    """
    recognizer = sr.Recognizer()
    
    # Konfigurasi dasar - balanced untuk capture penuh
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    
    device_index = _env_mic_index() if mic_device is None else mic_device
    
    try:
        with sr.Microphone(device_index=device_index) as source:
            if listen_mode == "wake":
                # Konfigurasi balanced untuk wake mode - capture penuh dari awal
                # Best practice: Parameter balanced untuk capture penuh tanpa cut off awal suara
                
                # Energy threshold: Cukup untuk detect suara normal, tidak terlalu sensitif
                recognizer.energy_threshold = 350  
                
                # Pause threshold: Durasi silence sebelum stop recording
                # Penting: Cukup panjang untuk capture kata penuh setelah user selesai bicara
                recognizer.pause_threshold = 0.8   
                
                # Phrase threshold: Threshold untuk mulai recording
                # Tidak terlalu rendah agar tidak start recording terlalu cepat (yang bisa miss awal)
                recognizer.phrase_threshold = 0.3  
                
                # Non-speaking duration: Durasi silence minimum untuk stop
                recognizer.non_speaking_duration = 0.5  
                
                # Calibration untuk ambient noise (penting untuk filter noise)
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except sr.WaitTimeoutError:
                    pass
                
                # Continuous listening - ALWAYS detect semua suara apapun
                print("👂 Mendengarkan terus menerus... (akan detect semua suara)")
                
                while True:
                    try:
                        # listen() sudah punya internal buffer untuk capture awal suara
                        # timeout: Max waktu menunggu sebelum ada suara (untuk wait, bukan cut off)
                        # phrase_time_limit: Max durasi recording (cukup untuk capture penuh)
                        audio = recognizer.listen(
                            source, 
                            timeout=1,  # Wait max 1 detik untuk ada suara
                            phrase_time_limit=4  # Max 4 detik recording (cukup untuk frase penuh)
                        )
                        
                        # Feedback saat audio terdeteksi
                        sys.stdout.write("🔊 Suara terdeteksi! ⚡ ")
                        sys.stdout.flush()
                        
                        # Process SEMUA suara yang terdeteksi - tidak filter di sini
                        try:
                            text = recognizer.recognize_google(audio, language='id-ID')
                            
                            # Return SEMUA text yang terdeteksi (apapun itu)
                            # Biarkan main.py yang cek apakah ini wake word atau bukan
                            if text and text.strip():
                                sys.stdout.write(f"\r✅ Terdengar: {text}\n")
                                sys.stdout.flush()
                                return text.strip()
                        except sr.UnknownValueError:
                            # Suara tidak jelas - clear dan continue
                            sys.stdout.write("\r" + " " * 50 + "\r")
                            sys.stdout.flush()
                            continue
                        except sr.RequestError as e:
                            print(f"\r❌ Error koneksi: {e}")
                            return None
                            
                    except sr.WaitTimeoutError:
                        # Timeout = tidak ada suara, lanjut loop (continuous listening)
                        continue
                        
            else:  # command mode - balanced untuk capture penuh
                # Konfigurasi balanced untuk command mode
                recognizer.energy_threshold = 300  # Balanced sensitivity
                recognizer.pause_threshold = 0.6   # Cukup panjang untuk capture perintah penuh
                recognizer.phrase_threshold = 0.3  # Balanced - capture dari awal
                recognizer.non_speaking_duration = 0.4  # Cukup untuk detect akhir perintah
                
                # Calibration
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                except sr.WaitTimeoutError:
                    pass
                
                # Interactive feedback
                print("👂 Siap mendengarkan...")
                sys.stdout.write("   ⏳ Menunggu perintah Anda...\r")
                sys.stdout.flush()
                
                try:
                    # Balanced listening - capture penuh dari awal sampai akhir
                    # timeout = wait for speech, phrase_time_limit = max durasi recording
                    audio = recognizer.listen(
                        source, 
                        timeout=5,  # Wait cukup lama untuk ada suara
                        phrase_time_limit=5  # Max durasi cukup untuk perintah penuh
                    )
                    
                    # Feedback saat suara terdeteksi
                    sys.stdout.write("\r🔊 Perintah terdeteksi! ⚡ Memproses... ")
                    sys.stdout.flush()
                    
                    # Recognition
                    text = recognizer.recognize_google(audio, language='id-ID')
                    
                    if text and text.strip():
                        sys.stdout.write(f"\r✅ Anda bilang: {text}\n")
                        sys.stdout.flush()
                        return text.strip()
                    else:
                        print("\r❌ Suara tidak jelas.")
                        return None
                    
                except sr.WaitTimeoutError:
                    print("\r⏱️ Timeout: Tidak ada perintah terdeteksi.")
                    return None
                except sr.UnknownValueError:
                    print("\r❌ Suara tidak jelas atau tidak ada suara terdeteksi.")
                    return None
                except sr.RequestError as e:
                    print(f"\r❌ Koneksi internet putus: {e}")
                    return None
                    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        return None
    except Exception as e:
        print(f"\r❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("Testing wake mode (balanced listening)...")
    result = mendengar("wake")
    print(f"Hasil: {result}")
