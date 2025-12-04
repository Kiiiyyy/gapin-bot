import edge_tts
import pygame
import asyncio
import os
import time

# Init Audio Mixer
pygame.mixer.init()

async def generate_voice(text, filename):
    """
    Generate voice audio file
    """
    try:
        # Menggunakan suara cewek Indonesia (Gadis)
        communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
	# communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
        await communicate.save(filename)
        return True
    except Exception as e:
        print(f"❌ Error generating voice: {e}")
        return False

def ngomong(text):
    """
    Text-to-speech function
    """
    if not text:
        return
        
    print(f"🤖 Robot: {text}")
    
    # Generate unique filename to avoid conflicts
    timestamp = int(time.time())
    temp_filename = f"temp_voice_{timestamp}.mp3"
    
    try:
        # Generate MP3
        success = asyncio.run(generate_voice(text, temp_filename))
        
        if not success:
            return
            
        # Play Audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Wait until audio finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Stop and unload the music
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        # Clean up: delete the temp file after a short delay
        time.sleep(0.5)  # Wait a bit before deleting
        try:
            os.remove(temp_filename)
            print(f"🗑️ File {temp_filename} dihapus")
        except Exception as e:
            print(f"⚠️ Tidak bisa hapus file: {e}")
            
    except Exception as e:
        print(f"❌ Error playing audio: {e}")
