import edge_tts
import pygame
import asyncio
import os
import time
from src.utils import silence_alsa  # <--- Import Peredam

# Init Audio Mixer dengan Peredam
try:
    with silence_alsa():
        pygame.mixer.init()
except Exception as e:
    # Error silent, tapi tetap jalan kalau cuma warning
    pass

async def generate_voice(text, filename):
    """Generate voice audio file"""
    try:
        # Menggunakan suara cewek Indonesia (Gadis)
        communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural", rate="+10%", pitch="+50Hz")
        await communicate.save(filename)
        return True
    except Exception as e:
        print(f"❌ Error generating voice: {e}")
        return False

def ngomong(text):
    """Text-to-speech function"""
    if not text:
        return
        
    print(f"🤖 Robot: {text}")
    
    timestamp = int(time.time())
    temp_filename = f"temp_voice_{timestamp}.mp3"
    
    try:
        success = asyncio.run(generate_voice(text, temp_filename))
        if not success: return
            
        # Play Audio
        with silence_alsa(): # Bungkam log saat load musik
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        time.sleep(0.1)
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except: pass
            
    except Exception as e:
        print(f"❌ Error Audio: {e}")