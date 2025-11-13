# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao

# Import message types and requests
from sic_framework.devices.common_naoqi.naoqi_text_to_speech import NaoqiTextToSpeechRequest
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoWakeUpRequest, NaoRestRequest

# Import libraries necessary for the demo
from time import sleep


class NaoEmotionalSpeechDemo(SICApplication):
    """
    NAO emotional speech demo application.
    Demonstrates how to make NAO express different emotions (happy, sad, angry)
    by adjusting TTS parameters like pitch, speed, and volume.
    
    Emotion parameters:
    - Happy: Higher pitch, faster speed, normal volume
    - Sad: Lower pitch, slower speed, lower volume
    - Angry: Lower pitch, faster speed, higher volume
    """
    
    def __init__(self):
        # Call parent constructor (handles singleton initialization)
        super(NaoEmotionalSpeechDemo, self).__init__()
        
        # Demo-specific initialization
        self.nao_ip = "10.0.0.181"
        self.nao = None

        self.set_log_level(sic_logging.INFO)
        
        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/path/to/logs")
        
        self.setup()
    
    def setup(self):
        """Initialize and configure the NAO robot."""
        self.logger.info("Starting NAO Emotional Speech Demo...")
        
        # Initialize the NAO robot
        self.nao = Nao(ip=self.nao_ip)
    
    def say_neutral(self, text):
        """
        Make NAO say text with neutral emotion (default parameters).
        """
        self.logger.info("Speaking with NEUTRAL emotion")
        self.nao.tts.request(NaoqiTextToSpeechRequest(text))
    def say_animated(self, text):
        """
        Make NAO say text with animated emotion.
        """
        self.logger.info("Speaking with ANIMATED emotion")
        self.nao.tts.request(NaoqiTextToSpeechRequest(text, animated=True))         # Normal to high volume
    
    def say_happy(self, text):
        """
        Make NAO say text with happy emotion.
        Happy characteristics:
        - Higher pitch (around 75-85 range)
        - Faster speed (around 120-150)
        - Normal to slightly higher volume (0.8-1.0)
        """
        self.logger.info("Speaking with HAPPY emotion")
        self.nao.tts.request(NaoqiTextToSpeechRequest(
            text,
            pitch=70,           # Higher pitch for cheerfulness
            speed=140,
            pitch_shift=3,     # Faster speech
            volume=0.9          # Normal to high volume
        ))
    
    def say_sad(self, text):
        """
        Make NAO say text with sad emotion.
        Sad characteristics:
        - Lower pitch (around 50-60 range)
        - Slower speed (around 70-85)
        - Lower volume (0.5-0.6)
        """
        self.logger.info("Speaking with SAD emotion")
        self.nao.tts.request(NaoqiTextToSpeechRequest(
            text,
            pitch=55,           # Lower pitch for sadness
            speed=90,           # Slower, more lethargic speech
            pitch_shift=1,
            volume=0.55         # Quieter voice
        ))
    
    def say_angry(self, text):
        """
        Make NAO say text with angry emotion.
        Angry characteristics:
        - Lower pitch (around 50-60 range)
        - Faster speed (around 130-160)
        - Higher volume (0.9-1.0)
        """
        self.logger.info("Speaking with ANGRY emotion")
        self.nao.tts.request(NaoqiTextToSpeechRequest(
            text,
            pitch=52,           # Lower, more aggressive pitch
            speed=150,
            pitch_shift=1,     
            volume=1.0          # Loud volume
        ))
    
    
    def wakeup(self):
        """Wake up the NAO robot."""
        self.logger.info("Waking up NAO...")
        self.nao.autonomous.request(NaoWakeUpRequest())
    
    def rest(self):
        """Put the NAO robot to rest."""
        self.logger.info("NAO going to rest...")
        self.nao.autonomous.request(NaoRestRequest())
    
    def run(self):
        """Main application logic demonstrating emotional speech."""
        try:
            # Wake up the robot
            self.wakeup()
            sleep(1)
            
            self.logger.info("Starting emotional speech demonstrations...")
            
            # Neutral emotion (baseline)
            self.say_neutral("Hello, I am Nao. Let me show you my different emotions.")
            sleep(2)

            self.say_animated("Hello, I am Nao. Let me show you my different emotions.")
            self.rest()

            # # Happy emotion
            # self.say_happy("I am so happy today! The sun is shining and everything is wonderful!")
            # sleep(3)
            
            # # Sad emotion
            # self.say_sad("I feel sad. Sometimes things don't go as planned and that makes me feel down.")
            # sleep(3)
            
            # # Angry emotion
            # self.say_angry("I am angry! This is not acceptable and I am very upset about it!")
            # sleep(3)
            
            # # Back to neutral
            # self.say_neutral("Thank you for listening to my emotional expressions. That was fun!")
            # sleep(2)
            
            # # Demonstrate the same sentence with different emotions
            # self.logger.info("Now the same sentence with different emotions...")
            # sleep(1)
            
            # sentence = "I really enjoy talking with you."
            
            # self.say_neutral(sentence)
            # sleep(2)
            
            # self.say_happy(sentence)
            # sleep(2)
            
            # self.say_sad(sentence)
            # sleep(2)
            
            # self.say_angry(sentence)
            # sleep(2)
            
            # # Final message
            # self.say_neutral("Goodbye! I hope you enjoyed my emotional speech demonstration.")
            # sleep(2)
            
            # # Put robot to rest
            # self.rest()
            
            self.logger.info("Demo completed successfully")
            
        except Exception as e:
            self.logger.error("Error in demo: {}".format(e))
        finally:
            self.logger.info("Shutting down application")
            self.shutdown()


if __name__ == "__main__":
    # Create and run the demo
    demo = NaoEmotionalSpeechDemo()
    demo.run()

