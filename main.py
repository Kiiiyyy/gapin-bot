from src.brain import tanya_robot
from src.speaking import ngomong
import os

def main():
    # Cek kelengkapan
    if not os.path.exists("data/info_kampus.txt"):
        print("⚠️ Warning: File data/info_kampus.txt belum dibuat!")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi di file .env")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS SIAP (Mode Ketik)")
    print("Ketik 'keluar' untuk berhenti.")
    print("==========================================")
    
    # Intro
    ngomong("Halo, sistem saya sudah aktif. Silakan tanya sesuatu.")

    while True:
        try:
            # 1. Input (Nanti diganti Mic)
            user_input = input("\n👤 Anda: ")
            
            if user_input.lower() in ["keluar", "exit", "stop"]:
                ngomong("Sampai jumpa lagi.")
                break
            
            if not user_input:
                continue

            # 2. Proses Berpikir (Brain)
            print("⏳ Sedang memproses...")
            jawaban = tanya_robot(user_input)
            
            # 3. Output Suara (Speaking)
            ngomong(jawaban)

        except KeyboardInterrupt:
            print("\nProgram dihentikan paksa.")
            break

if __name__ == "__main__":
    main()