from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np

simul_params = {
  "off_duration"     : 000,
  "recv_duration"    : 400,
  "send_duration"    : 400,
  "off_dist"         : identity, 
  "send_spacing"     : 2,
  "propagation_time" : 0.00013, #ms to run 40m in air
  "startup_dist"     : np.random.uniform,
  "startup_delay"    : (0, 20)
}


def build_network(size):
  return [Node(i, (i,i)) for i in range(size)]

def main():
  nodes = build_network(10)
  params = [
    Param("recv_duration", identity, (400, ), identity), 
    Param("off_duration",  identity, (0, )  , identity),
    Param("send_duration", identity, (400, ), identity),
    Param("send_spacing", identity, (2, ), identity),
    Param("prop_time", identity, (0.00013, ), identity),
    Param("startup_time", np.random.uniform, (0,20), identity)
  ]
  params_manager = SimulParamsManager(params)
  e = Environment(nodes, params_manager)
  e.simulate()

if __name__ == "__main__":
  main()
