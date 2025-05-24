import bpy
import bmesh 
import math
import numpy as np
import time
import bpy.app.handlers


nx = 22
L = 10

x = np.linspace(-L/2, L/2, nx)
y = x
z = x
X, Y, Z = np.meshgrid(x, y, z)

dx = x[2]-x[1]


class Tetra():

    def object(self, scene, name):
        obj = bpy.data.objects.new("Tetra", self.mesh_from_pydata())
        obj.name = name
        bpy.context.collection.objects.link(obj)
        return obj

    def mesh_from_pydata(self):
        me = bpy.data.meshes.new("some_name")
        me.from_pydata(self.Verts, [], self.Faces)
        return me

    def __init__(self, verts):
        self.Verts = verts
        faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)]
        
        self.Faces = faces

        pass


# test drive
context = bpy.context
scene = context.scene
start = time.time()
for k in range(0, nx):
    for i in range(0, nx):
        for j in range(0, nx):
            tet = Tetra([(0+i*dx, j*dx+0, k*dx+0), (1*dx+i*dx, j*dx+0, k*dx+0), (1*dx+i*dx, j*dx+1*dx, k*dx+0), (0+i*dx, j*dx+1*dx, k*dx+0),
                (0+i*dx, j*dx+0,  k*dx+1*dx), (1*dx+i*dx, j*dx+0, k*dx+1*dx), (1*dx+i*dx, j*dx+1*dx, k*dx+1*dx), (0+i*dx, j*dx+1*dx, k*dx+1*dx)])
            obj = tet.object(scene, ""+str(i)+","+str(j)+","+str(k)+"")

end = time.time()
print("Done in %d seconds" % (end - start) )
