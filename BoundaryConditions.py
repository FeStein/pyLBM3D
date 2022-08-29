import numpy as np
import Util
import copy
import sys

def selectAtCoordinate(fArg, coordinateArg='x', coordinateValueArg=0):
    if coordinateArg == 'x':
        outF = fArg[coordinateValueArg]
    elif coordinateArg == 'y':
        outF = fArg[:, coordinateValueArg, :]
    elif coordinateArg == 'z':
        outF = fArg[:, :, coordinateValueArg]
    return outF

# test selectAtCoordinate


def getMissingDistributionFunctionIndices(fArg, coordinateArg='x', coordinateValueArg=0):
    if coordinateArg == 'x' and coordinateValueArg == 0:
        outIndices = [1, 7, 9, 13, 15, 19, 21, 23, 26] # all c with posititve cx cross min x boundary
    elif coordinateArg == 'x' and coordinateValueArg == len(fArg)-1:
        outIndices = [2, 8, 10, 14, 16, 20, 22, 24, 25]
    elif coordinateArg == 'y' and coordinateValueArg == 0:
        outIndices = [3, 7, 11, 14, 17, 19, 21, 24, 25]
    elif coordinateArg == 'y' and coordinateValueArg == len(fArg[0])-1:
        outIndices = [4, 8, 12, 13, 18, 20, 22, 23, 26]
    elif coordinateArg == 'z' and coordinateValueArg == 0:
        outIndices = [5, 9, 11, 16, 18, 19, 22, 23, 25]
    elif coordinateArg == 'z' and coordinateValueArg == len(fArg[0][0]) - 1:
        outIndices = [6, 10, 12, 15, 17, 20, 21, 24, 26]
    return outIndices




def missingInterpolationNeighbor():
    return np.array([sys.maxsize, sys.maxsize, sys.maxsize])


def selectInterpolationNeighbors(arrayArg,  ccArg, cArg, coordinateArg='x', coordinateValueArg=0): # just normal to plane defined by coordinateArg = const
    def findInterpolationNeigbor(potentialNeigborCoordinates, iArg, jArg, kArg, lArg, arrayArg, ccArg, cArg): # treats edge cases
        def interpolationNeighborIsNeeded(arrayArg, lArg, coordinateArg,
                                                   coordinateValueArg):  # it only makes sense to determine the interpolation neighbors for missing distribution functions at that boundary
            if lArg in getMissingDistributionFunctionIndices(arrayArg, coordinateArg, coordinateValueArg):
                return True
            else:
                return False
        if not interpolationNeighborIsNeeded(arrayArg,lArg,coordinateArg,coordinateValueArg):
            return missingInterpolationNeighbor()
        if Util.checkIfIndicesInArrayBounds(potentialNeigborCoordinates[0], potentialNeigborCoordinates[1], potentialNeigborCoordinates[2], arrayArg):
            return potentialNeigborCoordinates
        else:

            if coordinateArg == 'x': # 1 or 2 have to exist
                if coordinateValueArg == 0: # map everything missing to c1
                    ccMapped = ccArg[1]
                elif coordinateValueArg == len(arrayArg) - 1:
                    ccMapped = ccArg[2]
                else:
                    raise Exception("Either top or max value at boundary")
            elif coordinateArg == 'y':
                if coordinateValueArg == 0: # map everything missing to c3
                    ccMapped = ccArg[3]
                elif coordinateValueArg == len(arrayArg[0]) - 1:
                    ccMapped = ccArg[4]
                else:
                    raise Exception("Either top or max value at boundary")
            elif coordinateArg == 'z':
                if coordinateValueArg == 0:  # map everything missing to c3
                    ccMapped = ccArg[5]
                elif coordinateValueArg == len(arrayArg[0][0]) - 1:
                    ccMapped = ccArg[6]
                else:
                    raise Exception("Either top or max value at boundary")
            cL = 1.0 / cArg * ccMapped
            newPotentialNeigborCoordinates = np.array([int(iArg + cL[0]), int(jArg + cL[1]), int(kArg + cL[2])])
        if not Util.checkIfIndicesInArrayBounds(newPotentialNeigborCoordinates[0], newPotentialNeigborCoordinates[1], newPotentialNeigborCoordinates[2], arrayArg):
            raise Exception("Interpolation neighbor shoult be in domain after correction")
        return newPotentialNeigborCoordinates




    arrayAtCoordinate = selectAtCoordinate(arrayArg, coordinateArg, coordinateValueArg)
    outNeighbors = np.zeros((len(arrayAtCoordinate), len(arrayAtCoordinate[0]), 27, 3), dtype=int) # saves i,j,k indices in arrayArg
    outNeighbors.fill(np.nan)
    for i in range(0, len(arrayAtCoordinate)):
        for j in range (0, len(arrayAtCoordinate[0])):
            for l in range(0, 27):
                cL = 1.0 / cArg * ccArg[l]
                if coordinateArg == 'x':
                    ii = coordinateValueArg
                    jj = i
                    kk = j
                elif coordinateArg == 'y':
                    ii = i
                    jj = coordinateValueArg
                    kk = j
                elif coordinateArg == 'z':
                    ii = i
                    jj = j
                    kk = coordinateValueArg

                potentialNeigborCoordinates = [int(ii + cL[0]), int(jj + cL[1]), int(kk + cL[2])]
                neigborCoordinates = findInterpolationNeigbor(potentialNeigborCoordinates,ii,jj,kk,l,arrayArg,ccArg,cArg)
                outNeighbors[i, j, l] = np.array(
                    [neigborCoordinates[0], neigborCoordinates[1], neigborCoordinates[2]])

                #if checkIfIndicesInArrayBounds(potentialNeigborCoordinates[0], potentialNeigborCoordinates[1], potentialNeigborCoordinates[2], arrayArg):
                #if potentialNeigborCoordinates[0] < len(arrayArg) and potentialNeigborCoordinates[1] < len(arrayArg[0]) and potentialNeigborCoordinates[2] < len(arrayArg[0][0]):
                #    outNeighbors[i,j,l] = np.array([potentialNeigborCoordinates[0], potentialNeigborCoordinates[1], potentialNeigborCoordinates[2]])
    return copy.deepcopy(outNeighbors)


