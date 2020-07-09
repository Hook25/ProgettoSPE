import matplotlib.pyplot as plt
import csv

norm_rdc = []
cumul = []
etq = []
disc_norm = []

if __name__ == "__main__":
    with open('data.csv','r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        for row in data:
            norm_rdc.append(float(row[0]))
            cumul.append(float(row[1]))
            etq.append((int(row[2]), int(row[3])))
            disc_norm.append(float(row[4]))

    x_axis = [i for i in range(len(norm_rdc))]
    plt.plot(x_axis, norm_rdc, label = "norm rdc")
    plt.plot(x_axis, cumul, label = "cumul")
    plt.plot(x_axis, disc_norm, label = "disc norm")
    plt.legend()
    plt.title("Plot of simulation results")
    plt.show()