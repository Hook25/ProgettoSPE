from heapq import heappush, heappop
from events import *

SIMULATION_END = 10 * 60 * 1000 #1 minute

def identity(x): return x

simul_params = {
  "off_duration" : 300,
  "recv_duration": 100,
  "send_duration": 400,
  "off_dist"     : identity, 
  "send_delay"   : 300, 
  "send_spacing" : 20
}

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
  def get_recv_duration():
    return simul_params["recv_duration"]
  def get_off_duration():
    return simul_params["off_duration"]
  def get_send_duration():
    return simul_params["send_duration"]
  def get_send_spacing():
    return simul_params["send_spacing"]

class Environment:
  def __init__(self, nodes):
    self.time = 0
    self.nodes = nodes
    self.evt_queue = []
    self.ism = 0 #in system messages
    for node in nodes:
      StartEvent(node.id, 0, self).new_from_now().plan()
    self.push(EndEvent(-1, SIMULATION_END, self))
  def ca(self, message):
    self.ism -= 1
  def push(self, message):
    heappush(self.evt_queue, message)
  def pop(self):
    return heappop(self.evt_queue)
  def co(self, message):
    self.ism += 1
  def simulate(self):
    last_evt = self.pop()
    while self.evt_queue and not last_evt.same_kind(EndEvent):
      last_evt.run()
      last_evt = self.pop()


def main():
  nodes = [Node(i, (i,i)) for i in range(10)]
  e = Environment(nodes)
  e.simulate()
  for node in e.nodes:
    print(node.discovered)


if __name__ == '__main__':
  main()
