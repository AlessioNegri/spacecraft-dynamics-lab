"""
Atmosphere Models

Implements all the atmosphere models using "U.S. Standard Atmosphere 1976" model

References:
- Pasquale M. Sforza, "Manned Spacecraft - Design Principles"
    - Chapter 2: Earth's Atmosphere
"""

import pathlib
import astropy.units as u
import numpy as np
import scipy.interpolate as interpolate
import typing

import astro.physical_constants as physical_constants

class Atmosphere():
    """Atmosphere"""

    def __init__(self):
        """Constructor"""
        
        data_path: pathlib.Path = pathlib.Path(__file__).with_name("USStandardAtmosphere1976.csv")
        
        data: np.ndarray = np.loadtxt(fname=data_path, delimiter=",", skiprows=1)

        z: np.ndarray = data[:, 0].astype(float) # ? Altitude [km]
        T: np.ndarray = data[:, 1].astype(float) # ? Temperature [K]
        p: np.ndarray = data[:, 2].astype(float) # ? Pressure [kPa]
        r: np.ndarray = data[:, 3].astype(float) # ? Density [kg / m^3]
        
        self.temperature_interpolator: interpolate.CubicSpline = interpolate.CubicSpline(x=z,
                                                                                         y=T,
                                                                                         bc_type='natural')

        self.pressure_interpolator: interpolate.interp1d = interpolate.interp1d(x=z,
                                                                                y=np.log(p),
                                                                                kind='linear',
                                                                                fill_value="extrapolate",
                                                                                assume_sorted=True)

        self.density_interpolator: interpolate.interp1d = interpolate.interp1d(x=z,
                                                                               y=np.log(r),
                                                                               kind='linear',
                                                                               fill_value="extrapolate",
                                                                               assume_sorted=True)

    def thermodynamic_properties(self,
                                 altitude: u.Quantity,
                                 thermodynamic_consistency: bool = False)\
                                     -> typing.Tuple[u.Quantity, u.Quantity, u.Quantity]:
        """
        Return temperature, pressure, and density at the requested altitude

        Args:
            altitude (u.Quantity): Altitude
            thermodynamic_consistency (bool, optional): Enforce thermodynamic consistency. Defaults to False.

        Returns:
            typing.Tuple[u.Quantity, u.Quantity, u.Quantity]: (temperature, pressure, density)
        """
        
        z: np.ndarray = np.asarray(altitude.to_value(u.km), dtype=float)
        
        temperature: u.Quantity = self.temperature_interpolator(z) * u.K
        
        pressure: u.Quantity = np.exp(self.pressure_interpolator(z)) * u.kPa
        
        density: u.Quantity = np.exp(self.density_interpolator(z)) * u.kg / u.m**3
        
        if thermodynamic_consistency:
            
            R: u.Quantity = physical_constants.atmospheric_gas_constant
            
            density = (pressure.to(u.Pa) / (R * temperature)).decompose()
        
        return (temperature, pressure.to(u.Pa), density)

    def sample_properties(self,
                          altitude_grid: typing.Iterable[u.Quantity] | None = None,
                          thermodynamic_consistency: bool = False) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample atmosphere properties on an altitude grid

        Args:
            altitude_grid (typing.Iterable[u.Quantity] | None, optional): List of altitude values. Defaults to None.
            thermodynamic_consistency (bool, optional): Enforce thermodynamic consistency. Defaults to False.

        Returns:
            typing.Tuple[np.ndarray, np.ndarray, np.ndarray]: (temperature, pressure, density)
        """
        
        altitudes: u.Quantity = np.linspace(0, 1000, 1000) * u.km if altitude_grid is None else u.Quantity(altitude_grid)

        temperatures: list[float] = []
        pressures: list[float] = []
        densities: list[float] = []

        for altitude in altitudes:
            
            temperature, pressure, density = self.thermodynamic_properties(altitude=altitude,
                                                                           thermodynamic_consistency=thermodynamic_consistency)

            temperatures.append(temperature.to_value(u.K))
            pressures.append(pressure.to_value(u.kPa))
            densities.append(density.to_value(u.kg / u.m**3))

        return (np.asarray(temperatures), np.asarray(pressures), np.asarray(densities))
