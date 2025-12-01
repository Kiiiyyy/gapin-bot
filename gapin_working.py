import speech_recognition as sr
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

def gapin_dengarkan_optimized():
    """Fungsi mendengar yang dioptimalkan untuk bahasa Indonesia"""
    r = sr.Recognizer()
    
    # Settings khusus untuk kejelasan suara Indonesia
    r.energy_threshold = 800  # Lebih tinggi untuk mengurangi noise
    r.dynamic_energy_threshold = True
    r.dynamic_energy_adjustment_damping = 0.15
    r.pause_threshold = 1.2   # Pause lebih pendek untuk bahasa Indonesia
    r.phrase_threshold = 0.3  # Threshold untuk memulai deteksi
    r.non_speaking_duration = 0.5
    
    try:
        with sr.Microphone() as source:
            print("\n🔧 Kalibrasi untuk bahasa Indonesia...")
            print("   (Diam sebentar...)")
            r.adjust_for_ambient_noise(source, duration=2)
            
            print("\n🎤 BICARA DENGAN JELAS!")
            print("💡 Tips: Ucapkan perlahan, kata per kata")
            print("👂 Mendengarkan...")
            
            # Listen dengan parameter optimal
            audio = r.listen(
                source, 
                timeout=8, 
                phrase_time_limit=6,
                snowboy_configuration=None
            )
            
            print("✅ Memproses suara Indonesia...")
            
            # Gunakan Google Speech Recognition dengan parameter khusus
            text = r.recognize_google(
                audio, 
                language='id-ID',
                show_all=False  # Hanya hasil terbaik
            )
            
            text = text.strip().lower()
            print(f"🎉 HASIL: '{text}'")
            return text
            
    except sr.WaitTimeoutError:
        print("⏰ Timeout: Tidak ada suara")
        return None
    except sr.UnknownValueError:
        print("🔇 Suara tidak jelas")
        return None
    except sr.RequestError as e:
        print(f"🌐 Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_berbagai_kalimat():
    """Test dengan berbagai kalimat Indonesia"""
    print("🇮🇩 TEST BAHASA INDONESIA")
    print("=" * 40)
    
    kalimat_test = [
        "halo gapin",
        "apa kabar", 
        "terima kasih",
        "nama kamu siapa",
        "cerita lucu",
        "hari ini cerah",
        "saya mau tanya",
        "stop sekarang"
    ]
    
    print("Kalimat yang akan di-test:")
    for i, kalimat in enumerate(kalimat_test, 1):
        print(f"   {i}. '{kalimat}'")
    
    print(f"\n🎤 Silakan ucapkan salah satu kalimat di atas")
    
    for attempt in range(3):
        print(f"\n🔄 Percobaan {attempt + 1}/3")
        hasil = gapin_dengarkan_optimized()
        
        if hasil:
            # Cek akurasi
            for kalimat in kalimat_test:
                if any(kata in hasil for kata in kalimat.split()):
                    print(f"✅ Kata kunci terdeteksi: '{kalimat}'")
                    return hasil, kalimat
            
            print(f"⚠️  Terdengar: '{hasil}' (tidak sesuai expected)")
        else:
            print("❌ Gagal mendeteksi")
    
    return None, None

def main():
    print("🤖 GAPIN - OPTIMIZED INDONESIA SPEECH")
    print("=" * 50)
    
    while True:
        print("\n" + "="*40)
        hasil, expected = test_berbagai_kalimat()
        
        if hasil:
            print(f"\n📊 HASIL AKHIR:")
            print(f"   Yang diucapkan: '{expected}'")
            print(f"   Yang terdengar: '{hasil}'")
            
            # Hitung akurasi
            kata_expected = set(expected.split())
            kata_hasil = set(hasil.split())
            kata_tepat = kata_expected.intersection(kata_hasil)
            
            if kata_tepat:
                print(f"✅ Kata yang tepat: {kata_tepat}")
            else:
                print("❌ Tidak ada kata yang tepat")
        
        lanjut = input("\n🔁 Test lagi? (y/n): ").lower()
        if lanjut != 'y':
            break

if __name__ == "__main__":
    main()
