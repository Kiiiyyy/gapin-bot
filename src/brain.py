import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API KEY
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def load_data_kampus():
    try:
        # Baca file info_kampus.txt
        path = os.path.join("data", "info_kampus.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Belum ada data info kampus."

def tanya_robot(pertanyaan):
    # 1. Ambil data kampus (Simple RAG - Context Injection)
    data_kampus = load_data_kampus()
    
    # 2. Buat Prompt
    prompt = f"""
    Kamu adalah Robot Asisten Kampus yang ramah dan pintar.
    
    INFORMASI KAMPUS:
    {data_kampus}
    
    INSTRUKSI:
    - Jawab pertanyaan User berdasarkan INFORMASI KAMPUS di atas.
    - Jika pertanyaan soal Matematika atau Pengetahuan Umum (tidak ada di info kampus), jawab langsung dengan pengetahuanmu sendiri.
    - Jawaban harus SINGKAT, PADAT, dan JELAS (maksimal 2-3 kalimat) karena akan diubah menjadi suara.
    
    User: {pertanyaan}
    Robot:
    """
    
    # 3. Kirim ke Gemini
    try:
        response = model.generate_content(prompt)
        return response.text.replace("*", "") # Hapus bintang markdown biar enak didengar
    except Exception as e:
        print(f"\n[ERROR GEMINI]: {e}")  # <--- Tambahkan baris ini
        return "Maaf, koneksi otak saya sedang gangguan."
