# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao
from sic_framework.devices.nao import NaoqiTextToSpeechRequest

# Import libraries necessary for the demo
import time


class NaoAnimatedSpeechDemo(SICApplication):
    """
    NAO Animated Speech demo application.
    Demonstrates the ALAnimatedSpeech module with various instructions:
    - Animations (^start, ^run, ^wait, ^stop)
    - Speaking movement modes (^mode)
    - Tagged animations (^startTag, ^waitTag)
    """
    
    def __init__(self):
        # Call parent constructor (handles singleton initialization)
        super(NaoAnimatedSpeechDemo, self).__init__()
        
        # Demo-specific initialization
        self.nao_ip = "10.0.0.181"
        self.nao = None

        self.set_log_level(sic_logging.INFO)
        
        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/path/to/logs")
        
        self.setup()
    
    def setup(self):
        """Initialize and configure the NAO robot."""
        self.logger.info("Starting NAO Animated Speech Demo...")
        
        # Initialize the NAO robot
        self.nao = Nao(ip=self.nao_ip)
    
    def run(self):
        """Main application logic demonstrating animated speech."""
        try:
            self.logger.info("Testing Animated Speech with different instructions...")
            
            # Example 1: Simple animation with ^start and text
            self.logger.info("Example 1: Start animation during speech")
            text1 = "^start(animations/Stand/Gestures/Enthusiastic_4) Look what I can do while speaking!"
            self.nao.tts.request(NaoqiTextToSpeechRequest(text1))
            time.sleep(2)
            
            # Example 2: Start animation, then stop it
            self.logger.info("Example 2: Start and stop animation")
            text2 = "^start(animations/Stand/Gestures/Enthusiastic_4) I am moving now! ^stop(animations/Stand/Gestures/Enthusiastic_4) Now I stopped my gesture."
            self.nao.tts.request(NaoqiTextToSpeechRequest(text2))
            time.sleep(2)
            
            # Example 3: Wait for animation to complete
            self.logger.info("Example 3: Wait for animation to complete")
            text3 = "^start(animations/Stand/Gestures/Hey_1) Hi, everyone! ^wait(animations/Stand/Gestures/Hey_1) That was a nice wave!"
            self.nao.tts.request(NaoqiTextToSpeechRequest(text3))
            time.sleep(2)
            
            # Example 4: Run animation (suspend speech during animation)
            self.logger.info("Example 4: Run animation (suspends speech)")
            text4 = "Watch this! ^run(animations/Stand/Gestures/Excited_1) That was exciting!"
            self.nao.tts.request(NaoqiTextToSpeechRequest(text4))
            time.sleep(2)
            
            
        except Exception as e:
            self.logger.error("Error in animated speech demo: {}".format(e))
        finally:
            self.shutdown()


if __name__ == "__main__":
    # Create and run the demo
    demo = NaoAnimatedSpeechDemo()
    demo.run()

