###
# Copyright 2008-2019 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###
import types
from math import sin, cos, acos, atan2, sqrt

from diffcalc.gdasupport.scannable.parametrised_hkl import ParametrisedHKLScannable
from diffcalc.util import DiffcalcException
from diffcalc.dc import dcyou as _dc

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

circ_hkl = ParametrisedHKLScannable('circ', ('q', 'pol', 'az'))
circ_hkl.parameter_to_hkl = lambda (q, pol, az): (q * sin(pol) * cos(az), q * sin(pol) * sin(az), q * cos(pol))
circ_hkl.hkl_to_parameter = lambda (h, k, l): (sqrt(h*h+k*k+l*l), acos(l/sqrt(h*h+k*k+l*l)), atan2(k, h))

def __polar_to_hkl(params):
    from diffcalc.dc import dcyou as _dc
    from diffcalc.util import norm3, cross3
    import __main__

    sc, az = params
    h, k, l = __main__.hkl.getPosition()[:3]
    hkl_nphi = _dc._ub.ubcalc._UB * matrix([[h], [k], [l]])
    try:
        h_ref, k_ref, l_ref = _dc._ub.ubcalc.get_reflection(1)[0]
        ref_nphi = _dc._ub.ubcalc._UB * matrix([[h_ref], [k_ref], [l_ref]])
        ref_nphi *= norm3(hkl_nphi) / norm3(ref_nphi)
    except IndexError:
        raise DiffcalcException("Please add one reference reflection into the reflection list.")
    nphi = _dc._ub.ubcalc.n_phi
    inplane_vec = cross3(ref_nphi, nphi)
    inplane_vec *= sqrt(1 - sc ** 2) * norm3(hkl_nphi) / norm3(inplane_vec)
    ref_nhkl = _dc._ub.ubcalc._UB.I * ref_nphi
    h_ref, k_ref, l_ref = ref_nhkl.T.tolist()[0]  
    h_res, k_res, l_res = _dc._ub.ubcalc.calc_hkl_offset(h_ref, k_ref, l_ref, acos(sc), az)
    return h_res, k_res, l_res

def __hkl_to_polar(hkl):
    from diffcalc.dc import dcyou as _dc

    try:
        hkl_ref = _dc._ub.ubcalc.get_reflection(1)[0]
    except IndexError:
        raise DiffcalcException("Please add one reference reflection into the reflection list.")
    pol, az, _ = _dc._ub.ubcalc.calc_offset_for_hkl(hkl, hkl_ref)
    return cos(pol), az

conic_hkl = ParametrisedHKLScannable('conic', ('rlu', 'az'))
conic_hkl.parameter_to_hkl = __polar_to_hkl
conic_hkl.hkl_to_parameter = __hkl_to_polar

def __conic_h_to_hkl(self, params):
    from diffcalc.dc import dcyou as _dc
    from diffcalc.util import norm3, solve_h_fixed_q
    import __main__

    try:
        h_param, a, b, c, d = params
    except TypeError:
        raise DiffcalcException("Invalid number of input parameters.")
    h, k, l = __main__.hkl.getPosition()[:3]
    hkl_nphi = _dc._ub.ubcalc._UB * matrix([[h], [k], [l]])
    qval = norm3(hkl_nphi)**2
    hkl = solve_h_fixed_q(h_param, qval, _dc._ub.ubcalc._UB, (a, b, c, d))
    return hkl

def __hkl_to_conic_h(self, hkl):
    h, _, _ = hkl
    try:
        a, b, c, d = self.cached_params
    except TypeError:
        raise DiffcalcException("hkl constraint values not set.")
    return (h, a, b, c, d)

conic_h = ParametrisedHKLScannable('conic_h', ('h', 'a', 'b', 'c', 'd'), 4)
conic_h.parameter_to_hkl = types.MethodType(__conic_h_to_hkl, conic_h)
conic_h.hkl_to_parameter = types.MethodType(__hkl_to_conic_h, conic_h)

def __conic_k_to_hkl(self, params):
    from diffcalc.dc import dcyou as _dc
    from diffcalc.util import norm3, solve_k_fixed_q
    import __main__

    try:
        k_param, a, b, c, d = params
    except TypeError:
        raise DiffcalcException("Invalid number of input parameters.")
    h, k, l = __main__.hkl.getPosition()[:3]
    hkl_nphi = _dc._ub.ubcalc._UB * matrix([[h], [k], [l]])
    qval = norm3(hkl_nphi)**2
    hkl = solve_k_fixed_q(k_param, qval, _dc._ub.ubcalc._UB, (a, b, c, d))
    return hkl

def __hkl_to_conic_k(self, hkl):
    _, k, _ = hkl
    try:
        a, b, c, d = self.cached_params
    except TypeError:
        raise DiffcalcException("hkl constraint values not set.")
    return (k, a, b, c, d)

conic_k = ParametrisedHKLScannable('conic_k', ('k', 'a', 'b', 'c', 'd'), 4)
conic_k.parameter_to_hkl = types.MethodType(__conic_k_to_hkl, conic_k)
conic_k.hkl_to_parameter = types.MethodType(__hkl_to_conic_k, conic_k)

def __conic_l_to_hkl(self, params):
    from diffcalc.dc import dcyou as _dc
    from diffcalc.util import norm3, solve_l_fixed_q
    import __main__

    try:
        l_param, a, b, c, d = params
    except TypeError:
        raise DiffcalcException("Invalid number of input parameters.")
    h, k, l = __main__.hkl.getPosition()[:3]
    hkl_nphi = _dc._ub.ubcalc._UB * matrix([[h], [k], [l]])
    qval = norm3(hkl_nphi)**2
    hkl = solve_l_fixed_q(l_param, qval, _dc._ub.ubcalc._UB, (a, b, c, d))
    return hkl

def __hkl_to_conic_l(self, hkl):
    _, _, l = hkl
    try:
        a, b, c, d = self.cached_params
    except TypeError:
        raise DiffcalcException("hkl constraint values not set.")
    return (l, a, b, c, d)

conic_l = ParametrisedHKLScannable('conic_l', ('l', 'a', 'b', 'c', 'd'), 4)
conic_l.parameter_to_hkl = types.MethodType(__conic_l_to_hkl, conic_l)
conic_l.hkl_to_parameter = types.MethodType(__hkl_to_conic_l, conic_l)