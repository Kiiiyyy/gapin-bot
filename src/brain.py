import google.generativeai as genai
import os
import socket
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# Gunakan model Flash (Cepat)
model = genai.GenerativeModel('gemini-2.5-flash')

def cek_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def load_data_kampus():
    try:
        path = os.path.join("data", "info_kampus.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Belum ada data info kampus."

def tanya_robot(pertanyaan):
    if not cek_internet():
        print("❌ Koneksi Internet Putus!")
        return "ERROR_OFFLINE"

    data_kampus = load_data_kampus()
    
    # [UPDATE PROMPT: KAMPUS + PENGETAHUAN UMUM]
    prompt = f"""
    Kamu adalah Gapin (Gajah Pintar), asisten cerdas kebanggaan Politeknik Gajah Tunggal.
    
    TUGAS UTAMA:
    1. Menjawab pertanyaan seputar KAMPUS (Prioritas Utama) menggunakan data di bawah.
    2. Menjawab pertanyaan UMUM & AKADEMIK (Matematika, Sejarah, Sains, Teknologi, Bahasa, dll) menggunakan pengetahuanmu sendiri.
    
    DATA KAMPUS (Gunakan ini jika ditanya soal Poltek GT):
    {data_kampus}
    
    INSTRUKSI SUARA (TTS) - WAJIB DIKURUTI:
    1. HINDARI simbol aneh (*, #, -, >). Jangan pakai markdown.
    2. UBAH simbol matematika jadi kata (contoh: '/' jadi 'atau', '+' jadi 'tambah', '=' jadi 'sama dengan').
    3. HINDARI singkatan yang tidak umum.
    
    ATURAN MENJAWAB:
    1. Jika pertanyaan soal KAMPUS (Visi Misi, 5R, Pancasetya, 9 budi politeknik gt): Jawab LENGKAP dan UTUH sesuai teks. Gunakan tanda koma untuk jeda.
    2. Jika pertanyaan soal MATEMATIKA/SAINS: Jelaskan dengan singkat langkahnya atau langsung jawab hasilnya jika sederhana.
    3. Jika pertanyaan UMUM (Sejarah, Geografi, dll): Jawab dengan ringkas, padat, dan informatif (maksimal 2-3 kalimat, kecuali diminta menjelaskan detail).
    4. Selalu jawab dengan nada ramah, sopan, dan cerdas.
    
    User: {pertanyaan}
    Gapin:
    """
    
    try:
        response = model.generate_content(prompt)
        # Bersihkan sisa simbol markdown yang mungkin lolos
        text_bersih = response.text.replace("*", "").replace("#", "").replace("_", "")
        return text_bersih
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "Maaf, otak saya sedang gangguan."