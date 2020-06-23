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

def simulate(size_params_seed):
  size, params, seed = size_params_seed
  nodes = build_network(size)
  params_manager = SimulParamsManager(params)
  print(seed, params_manager.get_value("startup_time"))
  e = Environment(nodes, params_manager)
  e.simulate()
  return (size, e)

def avg(x): return sum(x) / len(x)

def calc_avg_disc(env):
  disc = [len(node.discovered) for node in env.nodes]
  return avg(disc)

def main():
  SIZE = 10
  p = Pool()
  params = [(SIZE, [
    Param("recv_duration", identity, (300, )), 
    Param("off_duration",  identity, (300, )),
    Param("send_duration", identity, (300, )),
    Param("send_spacing", identity, (111 - i, )),
    Param("prop_time", identity, (0.00013, )),
    Param("startup_time", np.random.RandomState(seed).uniform, (0,400))
  ], seed) for seed, i in enumerate(list(range(10, 110, 10)) * 100)]
  results = defaultdict(list)
  for size, env in p.imap_unordered(simulate, params):
    results[env.params.get_value("send_spacing")].append(env)
  from matplotlib import pyplot as plt
  for send_spacing, envs in results.items():
    avg_val = avg([avg([len(node.discovered) for node in env.nodes]) for env in envs])
    plt.bar(send_spacing, avg_val - 1)
    print(send_spacing, avg_val)
  plt.show()


if __name__ == "__main__":
  main()
