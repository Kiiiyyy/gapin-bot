import edge_tts
import pygame
import asyncio
import os

# Init Audio Mixer
pygame.mixer.init()

async def generate_voice(text):
    # Menggunakan suara cewek Indonesia (Gadis)
    communicate = edge_tts.Communicate(text, "id-ID-GadisNeural")
    await communicate.save("temp_voice.mp3")

def ngomong(text):
    print(f"🤖 Robot: {text}")
    
    # Generate MP3 (perlu wrap async karena edge-tts itu asinkronus)
    asyncio.run(generate_voice(text))
    
    # Play Audio
    try:
        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()
        
        # Tunggu sampai suara selesai
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # Hapus file temp biar bersih (opsional, kadang error di windows/linux kalau masih di-lock)
        # os.remove("temp_voice.mp3") 
    except Exception as e:
        print(f"Error Audio: {e}")
