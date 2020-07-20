from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np
from multiprocessing import Pool
from collections import defaultdict
from matplotlib import pyplot as plt

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
  time_to_send = 1
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

def dd_list() : return defaultdict(list)
def ddd_list() : return defaultdict(dd_list)
def dddd_list(): return defaultdict(ddd_list)
def name_size_cparam_vparam_envs(): return defaultdict(dddd_list)

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

def main():
  p = Pool()
  size = [5,25,50] * 140
  const_params = [(size[seed], [
    Param("send_duration", np.random.RandomState(seed).normal, (300, 2)),
    Param("prop_time", identity, (0.0013, )), #removed 1 0, now all times are ms / 10
    Param("startup_time", np.random.RandomState(seed).uniform, (0,1000))
    ]) 
    for seed in range(len(size)) #numero simulazioni
  ]
  params = send_spacing_domain(const_params, (1, 50, 9)) #crea per ogni parametro una simulazione
  params = recv_off_domain(params, (1, 300, 40)) 
  print("To do: ", len(params))
  
  import pickle
  results = name_size_cparam_vparam_envs()
  
  for i, env in enumerate(p.imap_unordered(simulate, params)):
    results["send_spacing"][len(env.nodes)][env.cget_param("send_spacing")][env.cget_param("recv_duration")].append(env)
    results["recv_duration"][len(env.nodes)][env.cget_param("recv_duration")][env.cget_param("send_spacing")].append(env)
    if i % 1000 == 0:
      print("{}/{}".format(i, len(params)))

  with open("save.pkl", "wb+") as f:
    pickle.dump(results, f)
  return
  
  to_draw = []
  xs, ys, zs = [], [], []
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  
  for etq, envs in results.items():
    avg_disc = avg([calc_avg_disc(env) for env in envs]) #average discovery rate
    norm_rdc = avg([calc_norm_radio_dc(env) for env in envs]) #quanto rimane accesa la radio
    norm_disc = (avg_disc - 1) / (size - 1) #average discovery rate normalizzato
    cumul = (norm_disc + (1-norm_rdc))/2 #quanti nodi si scoprono per Watt nel sistema, trovare un modo per normalizzarlo
    to_draw.append((norm_rdc, cumul, etq, norm_disc))
    xs.append(etq[0])
    ys.append(etq[1])
    zs.append(norm_disc)
    
  ax.set_xlabel('Send Spacing')
  ax.set_ylabel('Recv Duration')
  ax.set_zlabel('Cumul avg(dr, rdc)')
  ax.scatter(np.array(xs), np.array(ys), np.array(zs))
  plt.show()
  
  save_data_to_csv(to_draw)



if __name__ == "__main__":
  main()