def identity(x): return x

class Param:
  def __init__(self, name, dist, params, evolve_function):
    self.name = name
    self.dist = dist
    self.params = params
    self.evolve_function = evolve_function
  def evolve(self):
    self.params = self.evolve_function(self.params)
  def get_value(self):
    return self.dist(*self.params)

class SimulParamsManager:
  def __init__(self, params):
    self.params = { param.name : param for param in params } 
  def get_value(self, name):
    return self.params[name].get_value()
  def evolve(self, name):
    self.params[name].evolve()
