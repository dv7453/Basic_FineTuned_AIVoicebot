import assemblyai as aai
from elevenlabs import generate, stream, voices
from openai import OpenAI

class AI_Assistant:
    def __init__(self):
        aai.settings.api_key = "Your AssemblyAI API Key"
        self.openai_client = OpenAI(api_key = "Your OpenAI API Key")
        self.elevenlabs_api_key = "Your ElevenLabs API Key"

        self.transcriber = None
        self.full_transcript = [
            {"role":"system", "content": "You are working at a call center. Be resourceful and efficient."},
        ]
        self.voice_name = self.get_valid_voice()

    def get_valid_voice(self):
        # List available voices from ElevenLabs
        available_voices = voices(api_key=self.elevenlabs_api_key)
        print("Available voices:")
        for voice in available_voices:
            print(voice['name'])
        
        # Choose a valid voice, or return a default one if available
        return available_voices[0]['name'] if available_voices else "Default Voice"

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate = 16000,
            on_data = self.on_data,
            on_error = self.on_error,
            on_open = self.on_open,
            on_close = self.on_close,
            end_utterance_silence_treshold = 1000
        )

        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate = 16000)
        self.transcriber.stream(microphone_stream)

    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")

    def on_error(self, error: aai.RealtimeError):
        print("An error occured:", error)
        return

    def on_close(self):
        #print("Closing Session")
        return

###### Step 3: Pass real-time transcript to OpenAI ######
    
    def generate_ai_response(self, transcript):
        self.stop_transcription()

        self.full_transcript.append({"role":"user", "content": transcript.text})
        print(f"\nPatient: {transcript.text}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"\nReal-time transcription: ", end="\r\n")

###### Step 4: Generate audio with ElevenLabs ######
        
    def generate_audio(self, text):
        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice=self.voice_name,  # Use the valid voice name
            stream=True
        )

        stream(audio_stream)

greeting = "Thank you for calling Vancouver dental clinic. My name is Sandy, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()
