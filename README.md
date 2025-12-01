# gapin-bot

## Setup
```
pip install -r requirements.txt
```
Isi `.env` dengan `GOOGLE_API_KEY=<api key Gemini>`.
Pastikan `ffmpeg` terpasang agar konversi audio berjalan lancar.

## Menjalankan
```
python main.py
```

## Fitur Musik
- Simpan file `.mp3/.wav/.ogg/.flac` di folder `lagu/`.
- Contoh perintah: “Gapin putar lagu hymne politeknik”, “Gapin stop lagu”, “Gapin daftar lagu yang ada”.
- Jika judul tidak disebut, Gapin memutar lagu pertama di folder tersebut.