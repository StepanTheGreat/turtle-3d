from turtle import *
import numpy as np
import time, gzip, base64

W, H = 500, 500
FOV = 90
SIZE = 0.1
MODEL = "pigeon.obj" # Your custom .obj model path
WIDTH = 1
SPEED = 0
DYNAMIC = False

CAM_DIR = [0, 0, -1]
CAM_POS = [0, 0, -5]
VERTICES = None
FACES = None

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
			vert.append(0)
			vertices.append(vert)
		elif line[:2] == "f ":
			polygon = []
			for face in line[2:].split(" "):
				ind = int(face.split("/")[0])-1
				polygon.append(vertices[ind])
			polygons.append(polygon)

	polygons = np.array(polygons, dtype=object)
	return polygons
	
def load_from_file(path):
	with open(path, "r") as file:
		return load_model(file.read())
	
def rot_mat(x, y, z):
	# Convert degrees to radians
	x = np.radians(x)
	y = np.radians(y)
	z = np.radians(z)

	# Define X-axis rotation matrix
	rx = np.array([
		[1, 0, 0, 0],
		[0, np.cos(x), -np.sin(x), 0],
		[0, np.sin(x), np.cos(x), 0],
		[0, 0, 0, 1]
	], dtype=np.float32)

	# Define Y-axis rotation matrix
	ry = np.array([
		[np.cos(y), 0, np.sin(y), 0],
		[0, 1, 0, 0],
		[-np.sin(y), 0, np.cos(y), 0],
		[0, 0, 0, 1]
	], dtype=np.float32)

	# Define Z-axis rotation matrix
	rz = np.array([
		[np.cos(z), -np.sin(z), 0, 0],
		[np.sin(z), np.cos(z), 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]
	], dtype=np.float32)
	
	return rx @ ry @ rz

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def transform(p, proj, view, size, rot):
	# p = p @ rot @ size @ proj
	p = proj @ view @ rot @ size @ p
	return p

def transform_screen(p, proj, view, size, rot):
	# p = p @ rot @ size @ proj
	p = transform(p, proj, view, size, rot)
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
fov  = np.pi / 3.0
zfar = 1024
znear = 0.1
zdiff = zfar-znear
f = 1/np.tan(fov/2*2/np.pi)

projection = np.array([
	[f*aspect_ratio, 0, 0, 0],
	[0, f, 0, 0],
	[0, 0, (zfar+znear)/zdiff, 1],
	[0, 0, -(2*zfar*znear)/zdiff, 0]
], dtype=np.float32)

v_target = np.array(CAM_DIR, dtype=np.float32)
v_pos = np.array(CAM_POS, dtype=np.float32)
v_up = np.array([0, 1, 0], dtype=np.float32)

v_forward = normalize(v_target - v_pos)
v_right = normalize(np.cross(v_up, v_forward))
v_new_up = np.cross(v_forward, v_right)

view = np.array([
	[v_right[0], v_new_up[0], -v_forward[0], 0],
	[v_right[1], v_new_up[1], -v_forward[1], 0],
	[v_right[2], v_new_up[2], -v_forward[2], 0],
	[-np.dot(v_right, v_pos), -np.dot(v_new_up, v_pos), np.dot(v_forward, v_pos), 1]
], dtype=np.float32)

size = np.array([
	[SIZE, 0, 0, 0],
	[0, SIZE, 0, 0],
	[0, 0, SIZE, 0],
	[0, 0, 0, SIZE]
], dtype=np.float32)

rot = rot_mat(45, 22, 0)

speed(SPEED)
width(WIDTH)
Screen().bgcolor("black")
pencolor("#00FF00")
fillcolor("black")

def depth_filter(vertices):
	polygons = []

	for ind, vert in enumerate(vertices):
		v = [transform_screen(point, projection, view, size, rot) for point in vert]

		v1 = np.array([v[0][0], v[0][1], v[0][2]])
		v2 = np.array([v[1][0], v[1][1], v[1][2]])
		v3 = np.array([v[2][0], v[2][1], v[2][2]])

		edge1 = v2 - v1
		edge2 = v3 - v1

		face = np.cross(edge1, edge2)
		face = face / np.linalg.norm(face)

		result = np.dot(face, np.array(CAM_DIR, dtype=np.float32))
		if result >= 0:
			polygons.append(v)
	# polygons = sorted(polygons, key=lambda x: max([i[2] for i in x])/len(x))
	return polygons

def draw():
	polygons = depth_filter(VERTICES)
	for vert in polygons:
		startpoint = vert[0]
		up()
		setpos(*startpoint[:2])
		down()
		# begin_fill()
		for point in vert[1:]:
			goto(*point[:2])
		goto(*startpoint[:2])
		# end_fill()

global rotx, roty, factor
rotx = 0
roty = 0
factor = 2

def key_up():
	global rotx 
	rotx -= 5

def key_down():
	global rotx
	rotx += 5

def key_left():
	global factor
	factor = max(factor-1, 0)

def key_right():
	global factor
	factor = min(factor+1, 15)

listen()
onkey(key_up, "Up")
onkey(key_down, "Down")
onkey(key_left, "Left")
onkey(key_right, "Right")

while 1:
	roty += factor
	roty = 0 if roty >= 360 else roty
	rot = rot_mat(rotx, roty, 0)
	clear()
	draw()
	if not DYNAMIC:
		update()
	# time.sleep(0.015)
	# time.sleep(2)

mainloop()
