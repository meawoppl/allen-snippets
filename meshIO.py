#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, csg
import struct
import numpy as np

def loadABA(filename):
    fp = open(filename,"rb")

    # Read the vertex count
    vCount = struct.unpack("I", fp.read(4))[0]

    # The size of the data to read is 6 float32's (3 normal, 3 coordinates) per vertex 
    vertexDataSize = vCount * 4 * (3+3)

    # Use numpy to scrape the raw array into memory
    rawArray = np.fromstring(fp.read(vertexDataSize), dtype=np.float32)

    # Compute views of normals
    xn = rawArray[0::6]
    yn = rawArray[1::6]
    zn = rawArray[2::6]
    
    # Compute views of the coordinates
    xs = rawArray[3::6]
    ys = rawArray[4::6]
    zs = rawArray[5::6]

    # Accrue the polygons in a list
    polygons = []

    # Read the polygon count
    polyCount = struct.unpack("I", fp.read(4))[0]
    for polygonIndex in xrange(polyCount):
        # Get the point count in this polygon
        pointCount = struct.unpack("H", fp.read(2))[0]

        # Collect the vertex indices
        vertices = []
        for pointIndex in xrange(pointCount):
            index = struct.unpack("I", fp.read(4))[0]
            vertices.append(csg.Vertex.fromXYZ(xs[index], ys[index], zs[index]))
        
        # Dereference the indices into points
        for indx in xrange(pointCount-2):
            v1 = vertices[indx + 0]
            v2 = vertices[indx + 1]
            v3 = vertices[indx + 2]

            # Triange strip winding angle hoot-nanny
            even = (indx % 2 == 0)
            if even:
                polygons.append(csg.Polygon([v1, v2, v3]))
            else:
                polygons.append(csg.Polygon([v2, v1, v3]))

    return csg.PolygonMesh(polygons)



class UniqueVertexCollector(object):
    def __init__(self):
        # Bidirectional dictionary.  
        # ndarray -> vertexID and vice versa
        self.vertexIndex = {}
        self.indexVertex = {}

        # Internal counter for vertex insertion
        self.indexCount = 0

    def addVertex(self, vertex):
        # ndarrays are not hashable, but their string rep is
        stringRep = vertex.tostring()
        if stringRep in self.vertexIndex:
            return
        
        # The bidirectional dict (2 dicts)
        self.vertexIndex[stringRep] = self.indexCount
        self.indexVertex[self.indexCount] = vertex
        self.indexCount += 1

        return self.indexCount - 1

    def getVertex(self, index):
        return self.indexVertex[index]

    def getIndex(self, vertex):
        return self.vertexIndex[vertex.tostring()]

    def __len__(self):
        return len(self.vertexIndex)

    @staticmethod
    def fromPolygonList(triangleList):
        vc = UniqueVertexCollector()
        for tri in triangleList:
            for vertex in tri.vertices:
                vc.addVertex(vertex)
        return vc


def writeOBJ(mesh, filename):
    m = open("colors.mtl", "w")

    # m.write(""
    # Figure out what all colors we are using
    def tupleToColorString(colorTuple):
        return "color" + "_".join(["%0.2f" % c for c in colorTuple])

    colorsWritten = set()
    for polygon in mesh.polygons:
        polygonColor = polygon.shared["color"]
        if polygonColor in colorsWritten:
            continue
        m.write("newmtl " + tupleToColorString(polygonColor) + "\n")
        m.write("Ka %f %f %f\n" % polygonColor)
        m.write("Kd %f %f %f\n" % polygonColor)
        m.write("illum 2\n")
        m.write("\n")
        colorsWritten.add(polygonColor)
    
    m.close()

    f = open(filename, "w")
    f.write("# Created by pyCSG\n")
    f.write("mtllib colors.mtl\n")
    
    # Get the unique vertices
    vc = UniqueVertexCollector.fromPolygonList(mesh.polygons)

    # Write the vertices (in order!)
    for indx in xrange(len(vc)):
        f.write("v %f %f %f\n" % tuple(vc.getVertex(indx)))

    # Write the face indices
    for polygon in mesh.polygons:
        # Tell it to use the right color
        f.write("usemtl " + tupleToColorString(polygon.shared["color"]) + "\n")
        # .obj is 1 based hence the +1
        vIndices = [str(vc.getIndex(v) + 1) for v in polygon.vertices]
        f.write( "f " + " ".join(vIndices) + "\n" )

    f.close()
        
# TODO!
def writeSTL(mesh, filename):
    pass

def writePLY(mesh, filename):
    # Go through, and determine the unique vertices
    vc = UniqueVertexCollector.fromPolygonList(mesh.polygons)

    vertexCount = len(vc)
    faceCount   = len(mesh.polygons)

    # Open the file and stary writing the header
    f = open(filename, "w")
    f.write("ply\n")
    f.write("format ascii 1.0\n")
    f.write("element vertex %i\n" % vertexCount )

    for axName in ["x", "y", "z"]:
        f.write("property float32 %s\n" % axName)

    f.write("element face %i\n" % faceCount )
    f.write("property list uint8 int32 vertex_index\n")
    for clr in ["red", "blue", "green"]:
        f.write("property uchar %s\n" % clr)

    f.write("end_header\n")

    # Write the vertices
    for indx in xrange(len(vc)):
        vtx = vc.getVertex(indx)
        f.write( "%f %f %f\n" % tuple( vtx ) )
    
    # Write the indices
    for poly in mesh.polygons:
        nVert = len(poly.vertices)
        indxs = [vc.getIndex(vert.pos) for vert in poly.vertices]
        count_nIndexes = str(nVert) + " " + " ".join([str(i) for i in indxs])
        # Cast the 0-1 color into uint8 land, and stringify
        colors = "%i %i %i" % tuple([int(clr*255) for clr in poly.shared.get("color", (0.5, 0.5, 0.5) )])
        f.write(count_nIndexes + " " + colors + "\n")


    print "Wrote {0} vertices, and {1} faces to file '{2}'".format(vertexCount, faceCount, filename)
    f.close()
