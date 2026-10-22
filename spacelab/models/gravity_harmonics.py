import dataclasses as dc
import typing

@dc.dataclass
class GravityHarmonics:
    C: typing.Dict[typing.Tuple[int, int], float] # ? Tesseral coefficients (n, m) -> C_nm
    S: typing.Dict[typing.Tuple[int, int], float] # ? Tesseral coefficients (n, m) -> S_nm
    J: typing.Dict[typing.Tuple[int, int], float] # ? Zonal coefficients    (n, m) -> J_nm = np.sqrt(C_nm**2 + S_nm**2)
    L: typing.Dict[typing.Tuple[int, int], float] # ? Geographic longitude  (n, m) -> L_nm
