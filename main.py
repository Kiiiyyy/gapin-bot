from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar  # Import telinga baru
import os
import time

def main():
    # Cek env var
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi.")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS (Mode Suara)")
    print("Tekan Ctrl+C untuk berhenti.")
    print("==========================================")
    
    ngomong("Halo, saya siap mendengarkan. Silakan tanya sesuatu.")
    time.sleep(1) # Jeda biar gak nabrak

    while True:
        try:
            # 1. Mendengar (Input Suara)
            pertanyaan_user = mendengar()
            
            # Kalau tidak ada suara atau error, skip loop ini (dengar lagi)
            if not pertanyaan_user:
                continue
            
            # Cek kata kunci keluar
            if "keluar" in pertanyaan_user.lower() or "matikan" in pertanyaan_user.lower():
                ngomong("Oke, sampai jumpa.")
                break

            # 2. Mikir (Brain)
            jawaban = tanya_robot(pertanyaan_user)
            
            # 3. Ngomong (Speaking)
            ngomong(jawaban)

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break

if __name__ == "__main__":
    main()