# A script that reads the output a polarizer and plots the data over time
import os
import matplotlib.pyplot as plt

# Constants
SingleCollimator = "" # Set to a folder name here if you want to run the script for a single collimator
CollimatorType = "" # Set to AL (for aluminum collimators), ANAL (for anodized aluminum collimators), or SS (for stainless steel collimators) if you want to run the script for a specific collimator type
ValueUsed = 12 # Set to 12 (for DOCP), or 9 (for Azimuth)
TakeAverage = False # Set to True if you want to take the average of the data
JustPlot = False # Set to True if you want to plot data in pre-existing folders
ShiftToZero = True # Set to True if you want to shift the data to zero
ClearData = True # Set to True if you want to clear the data before running the script
SaveData = True # Set to True if you want to save the data to a a text file

# Variables
polarimeterData = []
circularityData = []
circularityMins = []


# read CVS file and returns a 2D array of lines and the comma separated values on each line
def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    dataCSV = [line.split('\t') for line in lines]
    return dataCSV

# make a 2D array of the data in the CSV file
def make_2D_array(dataCSV):
    data = []
    for line in dataCSV:
        data.append([value for value in line])
    return data

# Delete all the data in the current directory
if ClearData:
    for filename in os.listdir('./'):
        if filename.endswith('.csv') and filename.startswith('polarization-'):
            os.remove(filename)
    print("Data cleared")



# Main loop for gathering data and saving it to a file
for folder in os.listdir('./'):
    if folder.startswith('polarization-') and not folder.endswith('.csv'):
        if (SingleCollimator != "" and folder == SingleCollimator) or (CollimatorType != "" and folder.endswith(CollimatorType)) or (CollimatorType == "" and SingleCollimator == ""):
            for filename in os.listdir('./' + folder + '/'):
                if filename.endswith('.csv'):
                    polarimeterData = make_2D_array(read_csv_file('./' + folder + '/' + filename)[9:])

                    for i in range(len(polarimeterData)):
                        for j in range(len(polarimeterData[i])):
                            polarimeterData[i] = polarimeterData[i][j].split(';')

                    graphableCircularity = []

                    for i in range(len(polarimeterData)):
                        graphableCircularity.append(float(polarimeterData[i][ValueUsed]))

                    if ValueUsed == 12:
                        circularityData.append([filename.split('-')[0], max(graphableCircularity)])
                    if ValueUsed == 9:
                        circularityData.append([filename.split('-')[0], (max(graphableCircularity) - min(graphableCircularity))])
        
            # Shift the circularity data so that the lowest circularity is at 0 degrees
            circularityData.sort(key=lambda x: x[1])
            if ShiftToZero:
                circularityData = [[float(circularityData[i][0]) - float(circularityData[0][0]), float(circularityData[i][1])] for i in range(len(circularityData))]

            # print and add to the circularityMins the min value of the circularity data
            print(folder + " min = ", round(circularityData[0][1], 2))
            circularityMins.append([folder.split('-')[1] + '-' + folder.split('-')[2] + ' (' + folder.split('-')[3] + ')', round(circularityData[0][1], 2)])


            # Save the circularity data to a csv file
            with open(folder + '.csv', 'w') as f:
                for i in range(len(circularityData)):
                    f.write(str(circularityData[i][0]) + ',' + str(circularityData[i][1]) + '\n')
            circularityData = []

# Save the circularityMins data to a csv file
if SaveData:
    with open('circularityMins.csv', 'w') as f:
        for i in range(len(circularityMins)):
            f.write(str(circularityMins[i][0]) + ',' + str(circularityMins[i][1]) + '\n')




# plot the circularity with the x-axis being the angle from the file name
fig, ax = plt.subplots()
if ValueUsed == 12:
    ax.set_title('DOCP vs Angle')
    ax.set_xlabel('Angle (°)')
    ax.set_ylabel('DOCP (%)')
if ValueUsed == 9:
    ax.set_title('Azimuth vs Angle')
    ax.set_xlabel('Angle (°)')
    ax.set_ylabel('Azimuth (°)')
ax.grid()

# read the data from the csv files
for filename in os.listdir('./'):
    if filename.endswith('.csv') and filename.startswith('polarization-'):
        with open(filename, 'r') as f:
            lines = f.readlines()
            x = []
            y = []
            for line in lines:
                line = line.strip().split(',')
                x.append(float(line[0]))
                y.append(float(line[1]))
            # plot the data
            ax.scatter(x, y, label=filename.split('-')[2] + " " + filename.split('-')[3].replace('.csv', ''))

# Take the average of the data
if TakeAverage:
    # read the data from the csv files and take the average
    averageData = []
    for filename in os.listdir('./'):
        if filename.endswith('.csv') and filename.startswith('polarization-'):
            with open(filename, 'r') as f:
                lines = f.readlines()
                x = []
                y = []
                for line in lines:
                    line = line.strip().split(',')
                    x.append(float(line[0]))
                    y.append(float(line[1]))
                # Average the data
                # loop through the average data array and if the x value is already in the array append the y value to the x value array
                # if the x value is not in the array append the x value and y value to the array
                for i in range(len(x)):
                    for j in range(len(averageData)):
                        if averageData[j][0] == x[i]:
                            averageData[j][1].append(y[i])
                            break
                    else:
                        averageData.append([x[i], [y[i]]])



    # loop through the average data array and take the average of the y values
    for i in range(len(averageData)):
        sum = 0
        for j in range(len(averageData[i][1])):
            sum += averageData[i][1][j]
        averageData[i][1] = sum / len(averageData[i][1])

    # Save the average data to a csv file
    with open('polarization-average.csv', 'w') as f:
        for i in range(len(averageData)):
            f.write(str(averageData[i][0]) + ',' + str(averageData[i][1]) + '\n')

    #plot the average data
    x = []
    y = []
    for i in range(len(averageData)):
        x.append(averageData[i][0])
        y.append(averageData[i][1])
    ax.scatter(x, y, label='Average Data')

fig.subplots_adjust(right=0.80)  # Make room for the legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()








