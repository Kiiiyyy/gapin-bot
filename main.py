from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
from src.music import handle_music_command
from fuzzywuzzy import fuzz
import os


# =============================
#  LIST VARIASI WAKE WORD
# =============================
WAKE_WORDS = [
    "gapin", "gafin", "gaphin", "gappen", "gaping",
    "gabin", "gaben", "gavin", "kapin", "kafin",
    "gupin", "gopin", "ga pin", "ga fin"
]

WAKE_THRESHOLD = 80  # semakin tinggi = semakin ketat
MAX_COMMAND_ATTEMPTS = 1


def is_wake_word(text):
    """Cek apakah text mirip wake word (bagian depan kalimat)."""
    words = text.lower().split()

    if len(words) == 0:
        return False

    first_word = words[0]  # hanya cek kata pertama

    for w in WAKE_WORDS:
        score = fuzz.ratio(first_word, w)
        if score >= WAKE_THRESHOLD:
            return True

    return False


def dengarkan_perintah():
    """Dengarkan perintah setelah dipanggil."""
    for attempt in range(MAX_COMMAND_ATTEMPTS):
        print(f"🎙️ Mendengarkan perintah (percobaan {attempt+1})...")
        perintah = mendengar(listen_mode="command")
        if perintah:
            return perintah

        if attempt < MAX_COMMAND_ATTEMPTS - 1:
            print("😶 Tidak terdengar perintah, mencoba lagi...")

    return None


def main():

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi.")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS (Mode Wake Word + Fuzzy)")
    print("Cara pakai: Ucapkan 'Gapin', lalu tunggu konfirmasi")
    print("Setelah Gapin menjawab, baru ucapkan perintah Anda")
    print("Tekan Ctrl+C untuk berhenti.")
    print("==========================================")

    ngomong("Sistem siap. Silakan panggil saya dengan Gapin.")

    while True:
        try:
            # 1. Dengar wake word ("Gapin")
            suara_asli = mendengar(listen_mode="wake")

            if not suara_asli:
                continue

            suara_lower = suara_asli.lower().strip()
            print(f"🎧 Terdengar: {suara_asli}")

            # 2. Cek apakah ada wake word
            terpanggil = is_wake_word(suara_lower)

            if terpanggil:
                print("✅ Wake word terdeteksi!")
                
                # 3. Langsung jawab (best practice: confirm dulu)
                ngomong("Ya, ada yang bisa saya bantu?")
                
                # 4. Baru dengar perintah setelah jawab
                pertanyaan = dengarkan_perintah()

                if not pertanyaan:
                    print("😶 Tidak ada perintah yang tertangkap.")
                    ngomong("Aku tidak menangkap perintah. Panggil aku lagi ya.")
                    continue

                pertanyaan = pertanyaan.lower().strip()
                print(f"📝 Perintah: {pertanyaan}")

                # 5. Proses perintah
                handled, music_response, music_action = handle_music_command(pertanyaan)

                if handled:
                    if music_response:
                        ngomong(music_response)
                    if music_action:
                        try:
                            music_action()
                        except Exception as err:
                            print(f"❌ Gagal memutar lagu: {err}")
                            ngomong("Maaf, aku gagal memutar lagu itu.")
                    continue

                # 6. Jika bukan perintah musik, tanya ke brain
                jawaban = tanya_robot(pertanyaan)
                ngomong(jawaban)

            else:
                print(f"❌ Diabaikan (bukan panggilan): {suara_asli}")

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break


if __name__ == "__main__":
    main()
