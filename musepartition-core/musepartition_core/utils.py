"""Stub Utils pour tests Pipeline"""
from pathlib import Path

class DebugTracer:
    def __init__(self, output_dir="output/debug", enabled=True):
        self.enabled = enabled
        self.output_dir = Path(output_dir)
    
    def log_step(self, step_name: str, metadata: dict):
        if self.enabled:
            print(f"[DEBUG] {step_name}: {metadata}")

class IntermediateStorage:
    def __init__(self, output_dir="output/intermediate"):
        self.output_dir = Path(output_dir)
    
    def save_audio(self, audio, sr, filename="audio.npz"):
        pass
