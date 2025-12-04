from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import gaphin_listen 
from src.music import handle_music_command
from src.iot import handle_iot_command
from src.eyes import gapin_eyes
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  FATAL ERROR: API Key Gemini belum diisi!")
        return

    # --- START MATA ---
    print("👀 Menghidupkan Mata...")
    gapin_eyes.start()
    gapin_eyes.set_mode("IDLE")
    # ------------------

    print("\n" + "="*50)
    print("   🤖 ROBOT GAPIN (Asisten Kampus Poltek GT)")
    print("="*50 + "\n")
    
    gapin_eyes.set_mode("SPEAKING")
    # [UPDATE] Sapaan lebih ramah & beridentitas kampus
    ngomong("Halo! Saya Gapin, asisten pintar Politeknik Gajah Tunggal. panggil saya : Halo gapin")
    gapin_eyes.set_mode("IDLE")
    
    # [UPDATE] Wake Words difokuskan ke variasi "Halo Gapin"
    # Kita tetap simpan variasi typo (gavin, davin) biar robot gak budeg kalau Google salah dengar
    
    WAKE_WORDS = ["halo gapin", "halo gavi", "halo gavin", "halo davin", "gapin", "gavin", "halo dapin", "davin", "halo kevin", "halo ngapain"]

    # --- FUNGSI BANTUAN UNTUK TELINGA ---
    def update_eye_status(status):
        if status == "LISTENING":
            gapin_eyes.set_mode("LISTENING")
        elif status == "PROCESSING":
            gapin_eyes.set_mode("PROCESSING")
        elif status == "IDLE":
            gapin_eyes.set_mode("IDLE")

    while True:
        try:
            # 1. STANDBY PHASE (WAKE MODE)
            gapin_eyes.set_mode("IDLE")
            
            # Mode raw/cepat untuk standby
            suara_asli = gaphin_listen(mode="cmd", quick_calib=False) 
            
            if not suara_asli: continue
            
            suara_lower = suara_asli.lower()
            
            # 2. PROSES TRIGGER
            terpanggil = False
            final_command = ""

            for trigger in WAKE_WORDS:
                if trigger in suara_lower:
                    terpanggil = True
                    parts = suara_lower.split(trigger, 1)
                    if len(parts) > 1:
                        potongan = parts[1].strip()
                        if len(potongan) > 1:
                            final_command = potongan
                    break

            if terpanggil:
                # --- MATA MODE MENDENGAR ---
                gapin_eyes.set_mode("LISTENING") 
                
                # Jika cuma panggil nama ("Halo Gapin"), tanya balik dengan ramah
                if not final_command:
                    gapin_eyes.set_mode("SPEAKING")
                    # [UPDATE] Respon ramah
                    ngomong("Iya, Gapin di sini.")
                    
                    # PHASE 2 (COMMAND MODE)
                    final_command = gaphin_listen(
                        mode="cmd", 
                        quick_calib=True,
                        on_phase_change=update_eye_status 
                    )
                    
                    if not final_command:
                         gapin_eyes.set_mode("SPEAKING")
                         # [UPDATE] Respon kalau user diam saja
                         ngomong("Sepertinya suaranya putus-putus. Panggil Gapin lagi nanti ya.")
                         continue

                print(f"📝 Command: {final_command}")
                
                # --- LOGIKA EKSEKUSI ---
                
                # Sebelum menjawab, set mata ke PROCESSING sebentar
                gapin_eyes.set_mode("PROCESSING")

                # 1. IoT
                is_iot, iot_reply, iot_action = handle_iot_command(final_command)
                if is_iot:
                    gapin_eyes.set_mode("SPEAKING")
                    ngomong(iot_reply)
                    if iot_action: iot_action()
                    continue 
                
                # 2. Musik
                is_music, music_reply, music_action = handle_music_command(final_command)
                if is_music:
                    gapin_eyes.set_mode("SPEAKING")
                    if music_reply: ngomong(music_reply)
                    if music_action: music_action()
                    gapin_eyes.set_mode("IDLE")
                    continue 

                # 3. Exit
                if "matikan sistem" in final_command.lower() or "matikan system" in final_command.lower():
                    gapin_eyes.set_mode("SPEAKING")
                    # [UPDATE] Salam perpisahan ala kampus
                    ngomong("Baik, Gapin istirahat dulu. Semangat kuliahnya dan jangan lupa 5R ya!")
                    gapin_eyes.stop()
                    break
                    
                # 4. Gemini (Otak)
                # print("🧠 Tanya Gemini...") 
                jawaban = tanya_robot(final_command)
                
                gapin_eyes.set_mode("SPEAKING")
                ngomong(jawaban)
                
            else:
                pass

        except KeyboardInterrupt:
            print("\n🛑 Stop.")
            gapin_eyes.stop()
            break
        except Exception as e:
            print(f"\n❌ Error Main Loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()