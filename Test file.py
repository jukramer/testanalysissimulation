import sarracen
import pandas
import matplotlib.pyplot as plt


sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00011')


sdf.calc_density()
# sdf.describe()
print(sdf)
print(sdf_sinks)
# print(sdf['itype'].value_counts())

x1 = sdf['x'].quantile(0.0005)
x2 = sdf['x'].quantile(0.995)

y1 = sdf['y'].quantile(0.0005)
y2 = sdf['y'].quantile(0.995)

#Creating dots for sink particles
x_sink_0 = sdf_sinks.at[0, 'x']
y_sink_0 = sdf_sinks.at[0, 'y']

x_sink_1 = sdf_sinks.at[1, 'x']
y_sink_1 = sdf_sinks.at[1, 'y']

plt.style.use('dark_background')

ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 500, x_sink_0 + 500), ylim=(y_sink_0 - 500, y_sink_0 + 500), log_scale=True, xsec=0.00)
ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
ax.scatter(x=x_sink_1, y=y_sink_1, color='white')

# TODO See if it is possible to have the heatmap be blue
# TODO Centering follows 95th percentile rule
# TODO Work on radial binning analysis

plt.show()