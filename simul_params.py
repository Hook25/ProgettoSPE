def identity(x): return x

class Param:
  def __init__(self, name, dist, params):
    self.name = name
    self.dist = dist
    self.params = params
  def get_value(self):
    return self.dist(*self.params)
  def cget_value(self):
    return self.params[0]

class SimulParamsManager:
  def __init__(self, params):
    self.params = { param.name : param for param in params } 
  def get_value(self, name):
    return self.params[name].get_value()
  def cget_value(self, name):
    return self.params[name].cget_value()
