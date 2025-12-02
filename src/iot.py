import paho.mqtt.client as mqtt
import time

# --- KONFIGURASI MQTT ---
# Karena script ini jalan di Raspberry Pi yang sama dengan Mosquitto,
# kita bisa pakai 'localhost' atau '127.0.0.1'.
MQTT_BROKER = "127.0.0.1" 
MQTT_PORT = 1883
MQTT_TOPIC = "home/lampu/utama"

def kirim_perintah_lampu(state):
    """
    Mengirim perintah ON/OFF ke broker MQTT.
    state: True (Nyala) atau False (Mati)
    """
    pesan = "ON" if state else "OFF"
    
    try:
        # Buat client baru
        client = mqtt.Client()
        
        # Connect ke Broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Publish pesan
        client.publish(MQTT_TOPIC, pesan)
        print(f"📡 MQTT Publish: {MQTT_TOPIC} -> {pesan}")
        
        # Putus koneksi (karena kita cuma kirim sekali)
        client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Error MQTT: {e}")
        return False

def handle_iot_command(text):
    """
    Mengecek apakah text berisi perintah lampu.
    Returns: (is_handled, reply_text, action_function)
    """
    text = text.lower()
    
    # Keyword untuk NYALAKAN
    if any(k in text for k in ["nyalakan lampu", "hidupkan lampu", "lampu nyala", "buka lampu"]):
        def aksi_nyala():
            kirim_perintah_lampu(True)
            
        return True, "Oke, lampu dinyalakan.", aksi_nyala

    # Keyword untuk MATIKAN
    if any(k in text for k in ["matikan lampu", "padamkan lampu", "lampu mati", "tutup lampu"]):
        def aksi_mati():
            kirim_perintah_lampu(False)
            
        return True, "Siap, lampu dimatikan.", aksi_mati

    # Bukan perintah lampu
    return False, None, None