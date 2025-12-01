# gapin-bot

## Setup
```
pip install -r requirements.txt
```
Isi `.env` dengan `GOOGLE_API_KEY=<api key Gemini>`.
Pastikan `ffmpeg` terpasang agar konversi audio berjalan lancar.
Install paket system yang dibutuhkan mic (ALSA/PulseAudio) dan izinkan akses (`sudo usermod -aG audio $USER` atau `setcap cap_net_raw+ep $(which python)` bila perlu).

### Audio Input
- Engine mendengar menggunakan PyAudio + WebRTC VAD (paket `webrtcvad`).
- Default memanfaatkan perangkat mic pertama; set variabel `MIC_DEVICE_INDEX=<angka>` jika ingin memilih device tertentu (lihat daftar lewat `python -m speech_recognition`).
- Mode wake dan command otomatis berhenti ketika tidak ada suara sehingga respon terasa instan.

## Menjalankan
```
python main.py
```

## Fitur Musik
- Simpan file `.mp3/.wav/.ogg/.flac` di folder `lagu/`.
- Contoh perintah: “Gapin putar lagu hymne politeknik”, “Gapin stop lagu”, “Gapin daftar lagu yang ada”.
- Jika judul tidak disebut, Gapin memutar lagu pertama di folder tersebut.