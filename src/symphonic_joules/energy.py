"""
Energy calculations module for Symphonic-Joules.

This module provides tools for:
- Energy transformations and measurements
- Power calculations
- Energy flow analysis
- Physics-based computations
- Acoustic energy analysis
"""

import numpy as np
from typing import Tuple, Dict


def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    """
    Calculate kinetic energy using the formula: KE = 0.5 * m * v^2

    Args:
        mass: Mass of the object in kilograms (kg)
        velocity: Velocity of the object in meters per second (m/s)

    Returns:
        Kinetic energy in Joules (J)

    Raises:
        ValueError: If mass is negative
    """
    if mass < 0:
        raise ValueError("Mass cannot be negative")
    return 0.5 * mass * velocity ** 2


def calculate_potential_energy(mass: float, height: float, gravity: float = 9.81) -> float:
    """
    Calculate gravitational potential energy using the formula: PE = m * g * h

    Args:
        mass: Mass of the object in kilograms (kg)
        height: Height above reference point in meters (m)
        gravity: Gravitational acceleration in m/s^2 (default: 9.81)

    Returns:
        Potential energy in Joules (J)

    Raises:
        ValueError: If mass is negative
    """
    if mass < 0:
        raise ValueError("Mass cannot be negative")
    return mass * gravity * height


def acoustic_intensity_proxy(y: np.ndarray) -> np.ndarray:
    """
    Compute a proxy for instantaneous acoustic intensity.
    
    In acoustics, intensity is proportional to the square of sound pressure.
    This function computes the square of the audio signal as a proxy for
    instantaneous intensity (energy per unit area per unit time).
    
    Note: This is a simplified proxy. True acoustic intensity requires
    calibrated measurements and consideration of the acoustic impedance
    of the medium.
    
    Args:
        y: Audio waveform as numpy array (sound pressure proxy)
    
    Returns:
        Array of instantaneous intensity proxy values (proportional to pressure squared)
    
    Raises:
        ValueError: If waveform is invalid
    
    References:
        Beranek, L. L., & Mellow, T. (2012). Acoustics: Sound fields and transducers.
        Academic Press.
    
    Example:
        >>> intensity = acoustic_intensity_proxy(waveform)
        >>> mean_intensity = np.mean(intensity)
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot compute intensity for empty waveform")
    
    # Intensity proxy: I ∝ p^2 (pressure squared)
    return y ** 2


def frame_energy_density(y: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
    """
    Compute average energy density per frame.
    
    Energy density is calculated as the mean squared amplitude within each frame,
    representing the average acoustic energy per sample in that frame.
    
    Args:
        y: Audio waveform as numpy array
        frame_length: Length of each frame in samples
        hop_length: Number of samples to advance between frames
    
    Returns:
        Array of energy density values, one per frame
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        >>> energy = frame_energy_density(waveform, frame_length=2048, hop_length=512)
        >>> # Find frames with highest energy
        >>> high_energy_frames = np.where(energy > np.percentile(energy, 90))[0]
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot compute energy density for empty waveform")
    
    if frame_length <= 0:
        raise ValueError(f"frame_length must be positive, got {frame_length}")
    
    if hop_length <= 0:
        raise ValueError(f"hop_length must be positive, got {hop_length}")
    
    # Compute squared values (energy proxy)
    y_squared = y ** 2
    
    # Calculate number of frames
    n_frames = 1 + (len(y) - frame_length) // hop_length
    
    if n_frames <= 0:
        raise ValueError(f"Signal too short for given frame_length ({frame_length})")
    
    # Compute energy density for each frame
    energy_density = np.zeros(n_frames)
    
    for i in range(n_frames):
        start = i * hop_length
        end = start + frame_length
        # Mean energy (energy density) in this frame
        energy_density[i] = np.mean(y_squared[start:end])
    
    return energy_density


def energy_decomposition_proxy(y: np.ndarray, sr: int, cutoff_freq: float = 1000.0) -> Dict[str, float]:
    """
    Decompose signal energy into low and high frequency components.
    
    This provides a physics-informed energy decomposition by splitting
    the signal into frequency bands, loosely analogous to potential
    (low frequency, slower oscillations) and kinetic (high frequency,
    faster oscillations) energy concepts.
    
    Note: This is a conceptual proxy for educational purposes. True
    potential and kinetic energy in acoustics involve particle velocity
    and displacement, requiring additional measurements.
    
    Args:
        y: Audio waveform as numpy array
        sr: Sample rate in Hz
        cutoff_freq: Frequency (Hz) separating low and high bands (default: 1000 Hz)
    
    Returns:
        Dictionary with keys:
        - 'low_freq_energy': Energy in low frequency band (< cutoff_freq)
        - 'high_freq_energy': Energy in high frequency band (>= cutoff_freq)
        - 'total_energy': Total energy across all frequencies
        - 'low_freq_ratio': Fraction of energy in low frequencies
        - 'high_freq_ratio': Fraction of energy in high frequencies
    
    Raises:
        ValueError: If parameters are invalid
    
    References:
        Pierce, A. D. (1989). Acoustics: An introduction to its physical principles
        and applications. Acoustical Society of America.
    
    Example:
        >>> decomp = energy_decomposition_proxy(waveform, sr=22050, cutoff_freq=1000)
        >>> print(f"Low freq energy: {decomp['low_freq_ratio']:.1%}")
        >>> print(f"High freq energy: {decomp['high_freq_ratio']:.1%}")
    """
    if not isinstance(y, np.ndarray):
        raise ValueError("Waveform must be a numpy array")
    
    if y.size == 0:
        raise ValueError("Cannot compute energy decomposition for empty waveform")
    
    if sr <= 0:
        raise ValueError(f"Sample rate must be positive, got {sr}")
    
    if cutoff_freq <= 0 or cutoff_freq >= sr / 2:
        raise ValueError(f"Cutoff frequency must be between 0 and Nyquist frequency ({sr/2} Hz)")
    
    # Compute FFT for frequency domain analysis
    fft = np.fft.rfft(y)
    fft_freqs = np.fft.rfftfreq(len(y), 1/sr)
    
    # Power spectral density (squared magnitude)
    power_spectrum = np.abs(fft) ** 2
    
    # Split into low and high frequency bands
    low_freq_mask = fft_freqs < cutoff_freq
    high_freq_mask = fft_freqs >= cutoff_freq
    
    # Calculate energy in each band
    low_freq_energy = np.sum(power_spectrum[low_freq_mask])
    high_freq_energy = np.sum(power_spectrum[high_freq_mask])
    total_energy = low_freq_energy + high_freq_energy
    
    # Avoid division by zero
    if total_energy == 0:
        low_freq_ratio = 0.0
        high_freq_ratio = 0.0
    else:
        low_freq_ratio = low_freq_energy / total_energy
        high_freq_ratio = high_freq_energy / total_energy
    
    return {
        'low_freq_energy': float(low_freq_energy),
        'high_freq_energy': float(high_freq_energy),
        'total_energy': float(total_energy),
        'low_freq_ratio': float(low_freq_ratio),
        'high_freq_ratio': float(high_freq_ratio)
    }


__all__ = [
    "calculate_kinetic_energy", 
    "calculate_potential_energy",
    "acoustic_intensity_proxy",
    "frame_energy_density",
    "energy_decomposition_proxy"
]
