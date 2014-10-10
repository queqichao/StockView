import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
from datetime import datetime
from datetime import timedelta
from sets import Set
from matplotlib import pyplot as plt
import numpy as np
from collections import deque
import os.path

base_dir = '/data/www/quotes/'
def load_quotes(dt, end=datetime.now(), symbols = None):
  tmp_dt = dt
  if end is None or dt==end:
    f = [x.split(' ') for x in open(base_dir+'data/quotes'+tmp_dt.strftime('%Y%m%d')).read().split('\n')]
    f = f[:-1]
  else:
    f = []
    while tmp_dt <= end:
      if os.path.isfile(base_dir+'data/quotes'+tmp_dt.strftime('%Y%m%d')):
        ff = [x.split(' ') for x in open(base_dir+'data/quotes'+tmp_dt.strftime('%Y%m%d')).read().split('\n')]
        ff = ff[:-1]
        for x in ff:
          f.append(x)
      tmp_dt += timedelta(days=1)
  if symbols is None:
    symbols = open(base_dir+'data/symbols').read().split('\n')[:-1]
  quotes = []
  for x in symbols:
    quotes.append([y for y in f if y[0]==x])
  for quote in quotes:
    for x in quote:
      x[1] = float(x[1])
      x[2] = float(x[2])
      x[3] = float(x[3])
  return quotes    

def diff(p, k):
  d = []
  if len(p)<k+1:
    raise NameError('Length of p is less than k+1.')
  for i in range(len(p)-k):
    d.append(p[i+k]-p[i])
  return d

def timestamps(datetimes, k):
  times = []
  for i in range(k, len(datetimes)):
    times.append((datetime.strptime(datetimes[i], '%Y%m%d-%H:%M:%S')-datetime(1970,1,1)).total_seconds())
  return times

def moving_max(p,k):
  max_deque = deque([])
  res = []
  for i in range(len(p)):
    if i>=k:
      if i-max_deque[0]>=k:
        max_deque.popleft()
    while len(max_deque)>0:
      if p[max_deque[-1]] > p[i]:
        break
      else:
        max_deque.pop()
    max_deque.append(i)
    if i>=k-1:
      res.append(p[max_deque[0]])
  return res

def moving_min(p,k):
  min_deque = deque([])
  res = []
  for i in range(len(p)):
    if i>=k:
      if i-min_deque[0]>=k:
        min_deque.popleft()
    while len(min_deque)>0:
      if p[min_deque[-1]] < p[i]:
        break
      else:
        min_deque.pop()
    min_deque.append(i)
    if i>=k-1:
      res.append(p[min_deque[0]])
  return res

def interpolate(syms, start_price, end_price, start_time, end_time):
  res = []
  delta_in_min = (end_time-start_time).seconds/60
  price_linspaces = []
  for i in range(len(syms)):
    price_linspaces.append([np.linspace(start_price[i][0], end_price[i][0], delta_in_min+1),np.linspace(start_price[i][1], end_price[i][1], delta_in_min+1),np.linspace(start_price[i][2], end_price[i][2], delta_in_min+1)])
  for i in range(len(price_linspaces[0][0])-1):
    for j in range(len(syms)):
      res.append(syms[j]+' '+'%.4f' % price_linspaces[j][0][i+1]+' '+'%.4f' % price_linspaces[j][1][i+1]+' '+'%.4f' % price_linspaces[j][2][i+1]+' '+(start_time+timedelta(0,60*(i+1))).strftime('%Y%m%d-%H:%M:%S')+' '+(start_time+timedelta(0,60*(i+1))).strftime('%Y%m%d-%H:%M:%S'))
  return '\n'.join(res)

def day_splitter_plot(datetimes, step, y_min, y_max, ax):
  ticks = []
  ticks_label = []
  print_date = True
  for i, d in enumerate(datetimes):
    if d.hour==15 and d.minute==59:
      ax.plot([i/step, i/step],[y_min, y_max], '--', color='#C0C0C0')
      if print_date:
        ticks.append(i/step)
      	ticks_label.append(d.strftime('%m%d'))
      print_date = not print_date
  ax.set_xticks(ticks)
  ax.set_xticklabels(ticks_label)

def min_max_band_plot(p, k, mid, ax):
  mmax = moving_max(p, k)
  mmin = moving_min(p, k)
  center = [u/2+v/2 for (u,v) in zip(mmax, mmin)]
  print("%d / %d = %f" % (len([1 for (u,v) in zip(center, p[k-1:]) if u<v]), len(p)-k+1, len([1 for (u,v) in zip(center, p[k-1:]) if u<v])*1.0/(len(p)-k+1))) 
  ax.plot(range(k-1, len(p)), mmax, 'r')
  ax.plot(range(k-1, len(p)), mmin, 'r')
  if mid:
    ax.plot(range(k-1, len(p)), center, 'y')

def bollinger_band_plot(p, k):
  ma = moving_average(p, k)
  sq_dev = np.square(np.array(p)-np.array(ma))
  stdev = np.sqrt(moving_average(sq_dev, k))
  plt.plot(range(k-1, len(p)), ma[k-1:])
  plt.plot(range(k-1, len(p)), np.array(ma[k-1:])-2*stdev[k-1:])
  plt.plot(range(k-1, len(p)), np.array(ma[k-1:])+2*stdev[k-1:])

def diff_in_perc(p, k):
  dp = []
  if len(p)<k+1:
    raise NameError('Length of p is less than k+1.')
  for i in range(len(p)-k):
    dp.append((p[i+k]-p[i])/p[i])
  return dp

def Covar(p1, p2, k):
  d1 = diff_in_perc(p1, k)
  d2 = diff_in_perc(p2, k)
  return np.cov(d1,d2)[0][1]

def Beta(p1, p2, k):
  d1 = diff_in_perc(p1, k)
  d2 = diff_in_perc(p2, k)
  Cov = np.cov(d1,d2)
  return Cov[0][1]/Cov[1][1]

def Rsq(p1, p2, k):
  d1 = diff_in_perc(p1, k)
  d2 = diff_in_perc(p2, k)
  SS_tot = np.sum(np.square(np.array(d2)-np.mean(d2)))
  SS_res = np.sum(np.square(np.array(d1)-np.array(d2)))
  return 1-SS_res/SS_tot

def moving_average(p, k):
  ma = []
  curr_sum = sum(p[0:k])
  for i in range(len(p)-k+1):
    ma.append(curr_sum/k)
    if i != len(p)-k:
      curr_sum = curr_sum-p[i]+p[i+k]
  ma = [ma[0]]*(k-1)+ma
  return ma

def compare_plot(p1, p2):
  plt.figure(1)
  plt.subplot(211)
  plt.plot(p1)
  plt.subplot(212)
  plt.plot(p2)
  plt.show()

