"""
Physical Constants

List of important physical constants with appropriate units.
"""

import astropy.units as u

# * Speed of Light c

speed_of_light: u.Quantity = 299_792_458 * u.m / u.s

# * Stefan-Boltzmann constant sigma

stefan_boltzmann_constant: u.Quantity = 5.670e-8 * u.W / (u.m**2 * u.K**4)

# * Photosphere temperature T

photosphere_temperature: u.Quantity = 5777 * u.K

# * Radiated power intensity from the Sun photosphere S_0

radiated_power_intensity_photosphere: u.Quantity = stefan_boltzmann_constant * photosphere_temperature**4

# * Photosphere radius R_0

photosphere_radius: u.Quantity = 696_000 * u.km
