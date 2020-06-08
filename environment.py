
class Node:
  def __init__(self, i, position):
    self.position = position
    self.discovered = set([i])
  def discover(self, msg):
    self.discovered.insert(msg.id)
  def distance_from(self, other):
    return (
      ((self.position[0] - other.position[0]) ** 2) +
      ((self.position[1] - other.position[1]) ** 2)) ** .5

class Environment:
  def __init__(self, nodes):
    self.time = 0
    self.evt_queue = []
    self.ism = 0 #in system messages
  def msg_left(self, message):
    self.ism -= 1
  def msg_join(self, message):
    self.ism += 1
  def push_evt(self, message):
    self.evt_queue.push(message)
  def simulate(self):
    last_evt = self.evt_queue.pop()
    while self.evt_q and not last_evt.same_kind(EndEvent):
      last_evt.run()
      last_evt = self.evt_queue.pop()


def main():
  e = Environment([])
  e.simulate()


if __name__ == '__main__':
  main()
