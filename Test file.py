import sarracen
import pandas
import matplotlib.pyplot as plt
import matplotlib


sdf, sdf_sinks = sarracen.read_phantom('retrograde/retrograde_00007')


sdf.calc_density()
# sdf.describe()
print(sdf)
print(sdf_sinks)
# print(sdf['itype'].value_counts())

# For 30 degrees incline it seems the x, y and z are kind of swapped or something




# ower_bound = df['column_name'].quantile(0.05) and upper_bound = df['column_name'].quantile(0.95)

x1 = sdf['x'].quantile(0.05)
x2 = sdf['x'].quantile(0.95)

y1 = sdf['y'].quantile(0.05)
y2 = sdf['y'].quantile(0.95)

# only getting data from protoplanetary disc sink
x_sink_0 = sdf_sinks.at[0, 'x']
y_sink_0 = sdf_sinks.at[0, 'y']



ax = sdf[sdf.itype == 1].render('rho', xlim=(x1 -100, x2 + 100), ylim=(y1 -100, y2 + 100), log_scale=True, xsec=0.00)
ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
plt.show()