"""
Tests for the public API exports in the Symphonic-Joules package.
"""

import symphonic_joules
from symphonic_joules import (
    load_audio,
    save_audio,
    normalize_peak,
    to_mono,
    frame_signal,
    calculate_kinetic_energy,
    calculate_potential_energy,
    acoustic_intensity_proxy,
    frame_energy_density,
    energy_decomposition_proxy,
)


def test_audio_functions_exported():
    """Test that audio helpers are available from the top-level package."""
    assert callable(load_audio)
    assert callable(save_audio)
    assert callable(normalize_peak)
    assert callable(to_mono)
    assert callable(frame_signal)


def test_energy_functions_exported():
    """Test that energy helpers are available from the top-level package."""
    assert callable(calculate_kinetic_energy)
    assert callable(calculate_potential_energy)
    assert callable(acoustic_intensity_proxy)
    assert callable(frame_energy_density)
    assert callable(energy_decomposition_proxy)


def test_all_exports_are_listed():
    """Test that __all__ lists the exported helpers."""
    expected_exports = {
        "load_audio",
        "save_audio",
        "normalize_peak",
        "to_mono",
        "frame_signal",
        "calculate_kinetic_energy",
        "calculate_potential_energy",
        "acoustic_intensity_proxy",
        "frame_energy_density",
        "energy_decomposition_proxy",
    }

    assert expected_exports.issubset(set(symphonic_joules.__all__))
