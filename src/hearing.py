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
    Mendengarkan suara dan convert ke teks dengan optimasi untuk responsivitas maksimal.
    
    Args:
        listen_mode: "wake" = continuous listening tanpa timeout, 
                     "command" = listen dengan durasi tertentu (lebih responsive)
        mic_device: Device index untuk microphone (None = default)
    
    Returns:
        str: Teks yang terdeteksi, atau None jika tidak ada
    """
    recognizer = sr.Recognizer()
    
    # Konfigurasi dasar - optimized untuk speed
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.phrase_threshold = 0.2  # Lower = lebih cepat detect
    
    device_index = _env_mic_index() if mic_device is None else mic_device
    
    try:
        with sr.Microphone(device_index=device_index) as source:
            if listen_mode == "wake":
                # Konfigurasi untuk wake mode - optimized untuk speed
                recognizer.energy_threshold = 300  # Lower = lebih sensitif, detect lebih cepat
                recognizer.pause_threshold = 0.5   # Shorter = lebih cepat stop
                recognizer.non_speaking_duration = 0.25  # Minimal silence untuk stop cepat
                
                # Quick calibration (hanya 0.2s)
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except sr.WaitTimeoutError:
                    pass
                
                # Continuous listening - loop dengan feedback real-time
                print("👂 Mendengarkan terus menerus... (ucapkan 'Gapin' untuk memanggil)")
                
                while True:
                    try:
                        # Ultra-short timeout untuk maximum responsiveness
                        audio = recognizer.listen(source, timeout=0.3, phrase_time_limit=2.5)
                        
                        # INSTANT feedback saat audio terdeteksi
                        sys.stdout.write("🔊 Suara terdeteksi! ⚡ ")
                        sys.stdout.flush()
                        
                        # Process dengan feedback real-time
                        try:
                            text = recognizer.recognize_google(audio, language='id-ID')
                            
                            if text and text.strip():
                                sys.stdout.write(f"\r✅ Terdengar: {text}\n")
                                sys.stdout.flush()
                                return text.strip()
                        except sr.UnknownValueError:
                            # Clear line dan continue (fast reset)
                            sys.stdout.write("\r" + " " * 50 + "\r")
                            sys.stdout.flush()
                            continue
                        except sr.RequestError as e:
                            print(f"\r❌ Error koneksi: {e}")
                            return None
                            
                    except sr.WaitTimeoutError:
                        # Timeout = lanjut loop instantly (continuous listening)
                        continue
                        
            else:  # command mode - MAXIMUM RESPONSIVENESS
                # Konfigurasi ultra-responsive untuk command mode
                recognizer.energy_threshold = 250  # Very sensitive
                recognizer.pause_threshold = 0.4   # Very fast stop
                recognizer.non_speaking_duration = 0.2  # Minimal silence
                
                # Very quick calibration
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except sr.WaitTimeoutError:
                    pass
                
                # Interactive feedback
                print("👂 Siap mendengarkan...")
                sys.stdout.write("   ⏳ Menunggu perintah Anda...\r")
                sys.stdout.flush()
                
                try:
                    # Ultra-responsive listening
                    # Timeout pendek tapi phrase_limit cukup untuk perintah
                    audio = recognizer.listen(
                        source, 
                        timeout=4,  # Shorter timeout
                        phrase_time_limit=4  # Max durasi
                    )
                    
                    # Immediate feedback saat suara terdeteksi (INSTANT!)
                    sys.stdout.write("\r🔊 Perintah terdeteksi! ")
                    sys.stdout.flush()
                    
                    # Process immediately tanpa delay
                    sys.stdout.write("⚡ Memproses... ")
                    sys.stdout.flush()
                    
                    # Fast recognition (non-blocking feedback)
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
    print("Testing command mode (responsive listening)...")
    result = mendengar("command")
    print(f"Hasil: {result}")