# TODO muessen RBen pro Verteilungsfunktion beruecksichtigt werden?


def interpolationNeighborExists(indicesArg):
    return indicesArg[0] != missingInterpolationNeighbor()[0] and indicesArg[1] != missingInterpolationNeighbor()[1] and indicesArg[2] != missingInterpolationNeighbor()[2]

def extrapolateScalarToBd(rhoArg, ccArg, cArg, coordinateArg='x', coordinateValueArg=0):
    rhoBoundary = copy.deepcopy(selectAtCoordinate(rhoArg, coordinateArg, coordinateValueArg))
    IndicesInterpolationNeigbors = selectInterpolationNeighbors(rhoArg, ccArg, cArg, coordinateArg, coordinateValueArg)
    rhoBoundaryOut = np.zeros((len(rhoBoundary), len(rhoBoundary[0]), 27), dtype=float)
    for i in range(0, len(rhoBoundaryOut)):
        for j in range(0, len(rhoBoundaryOut[0])):
            for l in range(0, len(rhoBoundaryOut[0][0])):
                if(interpolationNeighborExists(IndicesInterpolationNeigbors[i,j,l])):
                    rhoBoundaryOut[i,j,l] = 0.5*(3.0 * rhoBoundary[i,j] - rhoArg[IndicesInterpolationNeigbors[i,j,l,0], IndicesInterpolationNeigbors[i,j,l,1], IndicesInterpolationNeigbors[i,j,l,2]])
    return rhoBoundaryOut

