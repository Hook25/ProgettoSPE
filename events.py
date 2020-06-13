import numpy as np
from environment import Node

def identitiy(x): return x

class Event:
  _kind = "Event"
  def __init__(self, id, ts, master):
    self.id = id
    self.ts = ts
    self.master = master
  def __str__(self):
    return "[%s] %s" % (self.ts, self._kind)
  def run(self):
    raise ValueError("Not implemented")
  def same_kind(self, other):
    return other and self._kind == other._kind
  def __lt__(self, other):
    return self.ts < other.ts
  def new_from_now(self):
    self.ts += self.dst_get_value()
    return self
  def plan(self):
    self.master.push(self)
    return self

class LeaveCarrierEvent(Event):
  _kind = "LeaveCarrierEvent"
  def __init__(self, id, ts, master, collided):
    super().__init__(id, ts, master)
    self.collided = collided
  def run(self):
    self.master.cf(self)
    if self.collided: return
    for node in self.master.nodes:
      if node.mode == Node.MODE_RECV:
        node.discover(self)
  def dst_get_value(self):
    return Node.get_prop_time()

class SendEvent(Event):
  _kind = "SendEvent"
  def run(self):
    self.master.co(self)
    collided = not self.master.is_cf()
    LeaveCarrierEvent(self.id, self.ts, self.master, collided).new_from_now().plan()
  def dst_get_value(self):
    return Node.get_send_spacing()

class ModeOffEvent(Event):
  _kind = "ModeOffEvent"
  def dst_get_value(self):
    """off is after recv, so running it terminates the former"""
    return Node.get_recv_duration()
  def run(self):
    self.master.nodes[self.id].mode = Node.MODE_OFF
    ModeSendEvent(self.id, self.ts, self.master).new_from_now().plan()

class ModeRecvEvent(Event):
  _kind = "ModeRecvEvent"
  def dst_get_value(self):
    """recv is after send, so scheduling it will terminate the former"""
    return Node.get_send_duration()
  def run(self):
    self.master.nodes[self.id].mode = Node.MODE_RECV
    ModeOffEvent(self.id, self.ts, self.master).new_from_now().plan()

class ModeSendEvent(Event):
  _kind = "ModeSendEvent"
  def run(self):
    mode_switch_evt = ModeRecvEvent(
      self.id, self.ts, self.master).new_from_now().plan()
    self.master.nodes[self.id].mode = Node.MODE_SEND
    next_send = SendEvent(self.id, self.ts, self.master).new_from_now()
    limit_ts = mode_switch_evt.ts
    while(next_send.ts < limit_ts):
      next_send.plan()
      next_send = SendEvent(
        self.id, next_send.ts, self.master).new_from_now()
  def dst_get_value(self):
    return Node.get_off_duration() 

class StartEvent(Event):
  _kind = "StartEvent"
  def dst_get_value(self):
    return Node.get_startup_time()
  def run(self):
    ModeSendEvent(self.id, self.ts, self.master).plan() 

class EndEvent(Event): pass

class LeftEnvEvent(Event):
  _kind = "LeftEnvEvent"
  def run(self, master):
    master.msg_left(self)

