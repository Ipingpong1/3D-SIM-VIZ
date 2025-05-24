import bpy
import bmesh 
import math
import numpy as np
import time
import bpy.app.handlers
cones = []

def reset_scene():
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in bpy.context.scene.objects:
        o.select_set(True)
        bpy.ops.object.delete()
        

def add_plane(name, resolution, size):
    # Create a new mesh and object to put the data into
    bpy.ops.mesh.primitive_plane_add(location=(0,0,0), size=L)
    plane_object = bpy.context.active_object
    plane_object.name = name
    
    # Bmesh is a method of editing the mesh data within an object
    bm = bmesh.new()
    bm.from_mesh(plane_object.data) 
    
    
    bmesh.ops.subdivide_edges(bm,
                          edges=bm.edges,
                          cuts=resolution-1,
                          use_grid_fill=True,
                          )

    # Write back to the mesh

    bm.to_mesh(plane_object.data)
    plane_object.data.update() 
    
    cones.append((plane_object, bm))
    
    return bm

def add_cube(name, loc, L):
    # Create a new mesh and object to put the data into
    bpy.ops.mesh.primitive_cube_add(location=loc, size=L)
    cube_object = bpy.context.active_object
    cube_object.name = name
    
    # Bmesh is a method of editing the mesh data within an object
    bm = bmesh.new()
    bm.from_mesh(cube_object.data) 

    # Write back to the mesh
    bm.to_mesh(cube_object.data)
    cube_object.data.update() 
    
    cones.append((cube_object, bm))
    
    return bm   

def apply_transforms():
    for cone in cones:
        bm = cone[1]
        cone_object = cone[0]
        bm.to_mesh(cone_object.data)   
        # bm.free()
 
def apply_wave_at_time(plane_bm, u, dx, t, V):
    for v in plane_bm.verts:
         
        x = int( ( v.co[0] + L/2 ) / dx)
        y = int( ( v.co[1] + L/2 )  / dx)
        
        v.co[2] = u[t,x,y]
        
def create_viz_cube(nx, dx):
    for k in range(0, nx):
        for i in range(0, nx):
            for j in range(0, nx):
                add_cube(""+str(i)+","+str(j)+","+str(k)+"", (i*dx, j*dx, k*dx), dx)


# ----------------------------------------#
#reset_scene() # COMMENT IN WHEN CREATING CUBES
# -----------------------------------------
# ---\ COMMENT OUT IF CREATING CUBES /--- #
for obj in bpy.context.scene.objects:
    bm = 0
    cones.append((obj, bm))
# ------^ ERASE IF CREATING CUBES ^------ #

plot_every = 20

dt =.0005
nt = 10000

nx = 22
L = 10

x = np.linspace(-L/2, L/2, nx)
y = x
z = x
X, Y, Z = np.meshgrid(x, y, z)

dx = x[2]-x[1]

u0 = np.zeros([len(x), len(y), len(z)], dtype=np.complex64)
V = np.zeros([len(x), len(y), len(z)])
out = np.zeros([nt//plot_every, len(x), len(y), len(z)])

u0_x_offset = 0
u0_y_offset = 0
u0_z_offset = 0
s = 2
for k in range(0, len(z)):
    for i in range(0, len(x)):
        for j in range(0, len(y)):
            u0[i, j, k] = 2*np.exp(-4 * (
                (x[i]-u0_x_offset)**2 +\
                (y[j]-u0_y_offset)**2 +\
                s*(z[k]-u0_z_offset)**2   ) /L ) * np.exp(-15j*(y[j]-u0_y_offset)) # * np.exp(11j*(x[i]-u0_x_offset))
u = u0

# ----\ COMMENT IN IF CREATING CUBES /---- #

# create_viz_cube(nx, dx)

#for obj in cones:
#    #get name of object
#    name = obj[0].name
#    co = name.split(",")
#    # check if object has material same as object name
#    # if there is then continue to next object
#    if name in obj[0].data.materials: 
#        continue
#    
#    #create new material with name of object
#    new_mat = bpy.data.materials.new(name)
#    color = abs(u0[int(co[0]), int(co[1]), int(co[2])])
#    new_mat.diffuse_color = (color/2, color/2, color/2, (color/2))
#    new_mat.blend_method = 'BLEND'
#    
#    #add new material to object
#    obj[0].data.materials.append(new_mat)
#    #added material will be last in material slots
#    #so make last slot active
#    obj[0].active_material_index = len(obj[0].data.materials) - 1
     
# ----^ COMMENT IN IF CREATING CUBES ^---- #
    

k = 2*(x/dx)*np.pi/L
Kx, Ky, Kz = np.meshgrid(k, k, k)
for t in range(0, nt):
    u[0, :, :]= 0
    u[-1, :, :] = 0
    u[:, 0, :]= 0
    u[:, -1, :] = 0
    
    V[0, :, :]= 100000 
    V[-1, :, :] = 100000
    V[:, 0, :]= 100000
    V[:, -1, :] = 100000
    
    u = np.exp(dt*1j*(X**2+Y**2+Z**2)*V)*u; # Solve non-constant part of 2D-LSE
    c = np.fft.fftshift(np.fft.fftn(u)); # Take 2D-Fourier transform
    c = np.exp(dt/2*1j*(-Kx**2-Ky**2-Kz**2))*c; # Advance in Fourier space
    u = np.fft.ifftn(np.fft.fftshift(c)); # R eturn to physical space
     
    if(t%plot_every == 0):
        out[t//plot_every] = u
        
run = True 

def my_handler(scene):
    if(scene.frame_current%2==0 and run == True):
        for obj in cones:
            name = obj[0].name
            co = name.split(",")
            color = np.abs(out[scene.frame_current, int(co[0]), int(co[1]), int(co[2])])**2
            if color < .001:
                # obj[0].hide_set(True)
                obj[0].data.materials[-1].diffuse_color = (color, color, color, color**2)
            else:
                # obj[0].hide_set(False)
                obj[0].data.materials[-1].diffuse_color = (1-4*color, -1+6*color, 1, color)
            
bpy.app.handlers.frame_change_pre.append(my_handler)
