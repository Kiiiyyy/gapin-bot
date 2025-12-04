import time
import random
import threading
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

class GapinEyes:
    def __init__(self):
        self.serial = None
        self.device = None
        self.is_running = False 
        self.current_mode = "IDLE"
        self.posisi_pupil = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]

        try:
            self.serial = spi(port=0, device=0, gpio=noop(), max_speed_hz=500000)
            self.device = max7219(self.serial, cascaded=1, block_orientation=-90, rotate=0)
            self.device.contrast(20)
            self.device.hide(); self.device.clear(); self.device.show()
            self.is_running = True
            print("👀 Mata LED Siap!")
        except Exception as e:
            print(f"⚠️ Mata LED Skip: {e}")
            self.device = None
            self.is_running = False

    def buat_mata(self, pos_x, pos_y, keadaan="normal"):
        mata = [
            "00111100", "01111110", "11111111", "11111111",
            "11111111", "11111111", "01111110", "00111100"
        ]
        pupil_size = 1
        start_x = 2 + pos_x
        start_y = 2 + pos_y
        mata_list = [list(row) for row in mata]
        
        for y in range(pupil_size * 2 + 1):
            for x in range(pupil_size * 2 + 1):
                px, py = start_x + x, start_y + y
                if 0 <= px < 8 and 0 <= py < 8 and (x != pupil_size or y != pupil_size): 
                    mata_list[py][px] = '0'
                    
        if keadaan == "setengah":
            mata_list[0] = list("00000000"); mata_list[1] = list("00111100")
            mata_list[6] = list("00111100"); mata_list[7] = list("00000000")
        elif keadaan == "tutup":
            return ["00000000"]*8
        elif keadaan == "senyum": 
             return ["00000000", "00000000", "11000011", "11100111", "01111110", "00111100", "00000000", "00000000"]
        elif keadaan == "lebar": 
             return ["00111100", "01111110", "11100111", "11100111", "11100111", "11100111", "01111110", "00111100"]
        elif keadaan == "pikir": 
             return ["00000000", "01111110", "11111111", "11111111", "11111111", "01111110", "00000000", "00000000"]
        # [BARU] Mata Mati / Error (Tanda Silang X)
        elif keadaan == "mati":
             return ["10000001", "01000010", "00100100", "00011000", "00011000", "00100100", "01000010", "10000001"]

        return ["".join(row) for row in mata_list]

    def tampilkan(self, pola):
        if not self.device: return
        try:
            with canvas(self.device) as draw:
                for y, row in enumerate(pola):
                    for x, col in enumerate(row):
                        if col == "1": draw.point((x, y), fill=1)
        except: pass

    # ====== ANIMASI MODE ======
    def _anim_idle(self):
        rand = random.random()
        if rand < 0.7: 
            pos = random.choice(self.posisi_pupil)
            self.tampilkan(self.buat_mata(pos[0], pos[1], "normal"))
            time.sleep(random.uniform(1.0, 2.5))
        else: 
            self.tampilkan(self.buat_mata(0, 0, "tutup")); time.sleep(0.1)
            self.tampilkan(self.buat_mata(0, 0, "normal")); time.sleep(0.5)

    def _anim_listening(self):
        for x in [-1, 0, 1, 0]:
            if self.current_mode != "LISTENING": return
            self.tampilkan(self.buat_mata(x, 0, "lebar")) 
            time.sleep(0.12)

    def _anim_processing(self):
        posisi_mikir = [(-1, -1), (0, -1), (1, -1), (0, -1)]
        for pos in posisi_mikir:
            if self.current_mode != "PROCESSING": return
            self.tampilkan(self.buat_mata(pos[0], pos[1], "pikir"))
            time.sleep(0.15)

    def _anim_speaking(self):
        self.tampilkan(self.buat_mata(0, 0, "senyum")); time.sleep(0.2)
        self.tampilkan(self.buat_mata(0, 1, "senyum")); time.sleep(0.2)

    # [BARU] Animasi Offline
    def _anim_offline(self):
        self.tampilkan(self.buat_mata(0, 0, "mati"))
        time.sleep(0.5) # Kedip lambat tanda error
        self.tampilkan(self.buat_mata(0, 0, "tutup"))
        time.sleep(0.5)

    def _loop(self):
        while self.is_running and self.device:
            try:
                if self.current_mode == "IDLE": self._anim_idle()
                elif self.current_mode == "LISTENING": self._anim_listening()
                elif self.current_mode == "PROCESSING": self._anim_processing()
                elif self.current_mode == "SPEAKING": self._anim_speaking()
                elif self.current_mode == "OFFLINE": self._anim_offline() # <--- Tambahan
                else: time.sleep(0.1)
            except Exception: time.sleep(1)

    def start(self):
        if not self.is_running or not self.device: return
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def set_mode(self, mode):
        self.current_mode = mode

    def stop(self):
        self.is_running = False
        if self.device: 
            try: self.device.clear()
            except: pass

gapin_eyes = GapinEyes()