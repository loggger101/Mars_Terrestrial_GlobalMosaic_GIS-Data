# -*- coding: utf-8 -*-
r"""How big is a 15° block? Each latitude band's block against the US state nearest it in area (KB §69.15).

The held-out split puts whole 15° x 15° blocks on one side (make_global60_classification.py, BLOCK_DEG): edges on
multiples of 15° of latitude and longitude, so over ±60° there are 24 x 8 = 192 blocks, in four bands of latitude
mirrored about the equator. A block's area on the project's sphere (R = 3,396,190 m, the CRS of every grid, §18):

    A = R² · Δλ · (sin φ2 − sin φ1)

Its shape, for the deck's drawing: N-S side R·Δφ, E-W edges R·Δλ·cos φ at each latitude.
State areas: US Census Bureau, 2010 census, total area (land and water); the five largest, which is enough, since
every block lies between Montana's area and Alaska's. Nearest is by ratio, the way a reader compares sizes.

    python interim_block_scale.py            (either Python)
"""
import math
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R_KM = 3396.19
BLOCK = 15.0
MI2 = 2.589988                                   # km² in one square mile
STATES = {                                       # km², 2010 census total area
    "Alaska": 1723337, "Texas": 695662, "California": 423967, "Montana": 380831, "New Mexico": 314917}


def block_km2(lat0):
    return R_KM ** 2 * math.radians(BLOCK) * (math.sin(math.radians(lat0 + BLOCK)) - math.sin(math.radians(lat0)))


def nearest(a):
    return min(STATES, key=lambda s: abs(math.log(a / STATES[s])))


def side_km(lat):
    return R_KM * math.radians(BLOCK) * math.cos(math.radians(lat))


if __name__ == "__main__":
    print("N-S side of every block: %.1f km" % (R_KM * math.radians(BLOCK)))
    for lat0 in (0, 15, 30, 45):
        a = block_km2(lat0)
        s = nearest(a)
        print("%2d-%2d°  %9.0f km²  %8.0f mi²  E-W %5.1f -> %5.1f km   nearest %-10s %9d km²  x%.2f"
              % (lat0, lat0 + BLOCK, a, a / MI2, side_km(lat0), side_km(lat0 + BLOCK), s, STATES[s], a / STATES[s]))
    band = 4 * math.pi * R_KM ** 2 * math.sin(math.radians(60))
    print("±60° band: %d blocks, %.0f km², mean block %.0f km²" % (24 * 8, band, band / 192))
