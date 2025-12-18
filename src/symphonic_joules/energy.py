"""
Energy calculations module for Symphonic-Joules.

This module provides tools for:
- Energy transformations and measurements
- Power calculations
- Energy flow analysis
- Physics-based computations
"""


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


__all__ = ["calculate_kinetic_energy", "calculate_potential_energy"]
