import astropy.units as u
import numpy as np
import pathlib as pl
import scipy.interpolate as interpolate
import typing as ty

from spacelab.enums import AtmosphereModel
from spacelab.utils.logger import logger
from spacelab.utils.singleton import Singleton
from spacelab.utils.validator import validate_quantity, validate_type

import spacelab.physical_constants as sl_constants

class Atmosphere(Singleton):
    """
    **Atmosphere** describes the models used for modeling the thermodynamics properties of the Earth's atmosphere.
    
    <hr>
    
    📖 **References**

    - :cite:`(1) Orbital Mechanics for Engineering Students`
        - :cite:`Chapter 12 "Introduction to Orbital Perturbations"`
    
    - :cite:`(3) Manned Spacecraft - Design Principles`
        - :cite:`Chapter 2 "EARTH'S ATMOSPHERE"`
    
    - :cite:`(4) Manned Spacecraft - Design Principles`
        - :cite:`Chapter 6 "Earths's Atmosphere"`
    
    <hr>

    📌 **Notes**
    
    The *World Meteorological Organization* defines such a standard as
    
    *“A hypothetical vertical distribution of atmospheric temperature, pressure, and density which by international
    agreement and for historical reasons, is roughly representative of year-round mid-latitude conditions.”*
    
    The **1976 U.S. Standard Atmosphere** model is one of these. The *U.S. Committee on Extension to the Standard Atmosphere*
    (**COESA**) developed the 1976 version of the U.S. Standard Atmosphere (COESA, 1976).
    
    Rocket and satellite data along with conventional meteorological instruments and perfect gas theory were used to
    develop a standard profile for the thermodynamic and state properties of the atmosphere from sea level to a
    geometric altitude of 1000 km.
    
    This model is an idealized, steady-state representation of the atmosphere in the mid-latitudes during a period of
    moderate solar activity.
    
    <hr>
    
    🧮 **Attributes**
    
    **temperature_interpolator : interpolate.CubicSpline** Temperature interpolator (COESA, 1976)
    
    **pressure_interpolator : interpolate.interp1d** Pressure interpolator (COESA, 1976)
    
    **density_interpolator : interpolate.interp1d** Density interpolator (COESA, 1976)
    """

    def _singleton_init(self):
        
        self.temperature_interpolator: interpolate.CubicSpline
        self.pressure_interpolator: interpolate.interp1d
        self.density_interpolator: interpolate.interp1d
        
        self.altitude: np.ndarray
        self.density_USSA76: np.ndarray
        self.density_CIRA72: np.ndarray
        self.scale_height_USSA76: np.ndarray
        self.scale_height_CIRA72: np.ndarray
        
        self.load_1976_us_standard_atmosphere()
        self.load_density_models()
    
    def load_1976_us_standard_atmosphere(self) -> None:
        """
        Loads the 1976 U.S. Standard Atmosphere model.
        
        <hr>
        
        📖 **References**
        
        - :cite:`Section 2.5 "TABLES OF ATMOSPHERIC PROPERTIES"`
        """
        
        file: pl.Path = pl.Path(__file__).parent / "1976_us_standard_atmosphere.csv"
        
        if not file.exists():
            
            logger.warning(f"File {file} not found")
            
            return
        
        data: np.ndarray = np.loadtxt(fname=file, delimiter=",", skiprows=1)
        
        logger.info(f"File {file} loaded")

        z: np.ndarray = data[:, 0].astype(float) # ? Altitude [km]
        T: np.ndarray = data[:, 1].astype(float) # ? Temperature [K]
        p: np.ndarray = data[:, 2].astype(float) # ? Pressure [kPa]
        r: np.ndarray = data[:, 3].astype(float) # ? Density [kg / m^3]
        
        self.temperature_interpolator = interpolate.CubicSpline(x=z, y=T, bc_type='natural')

        self.pressure_interpolator = interpolate.interp1d(
            x=z, y=np.log(p), kind='linear', fill_value="extrapolate", assume_sorted=True)

        self.density_interpolator = interpolate.interp1d(
            x=z, y=np.log(r), kind='linear', fill_value="extrapolate", assume_sorted=True)
    
    def load_density_models(self) -> None:
        """
        Loads the density models.
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 12.4 "Atmospheric Drag"`
        - :cite:`(4) Section 6.1.3 "Piecewise-Expoìonential Model"`
        """
        
        file: pl.Path = pl.Path(__file__).parent / "density_models.csv"
        
        if not file.exists():
            
            logger.warning(f"File {file} not found")
            
            return
        
        data: np.ndarray = np.loadtxt(fname=file, delimiter=",", skiprows=1)
        
        logger.info(f"File {file} loaded")

        self.altitude = data[:, 0].astype(float) # ? Geometric altitude [km]
        self.density_USSA76 = data[:, 1].astype(float) # ? Density [kg / m^3]
        self.density_CIRA72 = data[:, 2].astype(float) # ? Density [kg / m^3]
        self.scale_height_USSA76 = data[:, 3].astype(float) # ? Scale height [km]
        self.scale_height_CIRA72 = data[:, 4].astype(float) # ? Scale height [km]

    def thermodynamic_properties(
        self, altitude: u.Quantity, thermodynamic_consistency: bool = False) -> ty.List[u.Quantity] | None:
        """
        Computes temperature, pressure, and density at the requested altitude using the 1976 U.S. Standard Atmosphere.

        :param altitude: Altitude
        :type altitude: u.Quantity
        :param thermodynamic_consistency: Enforce thermodynamic consistency, defaults to False
        :type thermodynamic_consistency: bool, optional
        :return: Temperature, pressure, and density
        :rtype: ty.List[u.Quantity] | None
        """
        
        # >>> Validation
        
        # * altitude
        
        err_msg: str | None = validate_quantity("altitude", altitude, u.m)
        
        if err_msg: logger.warning(err_msg); return None
        
        z: np.ndarray = np.asarray(altitude.to_value(u.km), dtype=float)
        
        if z < 0:
            
            logger.warning("'altitude' cannot be < 0 km")
            
            return None
        
        # * altitude
        
        err_msg = validate_type("thermodynamic_consistency", thermodynamic_consistency, bool)
        
        if err_msg: logger.warning(err_msg); return None
        
        # >>> Algorithm
        
        temperature: u.Quantity = self.temperature_interpolator(z) * u.K
        
        pressure: u.Quantity = np.exp(self.pressure_interpolator(z)) * u.kPa
        
        density: u.Quantity = np.exp(self.density_interpolator(z)) * u.kg / u.m**3
        
        if thermodynamic_consistency:
            
            R: u.Quantity = sl_constants.atmospheric_gas_constant
            
            density = (pressure.to(u.Pa) / (R * temperature)).decompose()
        
        return temperature, pressure.to(u.Pa), density

    def sample_properties(
        self, altitude_grid: ty.Iterable[u.Quantity] | None = None, thermodynamic_consistency: bool = False) -> ty.List[np.ndarray] | None:
        """
        Samples the thermodynamic properties from the given grid of altitudes. If the grid is not given, a default one
        is used (0 km - 1000 km).

        :param altitude_grid: List of altitude values, defaults to None
        :type altitude_grid: ty.Iterable[u.Quantity] | None, optional
        :param thermodynamic_consistency: Enforce thermodynamic consistency, defaults to False
        :type thermodynamic_consistency: bool, optional
        :return: Arrays for temperature (K), pressure (kPa), and density (kg / m**3)
        :rtype: ty.List[np.ndarray] | None
        """
        
        # >>> Validation
        
        # * altitude_grid
        
        if altitude_grid is not None and not isinstance(altitude_grid, ty.Iterable):
            
            logger.warning(f"'altitude_grid' expected {ty.Iterable[u.Quantity]}, got {type(altitude_grid)}")
            
            return None

        for i, item in enumerate([] if altitude_grid is None else altitude_grid):

            if not isinstance(item, u.Quantity):

                return (f"'altitude_grid[{i}]' expected {u.Quantity}, got {type(item)}")
            
            if item.to_value(u.km) < 0:
                
                logger.warning(f"'altitude_grid[{i}]' cannot be < 0 km")
                
                return None
            
        # * thermodynamic_consistency
        
        err_msg = validate_type("thermodynamic_consistency", thermodynamic_consistency, bool)
        
        if err_msg: logger.warning(err_msg); return None
        
        # >>> Algorithm
        
        altitudes: u.Quantity = np.linspace(0, 1000, 1000) * u.km if altitude_grid is None else u.Quantity(altitude_grid)

        temperatures: list[float] = []
        pressures: list[float] = []
        densities: list[float] = []

        for altitude in altitudes:
            
            res = self.thermodynamic_properties(altitude=altitude, thermodynamic_consistency=thermodynamic_consistency)
            
            if res == None: return None
            
            temperature, pressure, density = res

            temperatures.append(temperature.to_value(u.K))
            pressures.append(pressure.to_value(u.kPa))
            densities.append(density.to_value(u.kg / u.m**3))

        return np.asarray(temperatures), np.asarray(pressures), np.asarray(densities)
    
    def density(self, altitude: u.Quantity, model: AtmosphereModel = AtmosphereModel.USSA76) -> ty.List[u.Quantity]:
        """
        Calculates the atmospheric density given the altitude above the Earth using one of the following models:
        
        - *USSA76* piecewise exponential model
        - *CIRA-72* piecewise exponential model

        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 12.4 "Atmospheric Drag"`
        - :cite:`(4) Section 6.1.3 "Piecewise-Expoìonential Model"`

        📌 **Notes**
        
        The given altitude is located in the values of the altitude ranges. For example, and altitude of 249 km will be
        located in the range 200-250 but uses the value of 200 km reference altitude.

        :param altitude: Altitude
        :type altitude: u.Quantity
        :param model: Atmosphere model, defaults to AtmosphereModel.USSA76
        :type model: AtmosphereModel, optional
        :return: Density and scale height
        :rtype: ty.List[u.Quantity]
        """
        
        # >>> Validation
        
        # * altitude
        
        err_msg = validate_quantity("altitude", altitude, u.m)
        
        if err_msg: logger.warning(err_msg); return None
        
        z: float = altitude.to_value(u.km)
        
        if z < 0:
            
            logger.warning("'altitude' cannot be < 0 km")
            
            return None
            
        # * model
        
        err_msg = validate_type("model", model, AtmosphereModel)
        
        if err_msg: logger.warning(err_msg); return None
        
        # >>> Algorithm
        
        h: np.ndarray = self.altitude
        rho: np.ndarray
        H: np.ndarray
        
        if model == AtmosphereModel.USSA76:
            
            rho = self.density_USSA76
            H = self.scale_height_USSA76
        
        elif model == AtmosphereModel.CIRA72:
            
            rho = self.density_CIRA72
            H = self.scale_height_CIRA72
        
        # * Handle altitudes outside of the range
        
        if z > h[-1]:
            
            z = h[-1]
            
        elif z < h[0]:
            
            logger.warning(f"'altitude' is below {h[0]} km, using density at {h[0]} km")
            
            z = h[0]
        
        # * Determine the interpolation interval
        
        idx: int = np.searchsorted(h, z) - 1
        
        idx = np.clip(idx, 0, len(H) - 1)
        
        # * Exponential interpolation
        
        rho_z: u.Quantity = rho[idx] * np.exp(-(z - h[idx]) / H[idx]) * u.kg / u.m**3
        
        return rho_z, H[idx] * u.km
