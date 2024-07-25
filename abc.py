import azure.cognitiveservices.speech as speechsdk

# Azure Speech configuration
speech_key = "646725f01b944b1f922eb56a3ba5f5db"
service_region = "australiaeast"

# Create a speech configuration using the subscription key and region
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set the voice name (optional)
voice_name = "en-US-JennyNeural"
speech_config.speech_synthesis_voice_name = voice_name

# Create a speech synthesizer
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Set the text to synthesize
text = "This is a test to check if Azure Speech is working correctly."

# Synthesize speech
result = speech_synthesizer.speak_text_async(text).get()

# Check the synthesis result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized successfully.")
else:
    print("Speech synthesis failed.")