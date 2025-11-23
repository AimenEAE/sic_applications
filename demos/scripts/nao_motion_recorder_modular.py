# Import basic preliminaries
from sic_framework.core.sic_application import SICApplication
from sic_framework.core import sic_logging

# Import the device(s) we will be using
from sic_framework.devices import Nao
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoRestRequest, NaoWakeUpRequest

# Import message types and requests
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import (
    NaoqiMotionRecorderConf,
    NaoqiMotionRecording,
    PlayRecording,
    StartRecording,
    StopRecording,
)
from sic_framework.devices.common_naoqi.naoqi_stiffness import Stiffness

# Import libraries necessary for the demo
import time
from pathlib import Path


class ModularNaoMotionRecorder(SICApplication):
    """
    Modular NAO motion recorder application.
    
    Features:
    - Configurable body parts (limbs) to record
    - Adjustable stiffness for recording and playback
    - Configurable recording duration
    - Reusable motion recordings
    
    Available body parts:
    - "LArm" - Left Arm
    - "RArm" - Right Arm
    - "LLeg" - Left Leg
    - "RLeg" - Right Leg
    - "Head" - Head
    - "Body" - Entire body
    """
    
    def __init__(
        self,
        motion_name,
        body_parts=None,
        record_time=10,
        recording_stiffness=0.0,
        playback_stiffness=0.7,
        use_sensors=True,
        nao_ip="10.0.0.181"
    ):
        """
        Initialize the modular motion recorder.
        
        Args:
            motion_name: Name to save/load the motion recording
            body_parts: List of body parts to record (e.g., ["LArm", "RArm"])
                       Default: ["LArm", "RArm"]
            record_time: Recording duration in seconds (default: 10)
            recording_stiffness: Stiffness during recording (0.0 = loose, 1.0 = stiff)
                                Default: 0.0 (loose for manual movement)
            playback_stiffness: Stiffness during playback (0.0 = loose, 1.0 = stiff)
                               Default: 0.7 (moderate stiffness for replay)
            use_sensors: Whether to use sensors for recording (default: True)
            nao_ip: IP address of the NAO robot
        """
        # Call parent constructor (handles singleton initialization)
        super(ModularNaoMotionRecorder, self).__init__()
        
        # Motion recording configuration
        self.nao_ip = nao_ip
        self.motion_name = motion_name
        self.body_parts = body_parts if body_parts is not None else ["LArm", "RArm"]
        self.record_time = record_time
        self.recording_stiffness = recording_stiffness
        self.playback_stiffness = playback_stiffness
        self.use_sensors = use_sensors
        
        # NAO robot instance
        self.nao = None
        
        self.set_log_level(sic_logging.INFO)
        
        # Log files will only be written if set_log_file is called. Must be a valid full path to a directory.
        # self.set_log_file("/path/to/logs")
        
        self.setup()
    
    def setup(self):
        """Initialize and configure the NAO robot."""
        self.logger.info("Starting Modular NAO Motion Recorder...")
        self.logger.info("Configuration:")
        self.logger.info("  Motion name: {}".format(self.motion_name))
        self.logger.info("  Body parts: {}".format(", ".join(self.body_parts)))
        self.logger.info("  Record time: {} seconds".format(self.record_time))
        self.logger.info("  Recording stiffness: {}".format(self.recording_stiffness))
        self.logger.info("  Playback stiffness: {}".format(self.playback_stiffness))
        self.logger.info("  Use sensors: {}".format(self.use_sensors))
        
        # Initialize NAO with motion recorder configuration
        conf = NaoqiMotionRecorderConf(use_sensors=self.use_sensors)
        self.nao = Nao(self.nao_ip, motion_record_conf=conf)
        
        self.logger.info("NAO robot initialized successfully")
    
    def set_stiffness(self, stiffness, body_parts=None):
        """
        Set stiffness for specified body parts.
        
        Args:
            stiffness: Stiffness value (0.0 to 1.0)
            body_parts: List of body parts (None = use default from init)
        """
        parts = body_parts if body_parts is not None else self.body_parts
        self.logger.info("Setting stiffness to {} for: {}".format(stiffness, ", ".join(parts)))
        self.nao.stiffness.request(Stiffness(stiffness=stiffness, joints=parts))
    
    def wakeup(self):
        """Wake up the NAO robot."""
        self.logger.info("Waking up NAO...")
        self.nao.autonomous.request(NaoWakeUpRequest())
    
    def rest(self):
        """Put the NAO robot to rest."""
        self.logger.info("NAO going to rest...")
        self.nao.autonomous.request(NaoRestRequest())
    
    def save_motion_to_file(self, recording, motion_name=None):
        """
        Save a motion recording to a file.
        
        Args:
            recording: NaoqiMotionRecording object
            motion_name: Name to save the motion as (None = use default)
        
        Returns:
            Motion name used for saving
        """
        name = motion_name if motion_name is not None else self.motion_name
        
        self.logger.info("Saving motion as: {}".format(name))
        recording.save(name)
        
        self.logger.info("Motion saved successfully!")
        
        return name
    
    def load_motion_from_file(self, filename):
        """
        Load a motion recording from a file.
        
        Args:
            filename: Name of the motion (the framework handles .motion extension automatically)
        
        Returns:
            NaoqiMotionRecording object
        """
        # Remove .motion extension if provided (framework adds it automatically)
        if filename.endswith('.motion'):
            filename = filename[:-7]
        
        self.logger.info("Loading motion: {}".format(filename))
        recording = NaoqiMotionRecording.load(filename)
        self.logger.info("Motion loaded successfully!")
        
        return recording
    
    def list_saved_motions(self):
        """
        List all saved motion files in the motion_recordings directory.
        
        Returns:
            List of motion filenames (without .motion extension)
        """
        import os
        motion_dir = Path("motion_recordings")
        
        if not motion_dir.exists():
            self.logger.info("No motion_recordings directory found")
            return []
        
        motion_files = list(motion_dir.glob("*.motion"))
        motion_names = [f.stem for f in motion_files]
        
        self.logger.info("Found {} saved motion(s):".format(len(motion_names)))
        for name in motion_names:
            self.logger.info("  - {}".format(name))
        
        return motion_names
    
    def record_motion(self):
        """
        Record a motion by manually moving the robot.
        Saves the motion to a file and returns the recording.
        
        Returns:
            NaoqiMotionRecording object
        """
        self.logger.info("=" * 60)
        self.logger.info("RECORDING MOTION")
        self.logger.info("=" * 60)
        
        # Wake up the robot
        self.wakeup()
        time.sleep(1)
        
        # Set stiffness for recording (usually low/zero for manual movement)
        self.set_stiffness(self.recording_stiffness)
        time.sleep(0.5)
        
        # Start recording
        self.logger.info("Start moving the robot! (not too fast)")
        self.logger.info("Recording for {} seconds...".format(self.record_time))
        self.nao.motion_record.request(StartRecording(self.body_parts))
        
        # Wait for recording duration
        time.sleep(self.record_time)
        
        # Stop recording
        self.logger.info("Recording complete! Saving motion...")
        recording = self.nao.motion_record.request(StopRecording())
        
        # Save to file
        saved_name = self.save_motion_to_file(recording)
        
        self.logger.info("Motion saved as: {}".format(saved_name))
        self.logger.info("=" * 60)
        
        return recording
    
    def replay_motion(self, motion_name=None):
        """
        Replay a saved motion by loading it from file.
        
        Args:
            motion_name: Name of the motion to replay (None = use default)
        """
        name = motion_name if motion_name is not None else self.motion_name
        
        self.logger.info("=" * 60)
        self.logger.info("REPLAYING MOTION: {}".format(name))
        self.logger.info("=" * 60)
        
        # Load the recording from file
        recording = self.load_motion_from_file(name)
        
        # Set stiffness for playback (usually moderate to high)
        self.set_stiffness(self.playback_stiffness)
        time.sleep(0.5)
        
        # Play the recording
        self.logger.info("Playing motion...")
        self.nao.motion_record.request(PlayRecording(recording))
        
        self.logger.info("Motion replay complete!")
        self.logger.info("=" * 60)
    
    def replay_motion_from_file(self, filename):
        """
        Replay a motion directly from a file.
        
        Args:
            filename: Name of the motion file (with or without .motion extension)
        """
        self.logger.info("=" * 60)
        self.logger.info("REPLAYING MOTION FROM FILE: {}".format(filename))
        self.logger.info("=" * 60)
        
        self.nao.autonomous.request(NaoWakeUpRequest())
        time.sleep(1)
        
        self.set_stiffness(self.playback_stiffness)
        time.sleep(0.5)
        
        # Load the recording from file
        recording = self.load_motion_from_file(filename)
        
        # Set stiffness for playback (usually moderate to high)
        self.set_stiffness(self.playback_stiffness)
        time.sleep(0.5)
        
        # Play the recording
        self.logger.info("Playing motion...")
        self.nao.motion_record.request(PlayRecording(recording))
        
        self.logger.info("Motion replay complete!")
        self.logger.info("=" * 60)
    
    def record_and_replay(self):
        """Record a motion and immediately replay it."""
        # Record the motion
        self.record_motion()
        
        # Wait a bit before replaying
        time.sleep(2)
        
        # Replay the motion
        self.replay_motion()
    
    def run(self):
        """Main application logic - record and replay motion."""
        try:
            # Record and replay the motion
            self.record_and_replay()
            
            # Put robot to rest
            #self.rest()
            
            self.logger.info("Demo completed successfully")
            
        except Exception as e:
            self.logger.error("Error in motion recorder: {}".format(e))
        finally:
            self.shutdown()


