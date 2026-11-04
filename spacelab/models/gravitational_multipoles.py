import astropy.units as u
import csv
import numpy as np
import pathlib as pl
import typing as ty

from spacelab.utils.logger import logger
from spacelab.utils.singleton import Singleton
from spacelab.utils.validator import validate_quantity

import spacelab.bodies as sl_bodies

class GravitationalMultipoles(Singleton):
    """
    **Gravitational multipoles** describes the spatial distribution of mass and momentum in a gravitational system,
    breaking down a complex gravitational field into a series of terms with increasingly finer angular features.

    🧮 **Attributes**
    
    C : Dict[Tuple[int, int], float]
        Cosine coefficients
    
    S : Dict[Tuple[int, int], float]
        Sine coefficients
    
    J : Dict[Tuple[int, int], float]
        Harmonic coefficients
    
    L : Dict[Tuple[int, int], float]
        Geographic equilibrium longitudes
    
    j : Dict[Tuple[int, int], float]
        Reduced harmonic coefficients
    
    📌 **Notes**
    
    Because the detailed density distribution of the Earth is beyond our knowledge, the multipole coefficients
    :math:`C_{nm}` and :math:`S_{nm}` are available only by measuring them with particular satellites. The most famous
    and most precise of them is the *GRACE* satellite mission, which operated from 2002 to 2017.
    
    The harmonic amplitudes are calculated as :math:`J_{nm} = \\sqrt{C_{nm}^2 + S_{nm}^2}`.
    
    The Geographic longitudes are calculated as :math:`\\lambda_{nm} = 2 / m \\cdot \\arctan({S_{nm} / (C_{nm} + J_{nm})})`.
    
    Terminology:
    
    - *Zonal Harmonics* (:math:`m = 0`) describe latitudinal variations
    - *Sectorial Harmonics* (:math:`n = m`) describe longitudinal variations
    - *Tesseral Harmonics* (:math:`0 < m < n`) describe mixed variations
    
    📖 **References**
    
    - :cite:`walter`
        - Chapter 12 *Orbit Perturbations*
    """
    
    C: ty.Dict[ty.Tuple[int, int], float]
    S: ty.Dict[ty.Tuple[int, int], float]
    J: ty.Dict[ty.Tuple[int, int], float]
    L: ty.Dict[ty.Tuple[int, int], float]
    j: ty.Dict[ty.Tuple[int, int], float] # NOSONAR python:S1845
    
    def _singleton_init(self):
        
        self.C = {}
        self.S = {}
        self.J = {}
        self.L = {}
        self.j = {}
        
        self.load_earth_harmonic_coefficients()
    
    def load_earth_harmonic_coefficients(self) -> None:
        """
        Loads the multipole coefficients of Earth's gravitational potential.
        
        📖 **References**
        
        - :cite:`walter`
            - Section 12.2.2 *Gravitational Potential*
        """
        
        file: pl.Path = pl.Path(__file__).parent / "gravitational_multipoles.csv"
        
        if not file.exists():
            
            logger.error(f"File {file} not found")
            
            return
        
        with open(file=file, mode="r", newline="") as f:
            
            logger.info(f"File {file} loaded")
            
            reader: csv.DictReader[str] = csv.DictReader(f)
            
            for row in reader:
                
                n: int = int(row["n"])
                m: int = int(row["m"])

                if row["C"]: self.C[(n, m)] = float(row["C"])
                if row["S"]: self.S[(n, m)] = float(row["S"])
                if row["J"]: self.J[(n, m)] = float(row["J"])
                if row["L"]: self.L[(n, m)] = np.deg2rad(float(row["L"]))
        
                # * Compute tesseral harmonics
                
                if (n, m) not in self.J and (n, m) in self.C and (n, m) in self.S:
                
                    self.J[(n, m)] = np.sqrt(self.C[(n, m)]**2 + self.S[(n, m)]**2)
    
    def calc_earth_reduced_harmonic_coefficients(self, semimajor_axis: u.Quantity, eccentricity: u.Quantity) -> bool:
        """
        Calculates the earth reduced harmonic coefficients :math:`j_{nm}`.
        
        :param semimajor_axis: Semimajor axis
        :type semimajor_axis: u.Quantity
        :param eccentricity: Eccentricity
        :type eccentricity: u.Quantity
        :return: Success
        :rtype: bool
        
        📌 **Notes**
        
        The common factor 3/2 is a remnant of orbit averaging.
        
        📖 **References**
        
        - :cite:`walter`
            - Section 12.3.2 *Removing Short-Periodic Effects*
        """
        
        # >>> Validation
        
        # * semimajor_axis
        
        err_msg: str | None = validate_quantity("semimajor_axis", semimajor_axis, u.m)
        
        if err_msg: logger.warning(err_msg); return False
        
        sma: float = semimajor_axis.to_value(u.km)
        
        # * eccentricity
        
        err_msg = validate_quantity("eccentricity", eccentricity, u.one)
        
        if err_msg: logger.warning(err_msg); return False
        
        ecc: float = eccentricity.to_value(u.one)
        
        # * Check
        
        r_e: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        if sma < r_e:
            
            err_msg = f"Semimajor axis shall be greater than Earth radius ({sma} km < {r_e} km)"
            
            logger.warning(err_msg)
            
            return False
        
        # >>> Algorithm

        p: float = sma * (1 - ecc**2) # ? Semilatus Rectum
        
        self.j = { (n, m): 3 / 2 * self.J[(n, m)] * (r_e / p)**n for (n, m) in self.J.keys() }

        return True
