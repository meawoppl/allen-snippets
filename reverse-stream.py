import numpy as np
import struct, zipfile, os

from pylab import *


def readStream(zf):
    # Open the zipfile
    zf = zipfile.ZipFile(zf)

    # Extract (in ram) the streamlines file
    fp = zf.open("streamlines.sl")

    # Ignore the first six bytes. . .  No idea what they are
    unknown = struct.unpack("HHH", fp.read(6)) 

    # This is the number of segments that are listes
    nSegments = struct.unpack("I", fp.read(4))[0]
    
    segments = []
    # For each segment
    for i in xrange(nSegments):
        # Number of points in this segment
        nPoints = struct.unpack("H", fp.read(2))[0]

        # Read the segment data, 5 floats x, y, z, intensity, density, shape them properly
        pts = np.frombuffer(fp.read(4*5*nPoints), dtype=np.float32).reshape((-1,5)).T

        # Store the segment for later return
        segments.append(pts)

    # Return the Segments
    return segments


def loadAllSegments():
    segmentList = []
    for n, f in enumerate(os.listdir("rawdata")):
        print f
        path = os.path.join("rawdata", f)        
        segmentList += readStream(path)
        print "%i segments loaded" % len(segmentList)

    return segmentList
    


def testStream():
    for n, f in enumerate(os.listdir("rawdata")):
        print f
        path = os.path.join("rawdata", f)
        failureIDs = []

        streamSegments = readStream(path)

        for stream in streamSegments:
            xs, ys, zs, i1, i2 = stream

            figure(1)
            plot(xs, ys, "b", alpha=0.3)

            figure(2)
            plot(ys, zs, "b", alpha=0.3)

            figure(3)
            plot(xs, zs, "b", alpha=0.3)

        if n > 4:
            break

    print failureIDs


def computeDistances(segmentList):
    distances = []
    for segment in loadAllSegments():
        xs, ys, zs, ii, ij = segment

        xd = diff(xs)
        yd = diff(ys)
        zd = diff(zs)

        dist = sqrt( xd**2 + yd**2 + zd**2 )
        distances.append(dist)

    d = concatenate(distances)
    print d.shape
    hist(d, bins=200)
    print d.min(), d.max()
    show()


# def pointWise


if __name__ == "__main__":
    allSegs = loadAllSegments()
    computeDistances(allSegs)

    

    
        
