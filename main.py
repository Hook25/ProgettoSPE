from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np
from multiprocessing import Pool
from collections import defaultdict
from matplotlib import pyplot as plt
import scipy.stats as st
from math import sqrt
from math import ceil, floor

def build_network(size):
  return [Node(i, (i,i)) for i in range(size)]

def inc_1(prop):
  return [x + 1 for x in prop]

def dec_1(prop):
  return [x-1 for x in prop]

def simulate(size_params):
  size, params = size_params
  nodes = build_network(size)
  params_manager = SimulParamsManager(params)
  e = Environment(nodes, params_manager)
  e.simulate()
  return e

def avg(x): return sum(x) / len(x)

def calc_avg_disc(env):
  disc = [len(node.discovered) for node in env.nodes]
  return avg(disc)

def calc_norm_radio_dc(env):
  time_to_send = 0.01
  recv_duration = env.get_param("recv_duration")
  off_duration = env.get_param("off_duration")
  send_duration = env.get_param("send_duration")
  send_spacing = env.get_param("send_spacing")
  tot_cycle_duration = recv_duration + off_duration + send_duration
  tot_on_send = time_to_send * int(send_duration / send_spacing)
  return (tot_on_send + recv_duration) / tot_cycle_duration

def send_spacing_domain(params, domain):
  return [(
    size, 
    param_l + [
      Param("send_spacing", identity, (d_x,))
    ]) 
    for d_x in range(*domain) 
    for size, param_l in params
  ]  

def recv_off_domain(params, domain):
  TOT_RECV_TIME = 600
  return [(
    size, 
    param_l + [
      Param("recv_duration", identity, (TOT_RECV_TIME - x_dom, )),
      Param("off_duration", identity, (TOT_RECV_TIME - (TOT_RECV_TIME - x_dom), ))
    ])
    for x_dom in range(*domain)
    for size, param_l in params
  ]

def save_data_to_csv(data):
  #Saving data to a csv file
  data_file = open('metrics_with_conf_int.csv','a')
  for sample in data: 
    for metric in sample:
      data_file.write(str(metric))
      data_file.write(",")
    data_file.write("\n")
  data_file.close()

def _sd(arr):
  mean = np.mean(arr)
  arr = arr - mean
  arr = arr ** 2
  tmp = sum(arr)
  return sqrt(tmp / (len(arr)))

def _sem(arr):
  return _sd(arr) / sqrt(len(arr))

def mean_confidence_interval_man(data, confidence=0.95):
  a = 1.0 * np.array(data)
  n = len(a)
  m, se = np.mean(a), _sem(a)
  lb_ub = np.array(st.t.interval(confidence, len(data) - 1))
  lb_ub *= se
  lb_ub += m
  lb, ub = lb_ub
  return m, lb, ub

def main():
  size = 5
  p = Pool()
  const_params = [(size, [
    Param("send_duration", np.random.RandomState(seed).normal, (300, 2)),
    Param("prop_time", identity, (0.00013, )),
    Param("startup_time", np.random.RandomState(seed).uniform, (0,400))
    ]) 
    for seed in range(40) #numero simulazioni
  ]
  params = send_spacing_domain(const_params, (1, 200, 10)) #crea per ogni parametro una simulazione
  params = recv_off_domain(params, (1, 300, 10)) 
  print("To do: ", len(params))
  results = defaultdict(list)
  for i, env in enumerate(p.imap_unordered(simulate, params)):
    results[(env.get_param("send_spacing"), env.get_param("recv_duration"))].append(env)
    if i % 1000 == 0:
      print("{}/{}".format(i, len(params)))

  to_draw = []
  xs, ys, zs = [], [], []
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  
  for etq, envs in results.items():
    avg_disc = avg([calc_avg_disc(env) for env in envs]) #average discovery rate
    mean, lower_bound_disc, upper_bound_disc = mean_confidence_interval_man([calc_avg_disc(env) for env in envs])
    #print("Avg discovery rate: ", avg_disc, mean, lower_bound_disc, upper_bound_disc)

    norm_rdc = avg([calc_norm_radio_dc(env) for env in envs]) #quanto rimane accesa la radio
    mean, lower_bound_rdc, upper_bound_rdc = mean_confidence_interval_man([calc_norm_radio_dc(env) for env in envs])
    #print("Norm rdc: ", norm_rdc, mean, lower_bound_rdc, upper_bound_rdc)

    avg_receiver_off = avg([env.get_param("off_duration") for env in envs]) #quanto rimane accesa la radio
    mean, lower_bound_receiver_off, upper_bound_receiver_off = mean_confidence_interval_man([env.get_param("off_duration") for env in envs])
    #print("Avg receiver off: ", avg_receiver_off, mean, lower_bound_receiver_off, upper_bound_receiver_off)

    norm_disc = (avg_disc - 1) / (size - 1) #average discovery rate normalizzato
    lower_bound_norm_disc = (lower_bound_disc - 1) / (size - 1)
    upper_bound_norm_disc = (upper_bound_disc - 1) / (size - 1)
    #print("Norm disc rate: ", norm_disc, lower_bound_norm_disc, upper_bound_norm_disc)

    cumul = (norm_disc + (1-norm_rdc))/2 #quanti nodi si scoprono per Watt nel sistema, trovare un modo per normalizzarlo
    lower_cumul = (lower_bound_norm_disc + (1 - lower_bound_rdc))/2
    upper_cumul = (upper_bound_norm_disc + (1 - upper_bound_rdc))/2
    #print("Cumul: ", cumul, lower_cumul, upper_cumul)

    to_draw.append((norm_rdc, lower_bound_rdc, upper_bound_rdc, cumul, lower_cumul, upper_cumul, norm_disc, lower_bound_norm_disc, upper_bound_norm_disc, avg_receiver_off, etq))

    xs.append(etq[0])
    ys.append(etq[1])
    zs.append(norm_disc)
    
  ax.set_xlabel('Send Spacing')
  ax.set_ylabel('Recv Duration')
  ax.set_zlabel('Cumul avg(dr, rdc)')
  ax.scatter(np.array(xs), np.array(ys), np.array(zs))
  plt.show()
  
  to_draw.sort(key=lambda x: x[1])
  to_draw.reverse()
  to_draw = to_draw[:50]
  
  save_data_to_csv(to_draw)



if __name__ == "__main__":
  main()