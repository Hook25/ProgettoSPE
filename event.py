class Event:
  _kind = "Event"
  def __init__(self, id, ts):
    self.id = id
    self.ts = ts
  def __str__(self):
    return "[%s] %s" % (self.ts, self._kind)
  def run(self, master):
    raise ValueError("Not implemented")
  def same_kind(self, other):
    return other and self._kind == other._kind
  def __lt__(self, other):
    return self.ts < other.ts
  def new_from_now(self):
    return self.dst_get_value()
  
class SendEvent(Event):
  _kind = "SendEvent"
  def run(self, master):
    master.msg_join(self)

def NodeStartEvent(Event):
  _kind = "NodeStartEvent"
  def run(self, master):
    SendEvent(self.id, self.ts).new_from_now().plan()
    
def EndEvent(Event): pass

class LeftEnvEvent(Event):
  _kind = "LeftEnvEvent"
  def run(self, master):
    master.msg_left(self)

