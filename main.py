from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np

def build_network(size):
  return [Node(i, (i,i)) for i in range(size)]

def inc_1(prop):
  return [x + 1 for x in prop]

def dec_1(prop):
  return [x-1 for x in prop]

def simulate(size):
  nodes = build_network(size)
  params = [
    Param("recv_duration", identity, (400, ), dec_1), 
    Param("off_duration",  identity, (000, )  , inc_1),
    Param("send_duration", identity, (400, ), identity),
    Param("send_spacing", identity, (1, ), identity),
    Param("prop_time", identity, (0.00013, ), identity),
    Param("startup_time", np.random.uniform, (0,20), identity)
  ]
  params_manager = SimulParamsManager(params)
  e = Environment(nodes, params_manager)
  e.simulate()
  return e

def avg(x): return sum(x) / len(x)

def calc_avg_disc(env):
  disc = [len(node.discovered) for node in env.nodes]
  return avg(disc)

def main():
  envs = [simulate(5) for _ in range(40)]
  disc = (avg([calc_avg_disc(env) for env in envs]) - 1) / 4
  print(disc)


if __name__ == "__main__":
  main()
