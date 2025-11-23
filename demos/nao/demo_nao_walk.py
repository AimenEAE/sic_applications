# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao

# Import message types and requests
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoWakeUpRequest, NaoRestRequest
from sic_framework.devices.common_naoqi.naoqi_motion import (
    NaoPostureRequest,
    NaoqiMoveToRequest,
)

# Import libraries necessary for the demo
import time


class NaoWalkDemo(SICApplication):
    """
    NAO walking demo application.
    Makes NAO walk forward in a straight line using NaoqiMoveToRequest.
    """
    
    def __init__(self, nao_ip="10.0.0.181"):
        super(NaoWalkDemo, self).__init__()
        
        self.nao_ip = nao_ip
        self.nao = None
        
        self.set_log_level(sic_logging.INFO)
        self.setup()
    
    def setup(self):
        """Initialize and configure the NAO robot."""
        self.logger.info("Starting NAO Walk Demo...")
        self.nao = Nao(ip=self.nao_ip)
        self.logger.info("NAO initialized successfully")
    
    def run(self):
        """Main application logic."""
        try:
            # Wake up and stand
            self.logger.info("Waking up NAO...")
            self.nao.autonomous.request(NaoWakeUpRequest())
            time.sleep(2)
            
            self.logger.info("NAO standing up...")
            self.nao.motion.request(NaoPostureRequest("Stand", 0.5))
            time.sleep(1)
            
            # Walk forward in a straight line (1 meter forward, 0 sideways, 0 rotation)
            self.logger.info("NAO walking forward 1 meter...")
            self.nao.motion.request(NaoqiMoveToRequest(x=1.0, y=0.0, theta=0.0))
            time.sleep(3)
            
            # Rest
            self.logger.info("NAO going to rest...")
            self.nao.autonomous.request(NaoRestRequest())
            
            self.logger.info("Walking demo completed successfully")
            
        except Exception as e:
            self.logger.error("Error during walking demo: {}".format(e))
        finally:
            self.logger.info("Shutting down application")
            self.shutdown()


if __name__ == "__main__":
    # Configuration
    nao_ip = "10.0.0.181"
    
    # Create and run the demo
    demo = NaoWalkDemo(nao_ip=nao_ip)
    demo.run()