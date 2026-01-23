"""
Tests for the energy calculations module.
"""

import pytest
from src.symphonic_joules.energy import calculate_kinetic_energy, calculate_potential_energy


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
