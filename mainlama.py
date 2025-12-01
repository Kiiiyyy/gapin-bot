from src.brain import tanya_robot
from src.speaking import ngomong
from src.hearing import mendengar
from fuzzywuzzy import fuzz
import os
import time


# =============================
#  LIST VARIASI WAKE WORD
# =============================
WAKE_WORDS = [
    "gapin", "gafin", "gaphin", "gappen", "gaping",
    "gabin", "gaben", "gavin", "kapin", "kafin",
    "gupin", "gopin", "ga pin", "ga fin"
]

WAKE_THRESHOLD = 80  # semakin tinggi = semakin ketat


def is_wake_word(text):
    """Cek apakah text mirip wake word (bagian depan kalimat)."""

    words = text.lower().split()

    if len(words) == 0:
        return False, ""

    first_word = words[0]  # hanya cek kata pertama

    for w in WAKE_WORDS:
        score = fuzz.ratio(first_word, w)
        if score >= WAKE_THRESHOLD:
            return True, w

    return False, ""


def bersihkan_pertanyaan(teks, wake_word):
    """Buang wake word di depan kalimat tanpa merusak konten."""
    teks = teks.lower().strip()

    # Jika wake word ada di awal kalimat → hapus
    if teks.startswith(wake_word):
        teks = teks[len(wake_word):].strip()

    # Jika masih ada koma/tanda baca
    teks = teks.lstrip(",. ")

    return teks


def main():

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Error: API Key Gemini belum diisi.")
        return

    print("==========================================")
    print("🤖 ROBOT KAMPUS (Mode Wake Word + Fuzzy)")
    print("Ucapkan: 'Gapin ... (pertanyaan)'")
    print("Tekan Ctrl+C untuk berhenti.")
    print("==========================================")

    ngomong("Sistem siap. Silakan panggil saya dengan Gapin.")

    while True:
        try:
            # 1. Dengar suara
            suara_asli = mendengar()

            if not suara_asli:
                continue

            suara_lower = suara_asli.lower()
            print(f"🎧 Terdengar: {suara_asli}")

            # 2. Uji wake word
            terpanggil, ww = is_wake_word(suara_lower)

            if terpanggil:
                print(f"✅ Wake word cocok: {ww}")
                
                # 3. Bersihkan kalimat dari wake word
                pertanyaan = bersihkan_pertanyaan(suara_lower, ww)

                # Jika cuma memanggil "Gapin"
                if not pertanyaan.strip():
                    ngomong("Ya, ada yang bisa saya bantu?")
                    continue

                # 4. Proses perintah
                jawaban = tanya_robot(pertanyaan)
                ngomong(jawaban)

            else:
                print(f"❌ Diabaikan (bukan panggilan): {suara_asli}")

        except KeyboardInterrupt:
            print("\nProgram dihentikan.")
            break


if __name__ == "__main__":
    main()
