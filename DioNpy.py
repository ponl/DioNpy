#!/usr/bin/python2

"""
    DioNpy: A NumPy interface for Dionysus
    Copyright (C) 2015 Patrick A. O'Neil (ponl@poneil.com)

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    
    
    Dionysus was written by Dmitriy Morozov (dmitriy@mrzv.org)
"""

def load_npy(path):
    try:
        data = np.load(path)
        return data
    except IOError:
        print "Failed to read NumPy file: " + path
        sys.exit(0)
        return False


import sys
import numpy as np
from dionysus import *

if len(sys.argv) != 3:
    print """
    DioNpy: A simple interface for Dionysus. (Currently only reads npy point clouds)

    Usage:
    ./DioNpy.py input.npy pers.npy

    Currently only implements alpha-shapes from Dionysus
    """
    sys.exit(0)

points = []

inPath = sys.argv[1]
outPath = sys.argv[2]

#TODO: Implement other filtration types
filtType = 'a'          # a: alpha, r: rips

ext = inPath.split('.')[-1]

N = 0   # Number of points in cloud data
d = 0   # Dimension of point cloud data

# Rips Settings
k = 3       # k-skeleton
rmax = 50

# -- Numpy Input -- #
if ext == 'npy':
    ndat = load_npy(inPath)
    N = len(ndat)
    d = len(ndat[0])
    for row in ndat:
        points.append(list(row))

else:
    print "Unrecognized file extension: " + inPath
    sys.exit(0)


# --- Compute Filtrations --- #

simplices = Filtration()

if filtType == 'a':
    if d == 2:
        fill_alpha2D_complex(points, simplices)
    elif d == 3:
        fill_alpha3D_complex(points, simplices)
    else:
        print "Dionysus does not support alpha complexes of dimension (" + str(d) + ")."
        sys.exit(0)
        #filtType == 'r'

"""
if filtType == 'r':
    distances = PairwiseDistances(points)
    rips = Rips(distances)
    rips.generate(k, rmax, simplices.append)
"""

# --- Compute Persistence --- #
if filtType == 'a':
    simplices.sort(data_dim_cmp)
else:
    simplices.sort(rips.cmp)

p = StaticPersistence(simplices)
p.pair_simplices()

smap = p.make_simplex_map(simplices)

pers = [[],[],[]]
for i in p:
    if i.sign():
        birth = smap[i]
        if birth.data[1]: # Ignore zero persistence pair
            dim = birth.dimension()
            if i.unpaired():
                pers[dim].append([birth.data[0], -1])
            else:
                death = smap[i.pair()]
                pers[dim].append([birth.data[0],death.data[0]])


# --- Save Persistence Data --- #
cnt = 0
for p in pers:
    if len(p):
        pPath = outPath + str(cnt) + '.npy'
        cnt += 1
        
        np.save(pPath, np.array(p))





