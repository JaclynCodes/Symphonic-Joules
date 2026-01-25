"""
Tests for the audio processing module.
"""

import pytest
import numpy as np
from pathlib import Path
from src.symphonic_joules.audio import (
    load_audio,
    save_audio,
    normalize_peak,
    to_mono,
    frame_signal
)


class TestLoadAudio:
    """Tests for the load_audio function."""

    def test_load_audio_basic(self, tmp_path):
        """Test basic audio loading with a simple sine wave."""
        # Create a simple test audio file
        test_file = tmp_path / "test.wav"
        sample_rate = 22050
        duration = 1.0
        frequency = 440.0
        
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        y = np.sin(2 * np.pi * frequency * t)
        
        # Save using numpy/scipy style (soundfile will be used by save_audio)
        import soundfile as sf
        sf.write(str(test_file), y, sample_rate)
        
        # Load and verify
        loaded_y, loaded_sr, metadata = load_audio(str(test_file))
        
        assert loaded_sr == sample_rate
        assert metadata['channels'] == 1
        assert metadata['n_samples'] > 0
        assert metadata['duration'] == pytest.approx(duration, abs=0.01)

    def test_load_audio_nonexistent_file(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            load_audio("/nonexistent/path/to/audio.wav")

    def test_load_audio_metadata(self, tmp_path):
        """Test that metadata is correctly computed."""
        test_file = tmp_path / "test_metadata.wav"
        sample_rate = 16000
        duration = 2.0
        
        # Create test audio
        y = np.random.randn(int(sample_rate * duration))
        import soundfile as sf
        sf.write(str(test_file), y, sample_rate)
        
        # Load and check metadata
        _, sr, metadata = load_audio(str(test_file))
        
        assert 'duration' in metadata
        assert 'n_samples' in metadata
        assert 'channels' in metadata
        assert metadata['duration'] == pytest.approx(duration, abs=0.01)
        assert metadata['channels'] == 1


class TestSaveAudio:
    """Tests for the save_audio function."""

    def test_save_audio_basic(self, tmp_path):
        """Test basic audio saving."""
        output_file = tmp_path / "output.wav"
        sample_rate = 22050
        y = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
        
        save_audio(str(output_file), y, sample_rate)
        
        assert output_file.exists()
        
        # Verify we can load it back
        import soundfile as sf
        loaded_y, loaded_sr = sf.read(str(output_file))
        assert loaded_sr == sample_rate
        assert len(loaded_y) == len(y)

    def test_save_audio_invalid_sample_rate(self, tmp_path):
        """Test that negative sample rate raises ValueError."""
        output_file = tmp_path / "output.wav"
        y = np.array([0.1, 0.2, 0.3])
        
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            save_audio(str(output_file), y, -1)

    def test_save_audio_empty_waveform(self, tmp_path):
        """Test that empty waveform raises ValueError."""
        output_file = tmp_path / "output.wav"
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot save empty waveform"):
            save_audio(str(output_file), y, 22050)

    def test_save_audio_invalid_waveform_type(self, tmp_path):
        """Test that non-array waveform raises ValueError."""
        output_file = tmp_path / "output.wav"
        
        with pytest.raises(ValueError, match="Waveform must be a numpy array"):
            save_audio(str(output_file), [0.1, 0.2, 0.3], 22050)


class TestNormalizePeak:
    """Tests for the normalize_peak function."""

    def test_normalize_peak_basic(self):
        """Test basic peak normalization."""
        y = np.array([0.5, -0.8, 0.3, -0.2])
        normalized = normalize_peak(y)
        
        # Peak should be 1.0
        assert np.abs(normalized).max() == pytest.approx(1.0)
        
        # Relative proportions should be preserved
        assert normalized[0] / normalized[1] == pytest.approx(y[0] / y[1])

    def test_normalize_peak_already_normalized(self):
        """Test normalizing an already normalized signal."""
        y = np.array([1.0, -0.5, 0.3])
        normalized = normalize_peak(y)
        
        assert np.abs(normalized).max() == pytest.approx(1.0)
        np.testing.assert_array_almost_equal(y, normalized)

    def test_normalize_peak_all_zeros(self):
        """Test that all-zero waveform raises ValueError."""
        y = np.zeros(100)
        
        with pytest.raises(ValueError, match="Cannot normalize waveform with all zeros"):
            normalize_peak(y)

    def test_normalize_peak_empty_waveform(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot normalize empty waveform"):
            normalize_peak(y)

    def test_normalize_peak_invalid_type(self):
        """Test that non-array input raises ValueError."""
        with pytest.raises(ValueError, match="Waveform must be a numpy array"):
            normalize_peak([0.1, 0.2, 0.3])


class TestToMono:
    """Tests for the to_mono function."""

    def test_to_mono_already_mono(self):
        """Test that mono signal remains unchanged."""
        y = np.array([0.1, 0.2, 0.3, 0.4])
        mono = to_mono(y)
        
        np.testing.assert_array_equal(y, mono)

    def test_to_mono_stereo(self):
        """Test converting stereo to mono by averaging."""
        # Create stereo signal: [left_channel, right_channel]
        left = np.array([1.0, 2.0, 3.0])
        right = np.array([4.0, 5.0, 6.0])
        stereo = np.array([left, right])
        
        mono = to_mono(stereo)
        
        # Should average channels
        expected = np.array([2.5, 3.5, 4.5])
        np.testing.assert_array_almost_equal(mono, expected)

    def test_to_mono_multi_channel(self):
        """Test converting multi-channel (>2) to mono."""
        # 3 channels
        channels = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ])
        
        mono = to_mono(channels)
        
        # Should average all channels
        expected = np.array([4.0, 5.0, 6.0])
        np.testing.assert_array_almost_equal(mono, expected)

    def test_to_mono_empty_waveform(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot convert empty waveform"):
            to_mono(y)

    def test_to_mono_invalid_type(self):
        """Test that non-array input raises ValueError."""
        with pytest.raises(ValueError, match="Waveform must be a numpy array"):
            to_mono([0.1, 0.2, 0.3])


class TestFrameSignal:
    """Tests for the frame_signal function."""

    def test_frame_signal_basic(self):
        """Test basic signal framing."""
        y = np.arange(100)
        frame_length = 10
        hop_length = 5
        
        frames = frame_signal(y, frame_length, hop_length)
        
        # Check shape
        assert frames.shape[0] == frame_length
        assert frames.shape[1] > 0  # Should have multiple frames
        
        # First frame should start at 0
        np.testing.assert_array_equal(frames[:, 0], y[:frame_length])

    def test_frame_signal_non_overlapping(self):
        """Test framing with no overlap (hop_length == frame_length)."""
        y = np.arange(20)
        frame_length = 5
        hop_length = 5
        
        frames = frame_signal(y, frame_length, hop_length)
        
        # Should have 4 non-overlapping frames
        assert frames.shape[1] == 4
        np.testing.assert_array_equal(frames[:, 0], y[0:5])
        np.testing.assert_array_equal(frames[:, 1], y[5:10])

    def test_frame_signal_overlapping(self):
        """Test framing with 50% overlap."""
        y = np.arange(10)
        frame_length = 4
        hop_length = 2
        
        frames = frame_signal(y, frame_length, hop_length)
        
        # Check overlap
        assert frames.shape[0] == frame_length
        # First frame: [0,1,2,3]
        # Second frame: [2,3,4,5] - overlaps with first
        np.testing.assert_array_equal(frames[:, 0], [0, 1, 2, 3])
        np.testing.assert_array_equal(frames[:, 1], [2, 3, 4, 5])

    def test_frame_signal_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        y = np.arange(100)
        
        # Negative frame_length
        with pytest.raises(ValueError, match="frame_length must be positive"):
            frame_signal(y, -10, 5)
        
        # Zero hop_length
        with pytest.raises(ValueError, match="hop_length must be positive"):
            frame_signal(y, 10, 0)

    def test_frame_signal_empty_waveform(self):
        """Test that empty waveform raises ValueError."""
        y = np.array([])
        
        with pytest.raises(ValueError, match="Cannot frame empty waveform"):
            frame_signal(y, 10, 5)

    def test_frame_signal_invalid_type(self):
        """Test that non-array input raises ValueError."""
        with pytest.raises(ValueError, match="Waveform must be a numpy array"):
            frame_signal([0.1, 0.2, 0.3], 2, 1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
