import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import util
from datetime import datetime
from datetime import timedelta
import sys

date_format = '%Y-%m-%d'
datetime_format = '%Y%m%d-%H:%M:%S'
tick = sys.argv[1]
start = datetime.strptime(sys.argv[2], date_format).date()
end = datetime.strptime(sys.argv[3], date_format).date()
step = int(sys.argv[4])
syms = tick.split(',')
quotes = util.load_quotes(start, end, syms)
print('%d' % len(syms))
k = [15, 30, 60, 120, 240, 480, 960, 1920]
for i in range(len(syms)):
  fig = Figure()
  ax = fig.add_subplot(111)
#  s = datetime.strptime(quotes[i][0][5], datetime_format)
#  t = [(datetime.strptime(x[5], datetime_format)-s).total_seconds()/60 for x in quotes[i]]
  t = [x[5] for x in quotes[i]]
  p = [(x[1]+x[2])/2 for x in quotes[i]]
  y_min = min(p)-0.1*(max(p)-min(p))
  y_max = max(p)+0.1*(max(p)-min(p))
  datetimes = [datetime.strptime(x[5], datetime_format) for x in quotes[i]]
  util.day_splitter_plot(datetimes, step, y_min, y_max, ax)
  t = [x for j,x in enumerate(t) if j%step==0]
  p = [x for j,x in enumerate(p) if j%step==0]
  ax.plot(p)
  for j in range(len(k)):
    if len(p)>k[j]:
      util.min_max_band_plot(p, k[j], False, ax)
  ax.set_ylim(y_min, y_max)
  ax.set_xlim(0, len(p)*1.05)
  canvas = FigureCanvasAgg(fig)
  canvas.print_figure('/usr/share/nginx/www/quotes/%s.png' % syms[i], dpi=200)
