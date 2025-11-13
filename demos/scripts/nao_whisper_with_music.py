# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao

# Import message types and requests
from sic_framework.core.message_python2 import AudioRequest
from sic_framework.devices.common_naoqi.naoqi_text_to_speech import NaoqiTextToSpeechRequest
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoWakeUpRequest, NaoRestRequest

# Import libraries necessary for the demo
from pathlib import Path
import wave
import os

# OpenAI imports
# Note: Install with: pip install openai
try:
    from openai import OpenAI
    client = OpenAI(api_key="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")
except ImportError as e:
    print("Missing dependencies. Install with: pip install openai")
    raise e


class NaoWhisperWithMusicDemo(SICApplication):
    """
    Unified NAO demo combining OpenAI TTS and background music.
    
    Features:
    - Generate speech using OpenAI's TTS API
    - Play background music while speaking
    - Support for all OpenAI TTS parameters (voice, speed, model, instructions)
    
    Prerequisites:
    - pip install openai
    - OpenAI API key configured
    """
    
    def __init__(
        self,
        text_to_speak,
        background_music_file=None,
        voice="alloy",
        speed=1.0,
        model="gpt-4o-mini-tts",
        instructions=None,
        nao_ip="10.0.0.181"
    ):
        """
        Initialize the demo with all parameters.
        
        Args:
            text_to_speak: Text to convert to speech using OpenAI TTS
            background_music_file: Path to WAV file for background music (optional)
            voice: OpenAI voice (alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse)
            speed: Speech speed (0.25 to 4.0, default: 1.0)
            model: OpenAI model (tts-1, tts-1-hd, gpt-4o-mini-tts)
            instructions: Voice style instructions (only works with gpt-4o-mini-tts)
            nao_ip: IP address of the NAO robot
        """
        # Call parent constructor (handles singleton initialization)
        super(NaoWhisperWithMusicDemo, self).__init__()
        
        # Demo-specific initialization
        self.nao_ip = nao_ip
        self.text_to_speak = text_to_speak
        self.background_music_file = background_music_file
        self.voice = voice
        self.speed = speed
        self.model = model
        self.instructions = instructions
        
        # NAO and audio components
        self.nao = None
        self.background_sound = None
        self.background_samplerate = None
        self.speech_file_path = Path(__file__).parent / "whisper_speech.wav"
        
        self.set_log_level(sic_logging.INFO)
        
        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/path/to/logs")
        
        self.setup()
    
    def generate_speech_with_openai(self):
        """
        Generate speech using OpenAI's TTS API.
        
        Models:
        - tts-1: Fast, standard quality
        - tts-1-hd: High definition quality
        - gpt-4o-mini-tts: Latest model with instruction support
        
        Voices (gpt-4o-mini-tts):
        - alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
        
        Parameters:
        - speed: 0.25 to 4.0 (default: 1.0)
        - response_format: mp3, opus, aac, flac, wav, pcm
        """
        try:
            self.logger.info("Generating speech with OpenAI TTS API...")
            self.logger.info("Model: {}".format(self.model))
            self.logger.info("Voice: {}".format(self.voice))
            self.logger.info("Speed: {}".format(self.speed))
            self.logger.info("Text: '{}'".format(self.text_to_speak[:100] + "..." if len(self.text_to_speak) > 100 else self.text_to_speak))
            
            # Generate speech using OpenAI API with streaming response
            # Using WAV format directly to skip MP3 conversion
            with client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=self.text_to_speak,
                response_format="wav",
                instructions=self.instructions,
                speed=self.speed
            ) as response:
                response.stream_to_file(self.speech_file_path)
            
            self.logger.info("Speech generated and saved to: {}".format(self.speech_file_path))
            return True
            
        except Exception as e:
            self.logger.error("Failed to generate speech with OpenAI: {}".format(e))
            return False
    
    def verify_wav_format(self):
        """
        Verify WAV file format for NAO compatibility.
        NAO requires 16-bit PCM WAV files.
        """
        try:
            self.logger.info("Verifying WAV format...")
            
            # Check current WAV specs
            with wave.open(str(self.speech_file_path), "rb") as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                
                self.logger.info("OpenAI WAV specs:")
                self.logger.info("  sample rate: {} Hz".format(sample_rate))
                self.logger.info("  channels: {}".format(channels))
                self.logger.info("  sample width: {} bytes".format(sample_width))
            
            self.logger.info("WAV format verified - compatible with NAO")
            return True
            
        except Exception as e:
            self.logger.error("Failed to verify WAV format: {}".format(e))
            return False
    
    def load_background_music(self):
        """Load background music file if provided."""
        if self.background_music_file is None:
            self.logger.info("No background music file specified")
            return True
        
        try:
            self.logger.info("Loading background music file: {}".format(self.background_music_file))
            with wave.open(self.background_music_file, "rb") as wf:
                self.background_samplerate = wf.getframerate()
                self.background_sound = wf.readframes(wf.getnframes())
            
            self.logger.info("Background music loaded (sample rate: {})".format(self.background_samplerate))
            return True
            
        except Exception as e:
            self.logger.error("Failed to load background music file '{}': {}".format(
                self.background_music_file, e
            ))
            return False
    
    def setup(self):
        """Initialize and configure the NAO robot, generate speech, and load background music."""
        self.logger.info("Starting NAO Whisper with Music Demo...")
        
        # Initialize the NAO robot first
        self.logger.info("Connecting to NAO at {}...".format(self.nao_ip))
        self.nao = Nao(ip=self.nao_ip)
        
        # Load background music if provided
        self.load_background_music()
        
        # Generate speech with OpenAI (already in WAV format)
        if not self.generate_speech_with_openai():
            self.logger.error("Cannot proceed without generated speech")
            raise RuntimeError("Failed to generate speech with OpenAI")
        
        # Verify WAV format
        if not self.verify_wav_format():
            self.logger.error("Cannot proceed without valid WAV format")
            raise RuntimeError("Failed to verify WAV format")
        
        self.logger.info("Setup completed successfully")
    
    def play_background_music(self):
        """Start playing background music (non-blocking)."""
        if self.background_sound is not None and self.background_samplerate is not None:
            self.logger.info("Starting background music playback")
            message = AudioRequest(sample_rate=self.background_samplerate, waveform=self.background_sound)
            self.nao.speaker.request(message, block=False)
        else:
            self.logger.warning("No background music loaded, skipping playback")
    
    def say(self, text):
        """Make NAO say text using TTS."""
        self.nao.tts.request(NaoqiTextToSpeechRequest(text))
    
    def say_animated(self, text):
        """Make NAO say text with animated gestures."""
        self.nao.tts.request(NaoqiTextToSpeechRequest(text, animated=True), block=False)
    
    def play_generated_speech(self):
        """Play the generated OpenAI TTS speech through NAO's speakers."""
        try:
            self.logger.info("Loading generated speech WAV file for playback...")
            
            # Read the WAV file
            with wave.open(str(self.speech_file_path), "rb") as wf:
                samplerate = wf.getframerate()
                sound = wf.readframes(wf.getnframes())
                
                self.logger.info("Speech audio file specs:")
                self.logger.info("  sample rate: {}".format(samplerate))
                self.logger.info("  length: {} frames".format(wf.getnframes()))
                self.logger.info("  data size in bytes: {}".format(wf.getsampwidth()))
                self.logger.info("  number of channels: {}".format(wf.getnchannels()))
            
            # Send audio to NAO speakers
            self.logger.info("Sending generated speech to NAO speakers...")
            message = AudioRequest(sample_rate=samplerate, waveform=sound)
            self.nao.speaker.request(message)
            
            self.logger.info("Generated speech playback completed")
            return True
            
        except Exception as e:
            self.logger.error("Error playing generated speech on NAO: {}".format(e))
            return False
    
    def wakeup(self):
        """Wake up the NAO robot."""
        self.logger.info("Waking up NAO...")
        self.nao.autonomous.request(NaoWakeUpRequest())
    
    def rest(self):
        """Put the NAO robot to rest."""
        self.logger.info("NAO going to rest...")
        self.nao.autonomous.request(NaoRestRequest())
    
    def cleanup_files(self):
        """Clean up generated audio files."""
        try:
            if self.speech_file_path.exists():
                os.remove(self.speech_file_path)
                self.logger.info("Cleaned up generated speech WAV file")
                
        except Exception as e:
            self.logger.warning("Failed to cleanup files: {}".format(e))
    
    def run(self):
        """Main application logic."""
        try:
            self.play_background_music()
            self.say("Hello! I am a Nao robot. I am talking to you while the background music is playing.")
            # Play the generated speech on NAO
            self.play_generated_speech()
            
            self.logger.info("Demo completed successfully")
            
        except Exception as e:
            self.logger.error("Error in demo: {}".format(e))
        finally:
            # Clean up generated files
            self.cleanup_files()
            
            self.logger.info("Shutting down application")
            self.shutdown()


