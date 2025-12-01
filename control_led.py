import paho.mqtt.client as mqtt
import time

broker = "localhost"  # atau IP Pi sendiri
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")

client.on_connect = on_connect
client.connect(broker, 1883, 60)
client.loop_start()

def led_on():
    client.publish("home/led/control", "ON")

def led_off():
    client.publish("home/led/control", "OFF")

# Contoh penggunaan
while True:
    print("Nyalain 3 detik...")
    led_on()
    time.sleep(3)
    print("Matikan 3 detik...")
    led_off()
    time.sleep(3)
