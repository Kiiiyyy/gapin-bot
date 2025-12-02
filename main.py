from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
from src.music import handle_music_command  # <--- Import modul musik
import os
import time
from dotenv import load_dotenv

# Load env variables (biar API Key kebaca)
load_dotenv()

def main():
    # Cek env var
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi di .env")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS (Music + Flexible Wake Word)")
    print("Panggil 'Gapin' di mana saja dalam kalimat.")
    print("Contoh: 'Eh Gapin putar lagu avenged'")
    print("==========================================")
    
    ngomong("Sistem siap. Panggil saya Gapin.")
    
    # List variasi panggilan (cukup nama saja biar flexible)
    # Tambahkan 'halo gapin' juga biar kalau user formal tetap nyaut
    WAKE_WORDS = ["gapin", "gavin", "dapin", "gappin", "gapen", "gapin", "gaping", "gaben", "gabin", "gupin", "gopin", "ga pin", "ga fin", "davin"]

    while True:
        try:
            # 1. Mendengar (Input Suara Standby)
            suara_asli = mendengar(listen_mode="wake")
            
            if not suara_asli:
                continue
            
            suara_lower = suara_asli.lower()
            
            # 2. LOGIKA BARU: Cek Wake Word di MANA SAJA
            terpanggil = False
            sisa_pertanyaan = ""

            for trigger in WAKE_WORDS:
                if trigger in suara_lower:
                    terpanggil = True
                    print(f"✅ Terpanggil oleh trigger: '{trigger}'")
                    
                    # Potong kalimat, ambil isinya saja
                    # Contoh: "Eh Gapin putar lagu" -> parts[0]="Eh ", parts[1]=" putar lagu"
                    parts = suara_lower.split(trigger, 1)
                    if len(parts) > 1:
                        sisa_pertanyaan = parts[1].strip()
                    
                    break 

            if terpanggil:
                print(f"📝 Command Awal: {sisa_pertanyaan}")
                
                # Variabel untuk menampung perintah final yang akan dieksekusi
                final_command = sisa_pertanyaan

                # Kasus 1: Cuma panggil nama ("Gapin") tanpa perintah
                if not final_command:
                    ngomong("Ya, saya di sini. Mau apa?")
                    
                    print("🎤 Menunggu perintah lanjutan...")
                    final_command = mendengar(listen_mode="command")
                    
                    if not final_command:
                         ngomong("Tidak ada suara, saya kembali tidur.")
                         continue # Kembali ke loop awal

                # --- BAGIAN EDIT: CEK MUSIK DULU ---
                # Cek apakah command (baik yang langsung atau susulan) adalah musik?
                is_music, music_reply, music_action = handle_music_command(final_command)

                if is_music:
                    # 1. Robot jawab status musik ("Memutar lagu...")
                    if music_reply:
                        ngomong(music_reply)
                    
                    # 2. Jalankan lagunya
                    if music_action:
                        print("🎵 Memutar Musik...")
                        music_action()
                    
                    # 3. Skip tanya Gemini, langsung loop lagi
                    continue 
                # -----------------------------------

                # Kasus 2: Bukan musik, berarti pertanyaan buat Gemini
                print("🧠 Mengirim ke Gemini...")
                jawaban = tanya_robot(final_command)
                ngomong(jawaban)
                
            else:
                # Robot cuek kalau nama tidak dipanggil
                pass

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break
        except Exception as e:
            print(f"Error Loop: {e}")

if __name__ == "__main__":
    main()