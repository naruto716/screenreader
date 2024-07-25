import threading
import tkinter as tk
import customtkinter as ctk
import azure.cognitiveservices.speech as speechsdk
import pyperclip
from pynput import keyboard
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import simpleaudio as sa


# Azure Speech configuration
speech_key = "YOUR_KEY"
service_region = "australiaeast"

# Create a speech configuration using the subscription key and region
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Create a threadpool with a maximum of 5 threads
threadpool = ThreadPoolExecutor(max_workers=5)

# Create a cache for synthesized speech
speech_cache = OrderedDict()
MAX_CACHE_SIZE = 10


def read_text():
    text = text_box.get("1.0", "end-1c")
    if text.strip():
        threadpool.submit(synthesize_speech, text)


def read_clipboard():
    text = pyperclip.paste()
    # Set text_box
    text_box.delete("1.0", "end")
    text_box.insert("1.0", text)

    if text.strip():
        threadpool.submit(synthesize_speech, text)


def play_audio(audio_data):
    wave_obj = sa.WaveObject(audio_data, num_channels=1, bytes_per_sample=2, sample_rate=16000)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing


cache_lock = threading.Lock()


def synthesize_speech(text):
    key = voice_var.get() + "_" + text
    if key in speech_cache:
        audio_data = speech_cache[key]
        play_audio(audio_data)
    else:
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = synthesizer.speak_text_async(text).get()
        audio_data = result.audio_data
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesis failed. Potentially API key is bad.")

        if len(speech_cache) >= 10:
            speech_cache.popitem(last=False)  # Remove the oldest item
        with cache_lock:
            speech_cache[key] = audio_data


# Track the state of the control key and count of 'C' presses
ctrl_pressed = False
c_press_count = 0

def on_press(key):
    global ctrl_pressed, c_press_count
    try:
        # Check if the key is a control character
        if key.char:
            # Convert control character to its corresponding ordinal
            if ord(key.char) == 3:  # Control+C is \u0003
                if ctrl_pressed:
                    c_press_count += 1
                    if c_press_count == 2:
                        read_clipboard()
    except AttributeError:
        # Check if the key is the control key
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
            c_press_count = 0  # Reset count whenever Ctrl is pressed

def on_release(key):
    global ctrl_pressed, c_press_count
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = False
        c_press_count = 0  # Reset count on Ctrl release


def change_voice(choice):
    voice_name = voice_var.get()
    speech_config.speech_synthesis_voice_name = voice_name


# Set up the main window
window = ctk.CTk()
window.title("Text-to-Speech App")
window.geometry("400x500")

# Title
title = ctk.CTkLabel(window, text="Text-to-Speech App", font=("Sans-serif", 16))
title.pack(pady=(10, 5))

# Text box
text_box = ctk.CTkTextbox(window, width=350, height=200)
text_box.pack(pady=10, padx=20, expand=True, fill='both')

# Read button
read_button = ctk.CTkButton(window, text="Read Text", command=read_text)
read_button.pack(pady=5, padx=70, fill='x')

# Voice selection
voice_var = tk.StringVar(value="de-DE-RalfNeural")
voice_options = ["en-GB-RyanNeural", "en-GB-EthanNeural", "en-GB-ElliotNeural", "en-GB-NoahNeural", "en-GB-ThomasNeural", "zh-CN-YunxiNeural", "zh-CN-YunyangNeural", "de-DE-ConradNeural", "de-DE-BerndNeural", "de-DE-RalfNeural"]
voice_dropdown = ctk.CTkOptionMenu(window, variable=voice_var, values=voice_options, command=change_voice,
                                   anchor="center")
voice_dropdown.pack(pady=(5, 10), padx=70, fill='x')

# Set initial voice
speech_config.speech_synthesis_voice_name = voice_var.get()

# Keyboard listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Run the app
window.mainloop()

# Shutdown the threadpool when the app is closed
threadpool.shutdown()
