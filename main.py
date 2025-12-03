from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
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
    print("   🤖 ROBOT GAPIN (Full Body: Mata + Telinga + Mulut)")
    print("="*50 + "\n")
    
    gapin_eyes.set_mode("SPEAKING")
    ngomong("Sistem online. Panggil saya Gapin.")
    gapin_eyes.set_mode("IDLE")
    
    # Tambahkan variasi nama panggilan (termasuk typo umum STT)
    WAKE_WORDS = ["halo gapin", "halo gavin", "halo davin", "gapin", "gavin", "dapin", "davin"]

    while True:
        try:
            # 1. STANDBY (Mata IDLE)
            gapin_eyes.set_mode("IDLE")
            suara_asli = mendengar(listen_mode="wake")
            
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
                        # [FIX PENTING] Filter sampah 1 huruf (misal: "n" sisa dari "davin")
                        # Perintah dianggap valid minimal 2 huruf
                        if len(potongan) > 1:
                            final_command = potongan
                    break

            if terpanggil:
                # --- MATA MODE MENDENGAR ---
                gapin_eyes.set_mode("LISTENING") 
                
                # Jika command kosong (atau cuma sampah 1 huruf tadi), tanya balik
                if not final_command:
                    gapin_eyes.set_mode("SPEAKING")
                    ngomong("Ya?") # Respon cepat
                    gapin_eyes.set_mode("LISTENING") 
                    
                    # Masuk phase 2 (tunggu perintah sebenarnya)
                    final_command = mendengar(listen_mode="command")
                    
                    if not final_command:
                         gapin_eyes.set_mode("SPEAKING")
                         ngomong("Tidak ada perintah.")
                         continue

                print(f"📝 Command Bersih: {final_command}")
                
                # --- LOGIKA EKSEKUSI ---
                
                # 1. Cek IoT (Lampu)
                is_iot, iot_reply, iot_action = handle_iot_command(final_command)
                if is_iot:
                    gapin_eyes.set_mode("SPEAKING")
                    ngomong(iot_reply)
                    if iot_action: iot_action()
                    continue 
                
                # 2. Cek Musik
                is_music, music_reply, music_action = handle_music_command(final_command)
                if is_music:
                    gapin_eyes.set_mode("SPEAKING")
                    if music_reply: ngomong(music_reply)
                    if music_action: music_action()
                    gapin_eyes.set_mode("IDLE")
                    continue 

                # 3. Cek Exit
                if "matikan sistem" in final_command.lower():
                    gapin_eyes.set_mode("SPEAKING")
                    ngomong("Sistem dimatikan.")
                    gapin_eyes.stop()
                    break
                    
                # 4. Tanya Gemini
                print("🧠 Tanya Gemini...")
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
            print(f"\n❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
