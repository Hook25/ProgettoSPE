import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv
import numpy as np

#norm rdc: Array(mean, lower, upper)
norm_rdc = []

#cumul: Array(mean, lower, upper)
cumul = []

#norm_disc: Array(mean, lower, upper)
norm_disc = []

avg_receiver_off = []
recv_duration = []
send_spacing = []

def read_data_from_csv(file_name):
    with open(file_name,'r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        next(data) #skip header
        for row in data:
            norm_rdc.append((float(row[0]), float(row[1]), float(row[2])))
            cumul.append((float(row[3]), float(row[4]), float(row[5]))) 
            norm_disc.append((float(row[6]), float(row[7]), float(row[8]))) 
            avg_receiver_off.append(float(row[9]))
            send_spacing.append(int(row[10]))
            recv_duration.append(int(row[11]))

def plot_3d_cumul_ci():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Send Spacing')
    ax.set_ylabel('Recv Duration')
    ax.set_zlabel('Cumul avg(dr, rdc)')
    ax.scatter(send_spacing, recv_duration, [i[0] for i in cumul])
    for i in np.arange(0, len(cumul)):
        ax.plot([send_spacing[i], send_spacing[i]], [recv_duration[i], recv_duration[i]], [cumul[i][1], cumul[i][2]], marker="_")
    plt.show()

def plot_conf_int(x, y, both_ci = False):
    if both_ci:
        plt.scatter([i[0] for i in x], [j[0] for j in y])
    else:
        plt.scatter(x, [i[0] for i in y])
    #plt.yticks([0.005 + (i*0.01) for i in range(100)])
    for i in range(len(x)):
        if both_ci:
            plt.plot([x[i][1], x[i][2]], [y[i][0], y[i][0]], marker="_")
            plt.plot([x[i][0], x[i][0]], [y[i][1], y[i][2]], marker="_")
        else:
            plt.plot([x[i], x[i]], [y[i][1], y[i][2]], marker="_")
    plt.show()

if __name__ == "__main__":

    read_data_from_csv('metrics_with_conf_int.csv')
    
    idx   = np.argsort([i[0] for i in norm_rdc])
    ordered_norm_rdc = np.array(norm_rdc)[idx]
    ordered_cumul = np.array(cumul)[idx]
    plot_conf_int(ordered_norm_rdc, ordered_cumul, True)

    plot_conf_int([x[0] for x in ordered_norm_rdc], ordered_cumul, False)
    
    ##Normalize Cumul metric
    #norm = np.linalg.norm(cumul)
    #normal_cumul = cumul/norm

    ##Sorting cumul and recv_off
    #idx = np.argsort(recv_off_duration)
    #recv_off_duration = np.array(recv_off_duration)[idx]
    #normal_cumul = np.array(normal_cumul)[idx]

    ##First plot - cumulative metric over receiver off duration
    #plt.plot(recv_off_duration, normal_cumul)
    #plt.title("cumulative metric over receiver off duration")
    #plt.ylabel("Normalized cumulative metrics")
    #plt.xlabel("Receiver off duration")
    #plt.show()

    #Sorting radio duty cycle and disc rate
    mean_norm_disc = [norm_disc[i][0] for i in range(len(norm_disc))]
    #mean_norm_rdc = [norm_rdc[i][0] for i in range(len(norm_rdc))]
    idx   = np.argsort(mean_norm_disc)
    ordered_mean_norm_disc = np.array(mean_norm_disc)[idx]
    ordered_norm_rdc = np.array(norm_rdc)[idx]

    #Second plot - Radio duty cycle over discovery rate
    plt.title("Radio duty cycle over Discovery rate")
    plt.ylabel("Radio Duty Cycle normalized")
    plt.xlabel("Discovery rate normalized")
    plot_conf_int(ordered_mean_norm_disc, ordered_norm_rdc )
    #plt.plot(ordered_mean_norm_disc, ordered_mean_norm_rdc, 'ro')
    #plt.show()

    #xs, ys, zs = [], [], []
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.set_xlabel('Send Spacing')
    #ax.set_ylabel('Recv Duration')
    #ax.set_zlabel('Discovery rate')
    #ax.scatter(send_spacing, recv_off_duration, disc_norm)
    #plt.show()

