"""
Tests for the energy calculations module.
"""

import pytest
import numpy as np
from src.symphonic_joules.energy import (
    calculate_kinetic_energy, 
    calculate_potential_energy,
    acoustic_intensity_proxy,
    frame_energy_density,
    energy_decomposition_proxy
)


class TestCalculateKineticEnergy:
    """Tests for the calculate_kinetic_energy function."""

    def test_kinetic_energy_basic(self):
        """Test basic kinetic energy calculation."""
        # KE = 0.5 * 2 * 3^2 = 0.5 * 2 * 9 = 9 J
        result = calculate_kinetic_energy(mass=2.0, velocity=3.0)
        assert result == 9.0

    def test_kinetic_energy_zero_velocity(self):
        """Test kinetic energy with zero velocity."""
        result = calculate_kinetic_energy(mass=10.0, velocity=0.0)
        assert result == 0.0

    def test_kinetic_energy_zero_mass(self):
        """Test kinetic energy with zero mass."""
        result = calculate_kinetic_energy(mass=0.0, velocity=5.0)
        assert result == 0.0

    def test_kinetic_energy_negative_velocity(self):
        """Test kinetic energy with negative velocity (direction doesn't affect energy)."""
        result = calculate_kinetic_energy(mass=2.0, velocity=-3.0)
        assert result == 9.0

    def test_kinetic_energy_negative_mass_raises(self):
        """Test that negative mass raises ValueError."""
        with pytest.raises(ValueError, match="Mass cannot be negative"):
            calculate_kinetic_energy(mass=-1.0, velocity=5.0)


class TestCalculatePotentialEnergy:
    """Tests for the calculate_potential_energy function."""

    def test_potential_energy_basic(self):
        """Test basic potential energy calculation."""
        # PE = 2 * 9.81 * 10 = 196.2 J
        result = calculate_potential_energy(mass=2.0, height=10.0)
        assert result == pytest.approx(196.2, rel=1e-2)

    def test_potential_energy_zero_height(self):
        """Test potential energy at zero height."""
        result = calculate_potential_energy(mass=10.0, height=0.0)
        assert result == 0.0

    def test_potential_energy_zero_mass(self):
        """Test potential energy with zero mass."""
        result = calculate_potential_energy(mass=0.0, height=100.0)
        assert result == 0.0

    def test_potential_energy_custom_gravity(self):
        """Test potential energy with custom gravity (e.g., Moon)."""
        # PE = 2 * 1.62 * 10 = 32.4 J (Moon's gravity ~1.62 m/s^2)
        result = calculate_potential_energy(mass=2.0, height=10.0, gravity=1.62)
        assert result == pytest.approx(32.4, rel=1e-2)

    def test_potential_energy_negative_height(self):
        """Test potential energy with negative height (below reference)."""
        result = calculate_potential_energy(mass=2.0, height=-5.0)
        assert result == pytest.approx(-98.1, rel=1e-2)

    def test_potential_energy_negative_mass_raises(self):
        """Test that negative mass raises ValueError."""
        with pytest.raises(ValueError, match="Mass cannot be negative"):
            calculate_potential_energy(mass=-1.0, height=10.0)


