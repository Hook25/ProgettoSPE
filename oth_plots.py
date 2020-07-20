import matplotlib.pyplot as plt
import csv
import numpy as np
from main import ddd_list, dd_list, dddd_list, name_size_cparam_vparam_envs

def calc_norm_avg_disc(env):
  def _avg(x): return sum(x) / len(x)
  disc = [(len(node.discovered) - 1) / len(env.nodes) for node in env.nodes]
  return _avg(disc)

def calc_norm_radio_dc(env):
  send_wgt = 0.1
  recv_duration = env.cget_param("recv_duration")
  off_duration = env.cget_param("off_duration")
  send_duration = env.cget_param("send_duration")
  send_spacing = env.cget_param("send_spacing")
  norm_recv = recv_duration / ( off_duration + recv_duration ) 
  norm_send = (send_duration / send_spacing) / send_duration
  wgt_norm_send = send_wgt * norm_send 
  return (norm_recv + wgt_norm_send) / (1 + send_wgt)
  
def avg(arr, cnf=.95):
  import scipy.stats
  a = 1.0 * np.array(arr)
  n = len(a)
  m, se = np.mean(a), scipy.stats.sem(a)
  h = se * scipy.stats.t.ppf((1 + cnf) / 2., n-1)
  return m, m-h, m+h, h

def calc_cumul(envs):
  norm_disc, norm_disc_lb, norm_disc_ub, ndd = avg([calc_norm_avg_disc(env) for env in envs]) 
  norm_rdc, norm_rdc_ub, norm_rdc_lb, nrd = avg([calc_norm_radio_dc(env) for env in envs]) 
  cumul = (norm_disc + (1-norm_rdc))/2
  cumul_d = (ndd + nrd)/2
  return ((norm_rdc, norm_rdc_ub, norm_rdc_lb), 
    (norm_disc, norm_disc_lb, norm_disc_ub), 
    (cumul, cumul - cumul_d, cumul + cumul_d))
  
def b_dom_cumul(param_envs):
  x = list(param_envs.keys())
  y = [
    calc_cumul(envs) for _, envs in param_envs.items()
  ]
  return x, y

def plot_conf_int(x, y, both_ci = False, **kwargs):
  if both_ci:
      plt.scatter([i[0] for i in x], [j[0] for j in y], **kwargs)
  else:
      plt.scatter(x, [i[0] for i in y], **kwargs)
  if "c" not in kwargs:
    kwargs["c"] = "b"
  for i in range(len(x)):
    if both_ci:
      plt.plot([x[i][1], x[i][2]], [y[i][0], y[i][0]], marker="_", c = kwargs["c"])
      plt.plot([x[i][0], x[i][0]], [y[i][1], y[i][2]], marker="_", c = kwargs["c"])
    else:
      plt.plot([x[i], x[i]], [y[i][1], y[i][2]], marker="_", c = kwargs["c"])

def get_palette(size, start, end):
  def get_str_hex(n):
    hx = hex(n).split('x')[-1]
    if len(hx) == 1:
      return "0" + hx
    return hx
  rs, gs, bs = int(start[0:2], 16), int(start[2:4], 16), int(start[4:6], 16)
  re, ge, be = int(end[0:2], 16), int(end[2:4], 16), int(end[4:6], 16)
  dr, dg, db = int((rs - re) / size) , int((gs - ge) / size), int((bs - be) / size)
  print(dr, dg, db)
  return ["#" + get_str_hex(rs - dr * i) + 
    get_str_hex(gs - dg * i) + 
    get_str_hex(bs - db * i) for i in range(size)] 

if __name__ == "__main__":
  import pickle
  with open("save.pkl", "rb") as f:
    saved = pickle.load(f)
  
  for graph_name in saved: 
    title = "Const [ %s ]: Size: " % graph_name
    x_label = "recv_duration"
    if graph_name == x_label:
        x_label = "send spacing"
    
    for size in saved[graph_name]:
        fig_cumul = plt.figure(num=1)
        fig_rdc = plt.figure(num=2)
        fig_ndsc = plt.figure(num=3)
        name = "imgs/" + graph_name + "_" + str(size)
        
        plt.figure(num=1)
        plt.title(title + str(size))
        plt.xlabel(x_label)
        plt.ylabel("(norm_disc + (1 - norm_rdc)) / 2")
        
        plt.figure(num=2)
        plt.title(title + str(size))
        plt.xlabel(x_label)
        plt.ylabel("Radio Duty Cycle")
        
        plt.figure(num=3)
        plt.title(title + str(size))
        plt.xlabel(x_label)
        plt.ylabel("Normalized Discovery Rate")
        
        palette = get_palette(len(saved[graph_name][size]), "000000", "FF0000")
        for p_i, cnst_param in enumerate(saved[graph_name][size]):
            x, cumul = b_dom_cumul(saved[graph_name][size][cnst_param])
            y_rdc = [c[0] for c in cumul]
            y_disc = [c[1] for c in cumul]
            y_cumul = [c[2] for c in cumul]
            
            plt.figure(num=1)
            plot_conf_int(x, y_cumul, label="{}".format(cnst_param), c = palette[p_i], s=6)  
            
            plt.figure(num=2)
            plot_conf_int(x, y_rdc, label="{}".format(cnst_param), c = palette[p_i], s=6)
            
            plt.figure(num=3)
            plot_conf_int(x, y_disc, label="{}".format(cnst_param), c = palette[p_i], s=6)
        
        for i in range(1, 4):
            plt.figure(num=i)
            plt.legend(loc = 'center left', bbox_to_anchor=(1.04, 0.5), borderaxespad=0)
            plt.subplots_adjust(right=0.7)

        plt.figure(num=1) 
        plt.savefig(name + "_cumul.png", dpi=300)
        plt.clf()
        
        plt.figure(num=2) 
        plt.savefig(name + "_rdc.png", dpi=300)
        plt.clf()
        
        plt.figure(num=3) 
        plt.savefig(name + "_dsc.png", dpi=300)
        plt.clf()

