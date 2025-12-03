import time
import random
import threading
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

class GapinEyes:
    def __init__(self):
        # Default values
        self.serial = None
        self.device = None
        self.is_running = False 
        self.current_mode = "IDLE"

        # ====== POSISI PUPIL ======
        self.posisi_pupil = [
            (0, 0),   # tengah
            (1, 0),   # kanan
            (-1, 0),  # kiri
            (0, 1),   # bawah
            (0, -1),  # atas
            (1, 1),   # kanan bawah
            (-1, -1)  # kiri atas
        ]

        # Setup Hardware (Sesuai kode Bapak)
        try:
            # Konfigurasi PIN sesuai request: port=0, device=0, gpio=noop()
            self.serial = spi(port=0, device=0, gpio=noop())
            self.device = max7219(self.serial, cascaded=1, block_orientation=0, rotate=0)
            self.device.contrast(50) # Set kecerahan (0-255)
            
            self.is_running = True
            print("👀 Mata LED Siap (Mode Pupil Bergerak)!")
            
        except Exception as e:
            print(f"⚠️ Warning: Mata LED Gagal Init. Error: {e}")
            self.device = None
            self.is_running = False

    # ====== LOGIKA GAMBAR MATA (Dari kode Bapak + Tambahan Mode) ======
    def buat_mata(self, pos_x, pos_y, keadaan="normal"):
        """Membuat pola mata dengan pupil yang bisa bergerak"""
        # Base pattern untuk mata terbuka
        mata = [
            "00111100", "01111110", "11111111", "11111111",
            "11111111", "11111111", "01111110", "00111100"
        ]
        
        pupil_size = 1
        start_x = 2 + pos_x
        start_y = 2 + pos_y
        mata_list = [list(row) for row in mata]
        
        # Gambar pupil
        for y in range(pupil_size * 2 + 1):
            for x in range(pupil_size * 2 + 1):
                pixel_y = start_y + y
                pixel_x = start_x + x
                if (0 <= pixel_x < 8 and 0 <= pixel_y < 8 and 
                    (x != pupil_size or y != pupil_size)): 
                    mata_list[pixel_y][pixel_x] = '0'
        
        # Modifikasi berdasarkan Keadaan
        if keadaan == "setengah":
            mata_list[0] = list("00000000"); mata_list[1] = list("00111100")
            mata_list[6] = list("00111100"); mata_list[7] = list("00000000")
        
        elif keadaan == "tutup":
            return ["00000000", "00000000", "00000000", "11111111", 
                    "11111111", "00000000", "00000000", "00000000"]
        
        # Mode Tambahan untuk Listening/Speaking
        elif keadaan == "senyum": # Mata ^ ^
             return ["00000000", "00000000", "11000011", "11100111",
                     "01111110", "00111100", "00000000", "00000000"]

        elif keadaan == "lebar": # Mata O O (Kaget/Fokus)
             # Mata terbuka tanpa kelopak
             return ["00111100", "01111110", "11100111", "11100111",
                     "11100111", "11100111", "01111110", "00111100"]
        
        return ["".join(row) for row in mata_list]

    def tampilkan(self, pola):
        if not self.device: return
        try:
            with canvas(self.device) as draw:
                for y, row in enumerate(pola):
                    for x, col in enumerate(row):
                        if col == "1": draw.point((x, y), fill=1)
        except:
            pass

    # ====== ANIMASI MODE ======

    def _anim_idle(self):
        """Mode Diam: Lirik kanan kiri & kedip natural"""
        # Logika Random dari kode Bapak
        rand = random.random()
        
        if rand < 0.7: # 70% Mata Bergerak
            pos = random.choice(self.posisi_pupil)
            self.tampilkan(self.buat_mata(pos[0], pos[1], "normal"))
            time.sleep(random.uniform(1.0, 2.5))
            
        elif rand < 0.9: # 20% Kedip Alami
            self.tampilkan(self.buat_mata(0, 0, "normal"))
            time.sleep(0.1)
            self.tampilkan(self.buat_mata(0, 0, "setengah"))
            time.sleep(0.08)
            self.tampilkan(self.buat_mata(0, 0, "tutup"))
            time.sleep(0.12)
            self.tampilkan(self.buat_mata(0, 0, "setengah"))
            time.sleep(0.08)
            self.tampilkan(self.buat_mata(0, 0, "normal"))
            time.sleep(0.5)
            
        else: # 10% Kedip Cepat
            self.tampilkan(self.buat_mata(0, 0, "setengah"))
            time.sleep(0.05)
            self.tampilkan(self.buat_mata(0, 0, "tutup"))
            time.sleep(0.06)
            self.tampilkan(self.buat_mata(0, 0, "normal"))
            time.sleep(0.3)

    def _anim_listening(self):
        """Mode Mendengar: Pupil bergerak kiri-kanan (Scanning)"""
        # Pupil scanning kiri kanan cepat
        for x in [-1, 0, 1, 0]:
            if self.current_mode != "LISTENING": return
            self.tampilkan(self.buat_mata(x, 0, "lebar")) 
            time.sleep(0.15)

    def _anim_speaking(self):
        """Mode Bicara: Mata Senyum & Kedip Happy"""
        self.tampilkan(self.buat_mata(0, 0, "senyum"))
        time.sleep(0.3)
        self.tampilkan(self.buat_mata(0, 0, "normal"))
        time.sleep(0.2)

    # ====== THREAD LOOP ======
    def _loop(self):
        while self.is_running and self.device:
            try:
                if self.current_mode == "IDLE":
                    self._anim_idle()
                elif self.current_mode == "LISTENING":
                    self._anim_listening()
                elif self.current_mode == "SPEAKING":
                    self._anim_speaking()
                else:
                    time.sleep(0.1)
            except Exception as e:
                # print(f"Error Animasi: {e}")
                time.sleep(1)

    # ====== KONTROL PUBLIK ======
    def start(self):
        if not self.is_running or not self.device:
            print("⚠️ Animasi mata di-skip (Hardware not found).")
            return
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def set_mode(self, mode):
        # Reset pupil ke tengah saat ganti mode biar transisi halus
        # self.tampilkan(self.buat_mata(0, 0, "normal")) 
        self.current_mode = mode

    def stop(self):
        self.is_running = False
        if self.device: 
            try: self.device.clear()
            except: pass

# Instance Global
gapin_eyes = GapinEyes()
