import google.generativeai as genai
import os
import socket
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# [UPDATE MODEL] Menggunakan gemini-1.5-flash (Paling Cepat & Terbaru untuk Robot)
model = genai.GenerativeModel('gemini-2.5-flash')

# [FUNGSI BARU] Cek Internet
def cek_internet():
    try:
        # Coba ping DNS Google (8.8.8.8) port 53
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
    # 1. Cek Koneksi Dulu
    if not cek_internet():
        print("❌ Koneksi Internet Putus!")
        return "ERROR_OFFLINE" # Kode rahasia buat main.py

    data_kampus = load_data_kampus()
    
    prompt = f"""
    Kamu adalah Gapin (Gajah Pintar), asisten kampus Politeknik Gajah Tunggal.
    
    DATA KAMPUS:
    {data_kampus}
    
    INSTRUKSI:
    - Jawab pertanyaan User dengan ramah, sopan, dan mencerminkan nilai 5R.
    - Jawaban harus SINGKAT dan PADAT (maksimal 2-3 kalimat) agar enak didengar lewat speaker.
    - Jika pertanyaan di luar konteks kampus, jawab dengan pengetahuan umum tapi tetap sopan.
    
    User: {pertanyaan}
    Gapin:
    """
    
    try:
        # Generate Content
        response = model.generate_content(prompt)
        return response.text.replace("*", "") # Hapus markdown bintang biar bersih
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "Maaf, otak saya sedang gangguan."