from heapq import heappush, heappop
from events import *
import numpy as np

SIMULATION_END = 2 * 1000 

class Node:
  MODE_SEND = "Mode send"
  MODE_RECV = "Mode receive"
  MODE_OFF  = "Mode off"
  def __init__(self, i, position):
    self.position = position
    self.mode = Node.MODE_OFF
    self.discovered = set([i])
    self.id = i
  def discover(self, msg):
    self.discovered.add(msg.id)
  def distance_from(self, other):
    return (
      ((self.position[0] - other.position[0]) ** 2) +
      ((self.position[1] - other.position[1]) ** 2)) ** .5

class Environment:
  def __init__(self, nodes, params):
    self.time = 0
    self.params = params
    self.nodes = nodes
    self.evt_queue = []
    self.ism = 0 #in system messages
    for node in nodes:
      StartEvent(node.id, 0, self).new_from_now().plan()
    self.push(EndEvent(-1, SIMULATION_END, self))
  def push(self, message):
    heappush(self.evt_queue, message)
  def pop(self):
    return heappop(self.evt_queue)
  def co(self, message):
    self.ism += 1
  def cf(self, message):
    self.ism -= 1
  def is_cf(self):
    return self.ism == 0
  def simulate(self):
    last_evt = self.pop()
    while self.evt_queue and not last_evt.same_kind(EndEvent):
      last_evt.run()
      last_evt = self.pop()
  def get_param(self, name):
    return self.params.get_value(name)
  def cget_param(self, name):
    return self.params.cget_value(name) 
  def evolve(self, name):
    self.params.evolve(name)

def main():
  nodes = [Node(i, (i,i)) for i in range(10)]
  e = Environment(nodes)
  e.simulate()
  for node in e.nodes:
    print(node.discovered)


if __name__ == '__main__':
  main()
