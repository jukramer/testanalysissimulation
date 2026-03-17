import sarracen
import pandas
import matplotlib.pyplot as plt


sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00010')


sdf.calc_density()
# sdf.describe()
print(sdf)
print(sdf_sinks)
# print(sdf['itype'].value_counts())


sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x'] 
sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y'] 

sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y'] 

#Creating dots for sink particles

# star sink particle
x_sink_0 = sdf_sinks.at[0, 'x'] 
y_sink_0 = sdf_sinks.at[0, 'y'] 
# flyby sink particle
x_sink_1 = sdf_sinks.at[1, 'x']
y_sink_1 = sdf_sinks.at[1, 'y']

print(sdf)
print(sdf_sinks)

plt.style.use('dark_background')

# Below one is not a sectional view

# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True, xsec=0.00)
# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True)

# for sdf.itype, 1 = gas, 7 = dust species A, 8 = dust species B

# column integrated view
# ax = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True)

# sectional view at z = 0
ax = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00)


# Sink particles visualisation
ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
ax.scatter(x=x_sink_1, y=y_sink_1, color='white')

# TODO See if it is possible to have the heatmap be blue
# TODO Centering accretion disc and moving all dust with it
# TODO Work on radial binning analysis

plt.show()