# Import
import numpy as np
import multiprocessing
import functools
import reps


# Constants
# Order of the T_d group and \Gamma_8 representation
h = 4.0 # dimension of the Gamma8 representation
L = 48.0 # dimension of the T_d double group
# Integration - GaAs
lc = 5.3435 * 2.0 # cubic lattice constant

# Functions

# Takes file containing state and stores it in appropriate format
def importData(fileName):
    output = []

    for line in open(fileName):
        l = line.split()
        x = [float(elem) for elem in l]
        coord = [round(elem,6) for elem in x[0:3]]
        spin = [x[3]+1j*x[4], x[5]+1j*x[6]]
        s = [coord] + [np.array(spin)]

        output.append(s)

    return output

# Function to perform a rotation on a point
def ROT( pt, r, RS, rho ):

    newr = np.dot(r, np.array(pt[0]))
    newspin = h/L*np.conjugate(rho)*np.dot(RS, pt[1])
    return [[round(elem,6) for elem in newr], newspin]

# Function to get state in an appropriate domain
def cubify( state ):
    pt = state[1][1]
    
    newstate = []
    for coord in state:
        if pt not in coord[0:3]:
            newstate.append(coord)

    return newstate

# Normalization
def Normalize( state ):
    delta = lc**3/len(state)
    S = sum([np.absolute(x[0])**2+np.absolute(x[1])**2 for x in state])
    return delta*S

# Inputs

# state file
n = input('npts value: ')
fileName = 'psi_npts' + str(n) + '.OUT'

# Number of cores to be used by the parallelized part of the computation
nCores = input('number of cores: ')

# Wavefunction
Psi = importData(fileName)
Psi.sort()

# start multiprocessing pool
p = multiprocessing.Pool(nCores)

# loop over 4 \Gamma_8 basis states
labels = ['HHd', 'LHd', 'LHu', 'HHu']

for ii in range(4):
    projPsi = [np.array([0,0])]*len(Psi)

    # projection
    for jj, rot in enumerate(reps.R):
        rs = reps.wD12[jj]
        RHO = reps.wD32[jj][ii,ii]

        rotPsi = p.map(functools.partial(ROT, r=rot, RS=rs, rho=RHO), Psi)
        rotPsi.sort()
        projPsi = [sum(x) for x in zip(projPsi, [y[1] for y in rotPsi])]

        outputPsi = []
        for kk, coord in enumerate(Psi):
            l = coord[0] + [projPsi[kk]]
            outputPsi.append(l)

        # define wavefunction on a grid for proper normalization
        outputPsi = cubify(outputPsi)
        
        # normalize
        spinors = [x[3] for x in outputPsi]
        N = Normalize(spinors)

        finalPsi = []
        for phi in outputPsi:
            nspin = list(np.sqrt(1.0/N)*phi[3])
            x = phi[0:3] + nspin
            finalPsi.append(x)

        # output state
        with open('proj' + str(labels[ii]) + '.OUT', 'w') as f:
            for x in finalPsi:
                x = [str(elem) for elem in x]
                f.write('    '.join(x) + '\n')