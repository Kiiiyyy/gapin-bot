from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
import os
import time

def main():
    # Cek env var
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi.")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS (Mode Wake Word)")
    print("Panggil: 'Halo Gapin [pertanyaan]'")
    print("Tekan Ctrl+C untuk berhenti.")
    print("==========================================")
    
    # Intro
    ngomong("Sistem siap. Panggil saya dengan Halo Gapin.")
    
    # List variasi panggilan (jaga-jaga Google salah dengar ejaan)
    WAKE_WORDS = ["halo gapin", "hallo gapin", "hello gapin", "halo gavin", "halo kapin"]

    while True:
        try:
            # 1. Mendengar (Input Suara)
            suara_asli = mendengar()
            
            # Kalau tidak ada suara, skip
            if not suara_asli:
                continue
            
            # Ubah ke huruf kecil biar gampang dicek
            suara_lower = suara_asli.lower()
            
            # 2. Cek apakah ada kata kunci di AWAL kalimat?
            terpanggil = False
            for p in WAKE_WORDS:
                if suara_lower.startswith(p):
                    terpanggil = True
                    break
            
            if terpanggil:
                print(f"✅ Terpanggil! Memproses: {suara_asli}")
                
                # Bersihkan kata kuncinya sebelum dikirim ke Gemini
                # Contoh: "Halo Gapin siapa rektor?" -> jadi "siapa rektor?"
                pertanyaan_bersih = suara_lower
                for p in WAKE_WORDS:
                    pertanyaan_bersih = pertanyaan_bersih.replace(p, "").strip()
                
                # Kalau cuma panggil "Halo Gapin" doang tanpa pertanyaan
                if not pertanyaan_bersih:
                    ngomong("Ya, ada yang bisa saya bantu?")
                    continue

                # 3. Mikir & Jawab
                jawaban = tanya_robot(pertanyaan_bersih)
                ngomong(jawaban)
                
            else:
                # Kalau ngomongin hal lain, robot cuek aja
                print(f"❌ Diabaikan (Bukan panggilan): {suara_asli}")

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break

if __name__ == "__main__":
    main()