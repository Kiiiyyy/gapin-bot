from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
from src.music import handle_music_command
from src.iot import handle_iot_command  # Import modul IOT
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Cek API Keyhttp://jeki-iot_potensio.mdbghttp://jeki-iot_potensio.mdbgo.io/set_status.php?led=2&status=1o.io/set_status.php?led=2&status=1
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  FATAL ERROR: API Key Gemini belum diisi!")
        return

    print("\n" + "="*50)
    print("   🤖 ROBOT GAPIN (IoT + Music Edition)")
    print("   -----------------------------------")
    print("   💡 IoT Cmd    : 'Nyalakan lampu', 'Matikan lampu'")
    print("   🎵 Music Cmd  : 'Putar lagu X', 'Stop lagu'")
    print("   ✅ Wake Word  : 'Halo Gapin', 'Gapin'")
    print("="*50 + "\n")
    
    ngomong("Sistem online. Panggil aku Gapin ya")
    
    # List panggilan
    WAKE_WORDS = ["gapin", "gavin", "dapin", "gapin", "davin", "davii", "daviin", "davi"]

    while True:
        try:
            # 1. Mendengar (Standby)
            suara_asli = mendengar(listen_mode="wake")
            if not suara_asli: continue
            
            suara_lower = suara_asli.lower()
            
            # 2. Cek Trigger Wake Word
            terpanggil = False
            final_command = ""

            for trigger in WAKE_WORDS:
                if trigger in suara_lower:
                    terpanggil = True
                    print(f"\n✅ Trigger: '{trigger}'")
                    # Potong kalimat: ambil teks setelah nama panggilan
                    parts = suara_lower.split(trigger, 1)
                    if len(parts) > 1:
                        final_command = parts[1].strip()
                    break

            if terpanggil:
                # Jika cuma panggil nama ("Gapin"), tanya balik
                if not final_command:
                    ngomong("Ya, gapin disini.")
                    final_command = mendengar(listen_mode="command")
                    if not final_command:
                         ngomong("Tidak ada perintah, standby.")
                         continue

                print(f"📝 Command: {final_command}")
                
                # --- PRIORITAS 1: CEK IOT (LAMPU) ---
                is_iot, iot_reply, iot_action = handle_iot_command(final_command)
                if is_iot:
                    ngomong(iot_reply) # Jawab "Oke dinyalakan"
                    if iot_action:
                        iot_action()   # Kirim sinyal MQTT
                    continue # Skip sisanya, kembali standby
                
                # --- PRIORITAS 2: CEK MUSIK ---
                is_music, music_reply, music_action = handle_music_command(final_command)
                if is_music:
                    if music_reply: ngomong(music_reply)
                    if music_action: music_action()
                    continue 

                # --- PRIORITAS 3: GEMINI (OTAK) ---
                # Cek command exit dulu
                if "matikan sistem" in final_command.lower():
                    ngomong("Sistem dimatikan. Dadah.")
                    break
                    
                print("🧠 Tanya Gemini...")
                jawaban = tanya_robot(final_command)
                ngomong(jawaban)

        except KeyboardInterrupt:
            print("\n🛑 Stop.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()