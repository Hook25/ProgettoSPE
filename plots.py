import matplotlib.pyplot as plt
import csv
import numpy as np

norm_rdc = []
cumul = []
etq = []
disc_norm = []
recv_off_duration = []
send_spacing = []

if __name__ == "__main__":
    with open('data.csv','r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        for row in data:
            norm_rdc.append(float(row[0]))
            cumul.append(float(row[1]))
            etq.append((int(row[2]), int(row[3])))
            recv_off_duration.append(int(row[3]))
            send_spacing.append(int(row[2]))
            disc_norm.append(float(row[4]))

    #Normalize Cumul metric
    norm = np.linalg.norm(cumul)
    normal_cumul = cumul/norm

    #Sorting cumul and recv_off
    idx = np.argsort(recv_off_duration)
    recv_off_duration = np.array(recv_off_duration)[idx]
    normal_cumul = np.array(normal_cumul)[idx]

    #First plot - cumulative metric over receiver off duration
    plt.plot(recv_off_duration, normal_cumul)
    plt.title("cumulative metric over receiver off duration")
    plt.ylabel("Normalized cumulative metrics")
    plt.xlabel("Receiver off duration")
    plt.show()

    #Sorting radio duty cycle and disc rate
    idx   = np.argsort(disc_norm)
    disc_norm = np.array(disc_norm)[idx]
    norm_rdc = np.array(norm_rdc)[idx]

    #Second plot - Radio duty cycle over discovery rate
    plt.title("Radio duty cycle over Discovery rate")
    plt.ylabel("Radio Duty Cycle normalized")
    plt.xlabel("Discovery rate normalized")
    plt.plot(disc_norm, norm_rdc)
    plt.show()

    xs, ys, zs = [], [], []
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Send Spacing')
    ax.set_ylabel('Recv Duration')
    ax.set_zlabel('Discovery rate')
    ax.scatter(send_spacing, recv_off_duration, disc_norm)
    plt.show()