# extrapolates second order tensor to boundary
def extrapolateTensorToBd(sigmaArg, ccArg, cArg, coordinateArg='x', coordinateValueArg=0):
    #def interpolationNeighborExists(indicesArg):
    #    return indicesArg[0] != -1 and indicesArg[1] != -1 and indicesArg[2] != -1

    sigmaBoundary = copy.deepcopy(selectAtCoordinate(sigmaArg, coordinateArg, coordinateValueArg))
    IndicesInterpolationNeigbors = selectInterpolationNeighbors(sigmaArg, ccArg, cArg, coordinateArg, coordinateValueArg)
    sigmaBdOut = np.zeros((len(sigmaBoundary), len(sigmaBoundary[0]), 27, 3, 3), dtype=float)
    for i in range(0, len(sigmaBdOut)):
        for j in range(0, len(sigmaBdOut[0])):
            for l in range(0, len(sigmaBdOut[0][0])):
                if (interpolationNeighborExists(IndicesInterpolationNeigbors[i, j, l])):
                    sigmaBdOut[i, j, l] = 0.5 * (3.0 * sigmaBoundary[i, j] - sigmaArg[IndicesInterpolationNeigbors[i, j, l, 0], IndicesInterpolationNeigbors[i, j, l, 1],IndicesInterpolationNeigbors[i, j, l, 2]])
    return sigmaBdOut


def getOppositeLatticeDirection(latticeDirection=0): # fits for Krueger convention D2Q27
    if (latticeDirection == 0):
        return 0
    elif (latticeDirection % 2 == 0):
        return (latticeDirection - 1)
    elif not (latticeDirection % 2 == 0):
        return (latticeDirection + 1)


def applyDirichletBoundaryConditions(fArg, fCollArg, rhoArg, csArg, ccArg, cArg, wArg, uBdArg, coordinateArg='x', coordinateValueArg=0):  # TODO not defined how edges/corners are handled
    rhoBd = extrapolateScalarToBd(rhoArg, ccArg, cArg, coordinateArg, coordinateValueArg) # needs to be computed for lattice link
    jBd = np.zeros((len(rhoBd), len(rhoBd[0]), 27, 3), dtype=float)
    for i in range(0, len(jBd)):
        for j in range(0, len(jBd[0])):
            for l in range(0, 27):
                jBd[i,j,l] = uBdArg / rhoBd[i,j,l]

    #jBd = uBdArg / rhoBd # interpolated at all lattice link directions
    fCollRelevant = selectAtCoordinate(fCollArg, coordinateArg, coordinateValueArg)
    fOut = copy.deepcopy(fArg)
    fRelevant = selectAtCoordinate(fOut, coordinateArg, coordinateValueArg)
    indicesMissing = getMissingDistributionFunctionIndices(fArg, coordinateArg, coordinateValueArg)
    for i in range(0, len(fRelevant)):
        for j in range(0, len(fRelevant[0])):
            for l in indicesMissing:
                oL = getOppositeLatticeDirection(l)
                test = jBd[i,j,l]
                test2 = np.tensordot(ccArg[oL], jBd[i,j,l],axes=1)
                #test2 = ccArg[oL]
                fRelevant[i,j,l] = fCollRelevant[i,j,oL] - 2.0 / csArg ** 2 * wArg[oL] * np.tensordot(ccArg[oL], jBd[i,j,l],axes=1)   # l goes into domain from boundary -> is the correct position to interpolate jBd from, oL streams across boundary
    return fOut




import Core

