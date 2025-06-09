import scipy
from scipy import linalg
import numpy as np
import matplotlib.pyplot as plt
import os

# Constants
Collimator = "330241-35"  # Set to the collimator you want to use


data = []

# open the file and read the data and returns a 2D array of lines and the comma separated values on each line
def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    #dataCSV = [line.split('\t') for line in lines]
    dataCSV = [line.split(';') for line in lines]
    return dataCSV

# get a data points from the cvs files
def get_centroid_points(rowX, columnX, rowY, columnY):
    #files = [f for f in os.listdir("330241-08/AxisTesting/") if f.endswith('.txt')]
    files = [f for f in os.listdir(f"{Collimator}/AxisTesting/") if f.endswith('.csv')]
    #print(files)
    data_points = []
    for file in files:
        #dataCSV = read_csv_file("330241-08/AxisTesting/" + file)
        dataCSV = read_csv_file(f"{Collimator}/AxisTesting/" + file)
        #print(dataCSV)
        #get the value from the row and column
        x = float(dataCSV[rowX][columnX])
        y = float(dataCSV[rowY][columnY])
        data_points.append((x, y))
    return data_points



# plot the data points on a scatter plot
def plot_data_points(data_points):
    x_values = [point[0] for point in data_points]
    y_values = [point[1] for point in data_points]
    plt.scatter(x_values, y_values)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Centroid Points')
    plt.grid()
    plt.show()



data = get_centroid_points(18, 13, 18, 14)



# fit a circle to the data points
x = np.array([point[0] for point in data])
y = np.array([point[1] for point in data])


# coordinates of the barycenter
x_m = np.mean(x)
y_m = np.mean(y)

# calculation of the reduced coordinates
u = x - x_m
v = y - y_m

# linear system defining the center in reduced coordinates (uc, vc):
#    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
#    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
Suv  = sum(u*v)
Suu  = sum(u**2)
Svv  = sum(v**2)
Suuv = sum(u**2 * v)
Suvv = sum(u * v**2)
Suuu = sum(u**3)
Svvv = sum(v**3)

# Solving the linear system
A = np.array([ [ Suu, Suv ], [Suv, Svv]])
B = np.array([ Suuu + Suvv, Svvv + Suuv ])/2.0
uc, vc = linalg.solve(A, B)

xc_1 = x_m + uc
yc_1 = y_m + vc

# Calculation of all distances from the center (xc_1, yc_1)
Ri_1      = np.sqrt((x-xc_1)**2 + (y-yc_1)**2)
R_1       = np.mean(Ri_1)
residu_1  = sum((Ri_1-R_1)**2)
residu2_1 = sum((Ri_1**2-R_1**2)**2)

# Decorator to count functions calls
import functools
def countcalls(fn):
    "decorator function count function calls "

    @functools.wraps(fn)
    def wrapped(*args):
        wrapped.ncalls +=1
        return fn(*args)

    wrapped.ncalls = 0
    return wrapped


from scipy      import optimize


def calc_R(xc, yc):
    """ calculate the distance of each 2D points from the center (xc, yc) """
    return np.sqrt((x-xc)**2 + (y-yc)**2)

@countcalls
def f_2(c):
    """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
    Ri = calc_R(*c)
    return Ri - Ri.mean()

center_estimate = x_m, y_m
center_2, ier = optimize.leastsq(f_2, center_estimate)

xc_2, yc_2 = center_2
Ri_2       = calc_R(xc_2, yc_2)
R_2        = Ri_2.mean()
residu_2   = sum((Ri_2 - R_2)**2)
residu2_2  = sum((Ri_2**2-R_2**2)**2)
ncalls_2   = f_2.ncalls



# print("Circle fit by leastsq")
# print("  center:    (x, y) = (%.3f, %.3f)" % (xc_2, yc_2))
# print("  radius:    R = %.3f" % R_2)
# print("  residu:    sum(Ri-R)^2 = %.3f" % residu_2)
# print("  residu2:   sum(Ri^2-R^2)^2 = %.3f" % residu2_2)
# print("  function calls: %d" % ncalls_2)

# Calculate the angle required to make that circle
distanceAdj = 100 + 20.7
distanceAdj = distanceAdj * 1000
distanceOpp = R_2

angleRad = np.arctan(distanceOpp/distanceAdj)
angleMrad = angleRad * 1000
angleDeg = angleRad * 180 / np.pi
print("Angle (mrad) for {}: ".format(Collimator), angleMrad)
print("Angle (deg) for {}: ".format(Collimator), angleDeg)

# plot the data points and the fitted circle
fig, ax = plt.subplots()
ax.set_title('Circle Fit')
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_aspect('equal')
ax.grid()
ax.scatter(x, y, label='Data Points', color='blue')
ax.scatter(xc_2, yc_2, label='Fitted Circle Center', color='red')
circle = plt.Circle((xc_2, yc_2), R_2, color='green', fill=False, label='Fitted Circle')
ax.add_artist(circle)
ax.legend()
ax.legend(loc='upper right')
plt.xlim(min(x)-50, max(x)+50)
plt.ylim(min(y)-50, max(y)+50)
plt.show()