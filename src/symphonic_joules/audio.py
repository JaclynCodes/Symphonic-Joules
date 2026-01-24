"""
Audio processing module for Symphonic-Joules.

This module provides tools for:
- Audio file loading and saving
- Audio signal analysis
- Frequency domain transformations
- Time-domain processing
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, Dict, Any, Optional


def load_audio(path: str, sr: Optional[int] = None, mono: bool = True) -> Tuple[np.ndarray, int, Dict[str, Any]]:
    """
    Load audio file and return waveform, sample rate, and metadata.
    
    Args:
        path: Path to the audio file
        sr: Target sample rate (None to use file's native sample rate)
        mono: Convert to mono if True (default: True)
    
    Returns:
        Tuple containing:
        - y: Audio waveform as numpy array (shape: (n_samples,) for mono or (n_channels, n_samples) for stereo)
        - sr: Sample rate in Hz
        - metadata: Dictionary with 'duration', 'n_samples', 'channels'
    
    Raises:
        FileNotFoundError: If audio file does not exist
        RuntimeError: If audio file cannot be loaded
    
    Example:
        >>> y, sr, metadata = load_audio('audio.wav', sr=22050)
        >>> print(f"Duration: {metadata['duration']:.2f}s, Channels: {metadata['channels']}")
    """
    try:
        # Load audio with librosa
        y, sample_rate = librosa.load(path, sr=sr, mono=mono)
        
        # Calculate metadata
        n_samples = len(y) if y.ndim == 1 else y.shape[1]
        channels = 1 if mono or y.ndim == 1 else y.shape[0]
        duration = n_samples / sample_rate
        
        metadata = {
            'duration': duration,
            'n_samples': n_samples,
            'channels': channels
        }
        
        return y, sample_rate, metadata
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Audio file not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file {path}: {str(e)}")


def save_audio(path: str, y: np.ndarray, sr: int) -> None:
    """
    Save audio waveform to a file.
    
    Args:
        path: Output file path
        y: Audio waveform as numpy array
        sr: Sample rate in Hz
    
    Raises:
        ValueError: If waveform or sample rate is invalid
        RuntimeError: If file cannot be saved
    
    Example:
        >>> save_audio('output.wav', waveform, 22050)
    """
    if sr <= 0:
        raise ValueError(f"Sample rate must be positive, got {sr}")
    
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot save empty waveform")
    
    try:
        sf.write(path, y, sr)
    except Exception as e:
        raise RuntimeError(f"Failed to save audio file {path}: {str(e)}")


def normalize_peak(y: np.ndarray) -> np.ndarray:
    """
    Normalize audio signal to peak amplitude 1.0.
    
    Args:
        y: Audio waveform as numpy array
    
    Returns:
        Normalized waveform with peak amplitude of 1.0
    
    Raises:
        ValueError: If waveform is invalid or all zeros
    
    Example:
        >>> normalized = normalize_peak(waveform)
        >>> assert np.abs(normalized).max() == 1.0
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot normalize empty waveform")
    
    peak = np.abs(y).max()
    
    if peak == 0:
        raise ValueError("Cannot normalize waveform with all zeros (no signal)")
    
    return y / peak


def to_mono(y: np.ndarray) -> np.ndarray:
    """
    Convert multi-channel audio to mono by averaging channels.
    
    Args:
        y: Audio waveform as numpy array
           Shape: (n_samples,) for mono, (n_channels, n_samples) for multi-channel
    
    Returns:
        Mono waveform with shape (n_samples,)
    
    Raises:
        ValueError: If waveform is invalid
    
    Example:
        >>> stereo = np.array([[1, 2, 3], [4, 5, 6]])  # 2 channels
        >>> mono = to_mono(stereo)
        >>> # Result: [2.5, 3.5, 4.5] (average of channels)
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot convert empty waveform")
    
    # Already mono
    if y.ndim == 1:
        return y
    
    # Multi-channel: average across channels (axis 0)
    return np.mean(y, axis=0)


def frame_signal(y: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
    """
    Frame the signal for time-series analysis.
    
    Splits the signal into overlapping frames for windowed analysis.
    
    Args:
        y: Audio waveform as numpy array
        frame_length: Length of each frame in samples
        hop_length: Number of samples to advance between frames (hop size)
    
    Returns:
        2D array of frames with shape (frame_length, n_frames)
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        >>> frames = frame_signal(waveform, frame_length=2048, hop_length=512)
        >>> print(f"Number of frames: {frames.shape[1]}")
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot frame empty waveform")
    
    if frame_length <= 0:
        raise ValueError(f"frame_length must be positive, got {frame_length}")
    
    if hop_length <= 0:
        raise ValueError(f"hop_length must be positive, got {hop_length}")
    
    # Use librosa's frame utility for efficient framing
    return librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)


# Public API for this module. These names will be imported when using
# `from symphonic_joules.audio import *`.
__all__ = ["load_audio", "save_audio", "normalize_peak", "to_mono", "frame_signal"]

