from turtle import *
import math, time, gzip, base64

W, H = 500, 500
FOV = 90
SIZE = 0.1
MODEL = "" # Your custom .obj model path
DYNAMIC = False

if not DYNAMIC:
	tracer(0, 0)
	
def load_model(data):
	vertices = []
	polygons = []
	for line in data.split("\n"):
		if line[:2] == "v ":
			vert = []
			for coord in line[2:].split(" "):
				vert.append(float(coord))
			vertices.append(vert)
		elif line[:2] == "f ":
			polygon = []
			for face in line[2:].split(" "):
				ind = int(face.split("/")[0])-1
				polygon.append(vertices[ind])
			polygons.append(polygon)
	return polygons
	
def load_from_file(path):
	with open(path, "r") as file:
		return load_model(file.read())

def mat_by_mat(m1, m2):
	# Multiply 2 matrices together
	result = [[0, 0, 0, 0],
		  		[0, 0, 0, 0],
		  		[0, 0, 0, 0],
		  		[0, 0, 0, 0]]

	for i in range(len(m1)):
		for j in range(len(m2[0])):
			for k in range(len(m2)):
				result[i][j] += m1[i][k] * m2[k][j]
	
	return result
	 
def vec_by_mat(v, m):
	# Vector by matrix multiplication
	result = [0, 0, 0, 0]

	for i in range(len(m)):
		for j in range(len(v)):
			result[i] += m[i][j] * v[j]
			
	return result
	
def rot_mat(x, y, z):
	# Convert degrees to radians
	x = math.radians(x)
	y = math.radians(y)
	z = math.radians(z)

	# Define X-axis rotation matrix
	rx = [
		[1, 0, 0, 0],
		[0, math.cos(x), -math.sin(x), 0],
		[0, math.sin(x), math.cos(x), 0],
		[0, 0, 0, 1]
	]

	# Define Y-axis rotation matrix
	ry = [
		[math.cos(y), 0, math.sin(y), 0],
		[0, 1, 0, 0],
		[-math.sin(y), 0, math.cos(y), 0],
		[0, 0, 0, 1]
	]

	# Define Z-axis rotation matrix
	rz = [
		[math.cos(z), -math.sin(z), 0, 0],
		[math.sin(z), math.cos(z), 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]
	]
	
	rxy = mat_by_mat(rx, ry)
	rxyz = mat_by_mat(rxy, rz)
	return rxyz

def transform(p, proj, size, rot):
	m = mat_by_mat(proj, rot)
	m = mat_by_mat(m, size)
	p = vec_by_mat(p, m)
	return [
		p[0]*W, p[1]*H, p[2]
	]

CUBE = "H4sIABsC+mQC/+NSVnAuTUrVy0/K4lJWCEstKslMTi3mKlPQNdQzQBBAAWx8JK4uNj5MEFk7qm40zSAu0B2BpYkpCm6JIJekKRgqGCkYK5gAWaYKZgrmChZgMRDbCMgyAosZA1nGIDmwOhMgbapgyAUAzDrMTN0AAAA="

if not MODEL:
	cube_model = gzip.decompress(
		base64.b64decode(CUBE)
	).decode("UTF-8")
	VERTICES = load_model(cube_model)
else:
	VERTICES = load_from_file(MODEL)

aspect_ratio = H/W
fov  = math.pi / 3.0
zfar = 1024
znear = 0.1
zdiff = zfar-znear
f = 1/math.tan(fov/2*2/math.pi)

projection = [
	[f*aspect_ratio, 0, 0, 0],
	[0, f, 0, 0],
	[0, 0, (zfar+znear)/zdiff, 1],
	[0, 0, -(2*zfar*znear)/zdiff, 0]
]

size = [
	[SIZE, 0, 0, 0],
	[0, SIZE, 0, 0],
	[0, 0, SIZE, 0],
	[0, 0, 0, SIZE]
]

rot = rot_mat(45, 22, 0)

speed(10)
width(2)
Screen().bgcolor("black")
pencolor("#00FF00")
fillcolor("black")

def depth_filter(vertices):
	polygons = []
	for vert in vertices:
		v = []
		for ind, point in enumerate(vert):
			p = transform(point, projection, size, rot)
			v.append(p)
		polygons.append(v)
	polygons = sorted(polygons, key=lambda x: max([i[2] for i in x])/len(x))
	return polygons

def draw():
	polygons = depth_filter(VERTICES)
	for inn, vert in enumerate(polygons):
		startpoint = vert[0]
		up()
		setpos(*startpoint[:2])
		down()
		begin_fill()
		for ind, point in enumerate(vert[1:]):
			goto(*point[:2])
		goto(*startpoint[:2])
		end_fill()
			
ry = 120
factor = 2

while 1:
	ry = (ry+factor)%360
	rot = rot_mat(45, ry, 0)
	clear()
	draw()
	if not DYNAMIC:
		update()
	time.sleep(0.015)
