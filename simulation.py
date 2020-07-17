from environment import Environment, Node
from simul_params import Param, SimulParamsManager, identity
import numpy as np
from multiprocessing import Pool

def avg(x): return sum(x) / len(x)

def build_network(size):
  return [Node(i, (i,i)) for i in range(size)]

def simulate(size, seed):
  nodes = build_network(size)
  params = [
    Param("recv_duration", identity, (50, )), 
    Param("off_duration",  identity, (900, )),
    Param("send_duration", identity, (50, )),
    Param("send_spacing", identity, (1, )),
    Param("prop_time", identity, (0.00013, )),
    Param("startup_time", np.random.RandomState(seed).uniform, (0,400))
  ]
  params_manager = SimulParamsManager(params)
  e = Environment(nodes, params_manager)
  e.simulate()
  return e

def avg(x): return sum(x) / len(x)

def calc_avg_disc(env):
  disc = [len(node.discovered) for node in env.nodes]
  return avg(disc)

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

def save_data_to_csv(data):
  #Saving data to a csv file
  data_file = open('simulations.csv','a')
  for value in data: 
    data_file.write(str(value))
    data_file.write(",")
  data_file.write("\n")
  data_file.close()

def main():
  size = 3
  total_simulations = 10
  envs = [simulate(size, i) for i in range(total_simulations)]
  avg_disc = avg([calc_avg_disc(env) for env in envs]) #average discovery rate
  norm_rdc = avg([calc_norm_radio_dc(env) for env in envs]) #quanto rimane accesa la radio
  norm_disc = (avg_disc - 1) / (size - 1) #average discovery rate normalizzato
  cumul = (norm_disc + norm_rdc)/2 #quanti nodi si scoprono per Watt nel sistema, trovare un modo per normalizzarlo
  print("Average discovery rate over ", size, " nodes: ", avg_disc)
  print("Normalized radio duty cycle: ", norm_rdc)
  print("Normalized discovery rate over ", size, " nodes: ", norm_disc)
  print("Cumulative metric with ", size, " nodes:",cumul)
  save_data_to_csv([
    envs[0].get_param("recv_duration"),
    envs[0].get_param("off_duration"),
    envs[0].get_param("send_duration"),
    envs[0].get_param("send_spacing"),
    avg_disc,
    norm_disc,
    norm_rdc,
    cumul,
    size
  ])

if __name__ == "__main__":
  main()