if __name__ == "__main__":
    # ============================================================================
    # CONFIGURATION - Modify these parameters as needed
    # ============================================================================
    
    # Motion name for saving/loading
    motion_name = "point_to_audience"
    
    # Body parts to record (choose from: "LArm", "RArm", "LLeg", "RLeg", "Head", "Body")
    body_parts = ["LArm", "RArm", "Head"]  # Record both arms
    
    # Recording duration in seconds
    record_time = 20
    
    # Stiffness values (0.0 = completely loose, 1.0 = completely stiff)
    recording_stiffness = 0.0  # Loose for manual movement during recording
    playback_stiffness = 0.7   # Moderate stiffness for smooth replay
    
    # Use sensors for more accurate recording
    use_sensors = True
    
    # NAO IP address
    nao_ip = "10.0.0.181"
    
    # ============================================================================
    # CREATE AND RUN THE DEMO
    # ============================================================================
    
    # Example 1: Basic usage - record both arms
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Recording both arms")
    print("=" * 60)
    
    demo = ModularNaoMotionRecorder(
        motion_name=motion_name,
        body_parts=body_parts,
        record_time=record_time,
        recording_stiffness=recording_stiffness,
        playback_stiffness=playback_stiffness,
        use_sensors=use_sensors,
        nao_ip=nao_ip
    )
    demo.run()
    
    #demo.replay_motion_from_file(motion_name)