def computePBd(sigmaBC, fArg, ccArg, cArg, uArg, dxArg, laArg, mueArg, coordinateArg='x', coordinateValueArg=0):
    def applyTractionBoundaryConditions(sigmaBd, sigmaBC):
        sigmaBd = copy.deepcopy(sigmaBd)
        for i in range(0, len(sigmaBd)):
            for j in range(0, len(sigmaBd[i])):
                for l in range(0, len(sigmaBd[i][j])):
                    for ii in range(0, len(sigmaBd[i][j][l])):
                        for jj in range(0, len(sigmaBd[i][j][l][ii])):
                            if (not np.isnan(sigmaBC[ii,jj])):
                                sigmaBd[i,j,l,ii,jj] = sigmaBC[ii,jj]
        return sigmaBd

    def computeSigmaBdWithoutExtrapolation(sigmaArg, ccArg, coordinateArg,coordinateValueArg):
        sigmaAtCoordinate = selectAtCoordinate(sigmaArg,coordinateArg,coordinateValueArg)
        sigmaBd = np.zeros((len(sigmaArg),len(sigmaArg[0]),len(ccArg),3,3), dtype=float)

        for i in range(0, len(sigmaBd)):
            for j in range(0, len(sigmaBd[i])):
                for l in range(0, len(sigmaBd[i][j])):
                    sigmaBd[i,j,l] = sigmaAtCoordinate[i,j]
        return sigmaBd

    def computeDivUBdWithoutExtrapolation(divUArg, ccArg, coordinateArg, coordinateValueArg):
        divUAtCoordinate = selectAtCoordinate(divU, coordinateArg, coordinateValueArg)
        divUBd = np.zeros((len(divUArg), len(divUArg[0]), len(ccArg)), dtype=float)

        for i in range(0, len(divUBd)):
            for j in range(0, len(divUBd[i])):
                for l in range(0, len(divUBd[i][j])):
                    divUBd[i, j, l] = divUAtCoordinate[i, j]
        return divUBd


    P = Core.secondMoment(fArg, ccArg)
    divU = Core.computeDivergenceU(uArg, dxArg)
    sigma = Core.computeSigma(P, divU, laArg, mueArg)
    #sigmaBd = extrapolateTensorToBd(sigma,ccArg,cArg,coordinateArg,coordinateValueArg) #with extrapolation
    sigmaBd = computeSigmaBdWithoutExtrapolation(sigma,ccArg,coordinateArg,coordinateValueArg) # without extrapolation
    #print(sigmaBd.shape)
    sigmaBd = applyTractionBoundaryConditions(sigmaBd, sigmaBC)
    #divUBd = extrapolateScalarToBd(divU, ccArg, cArg, coordinateArg, coordinateValueArg) #with extrapolation
    divUBd = computeDivUBdWithoutExtrapolation(divU,ccArg,coordinateArg,coordinateValueArg) # without extrapolation
    #print(divUBd.shape)
    Pbd = np.zeros(sigmaBd.shape, dtype=float)
    for i in range(0, len(sigmaBd)):
        for j in range(0, len(sigmaBd[i])):
            for l in range(0, len(sigmaBd[i][j])):
                Pbd[i,j,l] = -sigmaBd[i,j,l] + (laArg - mueArg) * divUBd[i,j,l] * np.identity(3, dtype=float)
    return Pbd


def applyNeumannBoundaryConditions(fArg, fCollArg, uArg , rhoArg, csArg, ccArg, cArg, wArg, sigmaBdArg, dxArg, laArg, mueArg, coordinateArg='x', coordinateValueArg=0):
    rhoBd = extrapolateScalarToBd(rhoArg, ccArg, cArg, coordinateArg,
                                  coordinateValueArg)  # needs to be computed for lattice link
    fCollRelevant = selectAtCoordinate(fCollArg, coordinateArg, coordinateValueArg)
    fOut = copy.deepcopy(fArg)
    fRelevant = selectAtCoordinate(fOut, coordinateArg, coordinateValueArg)
    indicesMissing = getMissingDistributionFunctionIndices(fArg, coordinateArg, coordinateValueArg)
    PBd = computePBd(sigmaBdArg,fArg,ccArg,cArg,uArg,dxArg,laArg,mueArg,coordinateArg,coordinateValueArg)
    for i in range(0, len(fRelevant)):
        for j in range(0, len(fRelevant[0])):
            for l in indicesMissing:
                oL = getOppositeLatticeDirection(l)

                tmp1 = PBd[i,j,l] - rhoBd[i,j,l] * csArg ** 2 * np.identity(3,dtype=float)
                tmp2 = np.outer(ccArg[oL], ccArg[oL].transpose()) - csArg ** 2 * np.identity(3, dtype=float)
                fRelevant[i,j,l] = - fCollRelevant[i, j, oL] + 2.0 * wArg[oL] * (rhoBd[i,j,l] + 1.0 / (2.0 * csArg ** 4) * (np.tensordot(tmp1,tmp2, axes=2)))

    return fOut
