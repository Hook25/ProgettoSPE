from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np
from multiprocessing import Pool
from collections import defaultdict

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
  TOT_RECV_W = 600
  return [(
    size, 
    param_l + [
      Param("recv_duration", identity, (TOT_RECV_W - x_dom, )),
      Param("off_duration", identity, (TOT_RECV_W - (TOT_RECV_W - x_dom), ))
    ])
    for x_dom in range(*domain)
    for size, param_l in params
  ]
  

def main():
  size = 5
  p = Pool()
  const_params = [(size, [
    Param("send_duration", identity, (300, )),
    Param("prop_time", identity, (0.00013, )),
    Param("startup_time", np.random.RandomState(seed).uniform, (0,400))
    ]) 
    for seed in range(30)
  ]
  params = send_spacing_domain(const_params, (1, 200, 10))
  params = recv_off_domain(params, (50, 300, 20))
  print("To do: ", len(params))
  results = defaultdict(list)
  for i, env in enumerate(p.imap_unordered(simulate, params)):
    results[(env.get_param("send_spacing"), env.get_param("recv_duration"))].append(env)
    if i % 1000 == 0:
      print("{}/{}".format(i, len(params)))
  from matplotlib import pyplot as plt
  to_draw = []
  for etq, envs in results.items():
    avg_disc = avg([calc_avg_disc(env) for env in envs])
    norm_rdc = avg([calc_norm_radio_dc(env) for env in envs])
    norm_disc = (avg_disc - 1) / (size - 1)
    cumul = norm_disc / norm_rdc
    to_draw.append((norm_rdc, cumul, etq, norm_disc))
  to_draw.sort(key=lambda x: x[1])
  to_draw.reverse()
  to_draw = to_draw[:50]
  for norm_rdc, cumul, etq, disc_norm in to_draw:
    plt.bar(norm_rdc, cumul) 
    print(norm_rdc, cumul, etq, disc_norm)
  plt.show()


if __name__ == "__main__":
  main()