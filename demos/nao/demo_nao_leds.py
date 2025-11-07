# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao
from sic_framework.devices.nao_stub import NaoStub

# Import message types and requests
from sic_framework.devices.common_naoqi.naoqi_leds import (
    NaoFadeRGBRequest,
    NaoLEDRequest,
)
from sic_framework.core.message_python2 import AudioRequest

# Import libraries necessary for the demo
import time
import wave

class NaoLEDsDemo(SICApplication):
    """
    NAO LEDs demo application.
    Demonstrates how to control the NAO robot's LEDs.
    """
    
    def __init__(self):
        # Call parent constructor (handles singleton initialization)
        super(NaoLEDsDemo, self).__init__()
        
        # Demo-specific initialization
        self.nao_ip = "10.0.0.181"
        self.nao = None

        # Audio playback configuration
        self.audio_file = "police-siren-sound-effect-240674.wav"
        self.sound = None
        self.samplerate = None

        self.set_log_level(sic_logging.INFO)
        
        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/Users/apple/Desktop/SAIL/SIC_Development/sic_applications/demos/nao/logs")
        
        self.setup()
    
    def setup(self):
        """Initialize and configure the NAO robot."""
        self.logger.info("Starting NAO LEDs Demo...")
        
        # Initialize the NAO robot
        self.nao = Nao(ip=self.nao_ip)

        # Load audio file once for playback during LED loop
        # try:
        #     with wave.open(self.audio_file, "rb") as wf:
        #         self.samplerate = wf.getframerate()
        #         self.sound = wf.readframes(wf.getnframes())
        #     self.logger.info("Loaded audio file '{}' (sample rate: {})".format(
        #         self.audio_file, self.samplerate
        #     ))
        # except Exception as e:
        #     self.logger.error("Failed to load audio file '{}': {}".format(self.audio_file, e))
    
    def run(self):
        """Main application logic."""
        try:
            self.logger.info("Requesting Eye LEDs to turn on")
            reply = self.nao.leds.request(NaoLEDRequest("FaceLeds", True))
            time.sleep(1)
            
            # Start audio playback before the loop (non-blocking)
            if self.sound is not None and self.samplerate is not None:
                self.logger.info("Playing audio during LED demo")
                message = AudioRequest(sample_rate=self.samplerate, waveform=self.sound, block=False)
                self.nao.speaker.request(message)
            
            for i in range(10):
                self.logger.info("Setting right Eye LEDs to red")
                reply = self.nao.leds.request(NaoFadeRGBRequest("RightFaceLeds", 1, 0, 0, 0), block=False)
                self.logger.info("Setting left Eye LEDs to blue")
                reply = self.nao.leds.request(NaoFadeRGBRequest("LeftFaceLeds", 0, 0, 1, 0), block=False)
                time.sleep(0.5)
                
                self.logger.info("Setting eyes to white")
                reply = self.nao.leds.request(NaoFadeRGBRequest("FaceLeds", 1, 1, 1, 1), block=False)
                time.sleep(0.5)
                #reply = self.nao.leds.request(NaoFadeRGBRequest("LeftFaceLeds", 1, 1, 1, 1))


            # self.logger.info("Setting right Eye LEDs to red")
            # reply = self.nao.leds.request(NaoFadeRGBRequest("RightFaceLeds", 1, 0, 0, 0))
            # time.sleep(1)

            # self.logger.info("Setting left Eye LEDs to blue")
            # reply = self.nao.leds.request(NaoFadeRGBRequest("LeftFaceLeds", 0, 0, 1, 0))

            self.logger.info("LEDs demo completed successfully")
        except Exception as e:
            self.logger.error("Error in LEDs demo: {}".format(e=e))
        finally:
            self.shutdown()


if __name__ == "__main__":
    # Create and run the demo
    demo = NaoLEDsDemo()
    demo.run()