class TestAcousticIntensityProxy:
    """Tests for the acoustic_intensity_proxy function."""

    def test_acoustic_intensity_basic(self):
        """Test basic acoustic intensity calculation."""
        y = np.array([1.0, 2.0, -3.0, 0.5])
        intensity = acoustic_intensity_proxy(y)
        
        # Intensity is square of pressure
        expected = np.array([1.0, 4.0, 9.0, 0.25])
        np.testing.assert_array_almost_equal(intensity, expected)

    def test_acoustic_intensity_zero_signal(self):
        """Test intensity of zero signal."""
        y = np.zeros(100)
        intensity = acoustic_intensity_proxy(y)
        
        assert np.all(intensity == 0)

    def test_acoustic_intensity_empty_raises(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot compute intensity for empty waveform"):
            acoustic_intensity_proxy(y)

    def test_acoustic_intensity_invalid_type(self):
        """Test that non-array input raises ValueError."""
        with pytest.raises(ValueError, match="Waveform must be a numpy array"):
            acoustic_intensity_proxy([0.1, 0.2, 0.3])


class TestFrameEnergyDensity:
    """Tests for the frame_energy_density function."""

    def test_frame_energy_density_basic(self):
        """Test basic energy density calculation."""
        # Create simple signal
        y = np.ones(100)
        frame_length = 10
        hop_length = 10
        
        energy = frame_energy_density(y, frame_length, hop_length)
        
        # For constant signal with amplitude 1, energy density = 1^2 = 1
        assert len(energy) == 10  # 100 samples / 10 hop = 10 frames
        np.testing.assert_allclose(energy, 1.0)

    def test_frame_energy_density_varying_signal(self):
        """Test energy density with varying signal."""
        # Create signal with different amplitudes in different regions
        y = np.concatenate([np.ones(50) * 0.5, np.ones(50) * 2.0])
        frame_length = 50
        hop_length = 50
        
        energy = frame_energy_density(y, frame_length, hop_length)
        
        # First frame: 0.5^2 = 0.25, second frame: 2.0^2 = 4.0
        assert energy[0] == pytest.approx(0.25)
        assert energy[1] == pytest.approx(4.0)

    def test_frame_energy_density_invalid_frame_length(self):
        """Test that invalid frame_length raises ValueError."""
        y = np.ones(100)
        
        with pytest.raises(ValueError, match="frame_length must be positive"):
            frame_energy_density(y, -10, 10)

    def test_frame_energy_density_signal_too_short(self):
        """Test that signal shorter than frame_length raises ValueError."""
        y = np.ones(5)
        
        with pytest.raises(ValueError, match="Signal too short"):
            frame_energy_density(y, 10, 5)

    def test_frame_energy_density_empty_waveform(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot compute energy density for empty waveform"):
            frame_energy_density(y, 10, 5)


class TestEnergyDecompositionProxy:
    """Tests for the energy_decomposition_proxy function."""

    def test_energy_decomposition_basic(self):
        """Test basic energy decomposition."""
        # Create a simple signal with known frequency
        sr = 8000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # Low frequency sine wave (500 Hz)
        y = np.sin(2 * np.pi * 500 * t)
        
        decomp = energy_decomposition_proxy(y, sr, cutoff_freq=1000)
        
        # Most energy should be in low frequencies
        assert decomp['low_freq_ratio'] > 0.9
        assert decomp['high_freq_ratio'] < 0.1
        assert decomp['low_freq_ratio'] + decomp['high_freq_ratio'] == pytest.approx(1.0)

    def test_energy_decomposition_high_frequency(self):
        """Test energy decomposition with high frequency signal."""
        sr = 8000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # High frequency sine wave (2000 Hz)
        y = np.sin(2 * np.pi * 2000 * t)
        
        decomp = energy_decomposition_proxy(y, sr, cutoff_freq=1000)
        
        # Most energy should be in high frequencies
        assert decomp['low_freq_ratio'] < 0.1
        assert decomp['high_freq_ratio'] > 0.9

    def test_energy_decomposition_mixed_signal(self):
        """Test energy decomposition with mixed frequency signal."""
        sr = 8000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # Mix of low (500 Hz) and high (2000 Hz) frequencies
        y_low = np.sin(2 * np.pi * 500 * t)
        y_high = np.sin(2 * np.pi * 2000 * t)
        y = y_low + y_high
        
        decomp = energy_decomposition_proxy(y, sr, cutoff_freq=1000)
        
        # Should have energy in both bands
        assert 0.3 < decomp['low_freq_ratio'] < 0.7
        assert 0.3 < decomp['high_freq_ratio'] < 0.7
        assert decomp['total_energy'] > 0

    def test_energy_decomposition_zero_signal(self):
        """Test energy decomposition with zero signal."""
        y = np.zeros(100)
        sr = 8000
        
        decomp = energy_decomposition_proxy(y, sr, cutoff_freq=1000)
        
        # All energy values should be zero
        assert decomp['total_energy'] == 0.0
        assert decomp['low_freq_ratio'] == 0.0
        assert decomp['high_freq_ratio'] == 0.0

    def test_energy_decomposition_invalid_sample_rate(self):
        """Test that invalid sample rate raises ValueError."""
        y = np.ones(100)
        
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            energy_decomposition_proxy(y, -1000, cutoff_freq=500)

    def test_energy_decomposition_invalid_cutoff(self):
        """Test that invalid cutoff frequency raises ValueError."""
        y = np.ones(100)
        sr = 8000
        
        # Cutoff above Nyquist frequency
        with pytest.raises(ValueError, match="Cutoff frequency must be between"):
            energy_decomposition_proxy(y, sr, cutoff_freq=5000)

    def test_energy_decomposition_empty_waveform(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot compute energy decomposition for empty waveform"):
            energy_decomposition_proxy(y, 8000, cutoff_freq=1000)

    def test_energy_decomposition_result_structure(self):
        """Test that result contains all required keys."""
        sr = 8000
        duration = 0.1
        t = np.linspace(0, duration, int(sr * duration))
        y = np.sin(2 * np.pi * 500 * t)
        
        decomp = energy_decomposition_proxy(y, sr, cutoff_freq=1000)
        
        # Check all required keys are present
        required_keys = ['low_freq_energy', 'high_freq_energy', 'total_energy', 
                        'low_freq_ratio', 'high_freq_ratio']
        for key in required_keys:
            assert key in decomp, f"Result should contain '{key}' key"
            assert isinstance(decomp[key], float), f"'{key}' should be a float"
