import speech_recognition as sr

print("Mencari microphone...")
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"ID: {index} - Nama: {name}")
