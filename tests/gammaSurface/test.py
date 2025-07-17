# /opt/local/bin/python3.13 test.py
import sys, string, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
plt.rcParams['text.usetex'] = True
sys.path.append("../../python")
from modlibUtils import *
sys.path.append("../../build/tools/pyMoDELib")
import pyMoDELib

materialFile="../../Library/Materials/Ni.txt"
absoluteTemperature=0.0
mat=pyMoDELib.PolycrystallineMaterialBase(materialFile,absoluteTemperature)
energyDensityScaling=mat.mu_SI*mat.b_SI
C2G=np.array([[1,0,0],[0,1,0],[0,0,1]])
singleCrystal=pyMoDELib.SingleCrystalBase(mat,C2G)

# initialize
n0=2 # image repetitions along first direction
n1=2 # image repetitions along second direction
nR=4
pts=50 # GSFE resolution in each direction
X=np.zeros((pts+1,pts+1))
Y=np.zeros((pts+1,pts+1))
GSFE=dict() # stores GSFE of matrix and other phases
GSFE["matrix"]=np.zeros((pts+1,pts+1))
for phaseKey, phaseValue in singleCrystal.secondPhases().items():
   GSFE[phaseValue.name]=np.zeros((pts+1,pts+1))

# Compute and plot
for planeKey, planeValue in singleCrystal.planeNormals().items(): # loop over lattice planes
    b0=planeValue.primitiveVectors[0].cartesian() # first primitive vector of the matrix lattice plane
    b1=planeValue.primitiveVectors[1].cartesian() # second primitive vector of the matrix lattice plane
    gammaSurface=planeValue.gammaSurface
    a0=gammaSurface.A[:,0]
    a1=gammaSurface.A[:,1]
    r0=gammaSurface.B[:,0]
    r1=gammaSurface.B[:,1]
#    gammaSurface=planeValue.gammaSurface
#    gammaSurface.B
#    print(planeValue.gammaSurface.B)
    for i in range(pts+1):
        for j in range(pts+1):
            s=i*n0/pts*b0+j*n1/pts*b1 # slip vector
            sL=planeValue.localSlipVector(s) # slip vector in the plane local coordinates
            X[j,i]=sL[0]
            Y[j,i]=sL[1]
            GSFE["matrix"][j,i]=planeValue.misfitEnergy(s)*energyDensityScaling
            for phaseKey, phaseValue in singleCrystal.secondPhases().items():
#                phaseGammaSurface=phaseValue.gammaSurface(planeKey)
                GSFE[phaseValue.name][j,i]=phaseValue.misfitEnergy(s,planeKey)*energyDensityScaling

    # Plot GSFE surface
    fig, axs = plt.subplots(2,2)
    axs[0, 0].set_aspect("equal")
    pmsh=axs[0, 0].pcolormesh (X, Y, GSFE["matrix"],cmap=cm.coolwarm,shading='gouraud')
    axs[0, 0].arrow(0, 0, a0[0], a0[1])
    axs[0, 0].arrow(0, 0, a1[0], a1[1])
    
    axs[0, 1].set_aspect("equal")
    axs[0, 1].arrow(0, 0, r0[0], r0[1])
    axs[0, 1].arrow(0, 0, r1[0], r1[1])
    for i in range(-nR,nR):
        for j in range(-nR,nR):
            r=i*r0+j*r1
            axs[0, 1].scatter(r[0],r[1],0.1,color='k')
    axs[0, 1].scatter(planeValue.gammaSurface.waveVectors[:,0],planeValue.gammaSurface.waveVectors[:,1],color='m')

    
#    fig.colorbar(pmsh)
    fig.savefig(mat.materialName+"_plane_"+str(planeKey)+"_matrix", bbox_inches='tight')
        
    for phaseKey, phaseValue in singleCrystal.secondPhases().items():
        phaseGammaSurface=phaseValue.gammaSurface(planeKey)
        a0=phaseGammaSurface.A[:,0]
        a1=phaseGammaSurface.A[:,1]
        r0=phaseGammaSurface.B[:,0]
        r1=phaseGammaSurface.B[:,1]
        axs[0, 1].arrow(0, 0, r0[0], r0[1])
        axs[0, 1].arrow(0, 0, r1[0], r1[1])
        for i in range(-nR,nR):
            for j in range(-nR,nR):
                r=i*r0+j*r1
                axs[0, 1].scatter(r[0],r[1],0.1,color='k')
        pmsh=axs[0, 0].pcolormesh (X, Y, GSFE[phaseValue.name],cmap=cm.coolwarm,shading='gouraud')
        axs[0, 0].arrow(0, 0, a0[0], a0[1])
        axs[0, 0].arrow(0, 0, a1[0], a1[1])
#        fig.colorbar(pmsh)
        fig.savefig(mat.materialName+"_plane_"+str(planeKey)+"_"+phaseValue.name, bbox_inches='tight')