if __name__ == "__main__":
    # Configure TTS parameters here
    story_text = """
    Rain lashed against the window of the midnight bus, blurring the faces of the other passengers. A crumpled note sat in Leo's palm, reading only "Don't trust the woman in the red hat." He looked up, and his blood ran cold.
    """
    
    # Voice options: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
    voice = "onyx"
    
    # Speed range: 0.25 to 4.0
    speed = 1.0
    
    # Background music file (optional)
    background_music_file = "./ghost-audio.wav"
    
    # Instructions for voice style (only works with gpt-4o-mini-tts)
    instructions = """
    Voice: Deep, hushed, and enigmatic, with a slow, deliberate cadence that draws the listener in.
    Phrasing: Sentences are short and rhythmic, building tension with pauses and carefully placed suspense.
    Punctuation: Dramatic pauses, ellipses, and abrupt stops enhance the feeling of unease and anticipation.
    """
    
    # Model options: tts-1, tts-1-hd, gpt-4o-mini-tts
    model = "gpt-4o-mini-tts"
    
    # NAO IP address
    nao_ip = "10.0.0.181"
    
    # Create and run the demo
    demo = NaoWhisperWithMusicDemo(
        text_to_speak=story_text,
        background_music_file=background_music_file,
        voice=voice,
        speed=speed,
        model=model,
        instructions=instructions,
        nao_ip=nao_ip
    )
    
    # Example usage: Say intro, play background music, then play generated speech
    demo.say("Hello! I am a Nao robot. I am going to tell a spooky story")
    demo.run()

