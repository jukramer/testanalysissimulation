import pandas as pd
import sarracen
import matplotlib.pyplot as plt

SECTIONAL_VIEW = False

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
x_sink_0 = sdf_sinks.at[0, 'x'] 
y_sink_0 = sdf_sinks.at[0, 'y'] 

x_sink_1 = sdf_sinks.at[1, 'x']
y_sink_1 = sdf_sinks.at[1, 'y']

print(sdf)
print(sdf_sinks)

plt.style.use('dark_background')

# Below one is not a sectional view

# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True, xsec=0.00)
# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True)

if SECTIONAL_VIEW:
    ax = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00)
else:
    ax = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True)

# Sink particles visualisation
def plot_sinks(ax):
    ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
    ax.scatter(x=x_sink_1, y=y_sink_1, color='white')

# sectional view at z = 0 , for sdf.itype, 1 = gas, 7 = dust (stokes = 10), 8 = dust (stokes = 1)
ax_1 = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00, cmap = 'bone')
ax_1.set_title("Gas Distribution in Disc")
plot_sinks(ax_1)
plt.show()

ax_2 = sdf[sdf.itype == 7].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00, cmap = 'gray', alpha = 0.6)
sdf[sdf.itype == 8].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00, cmap = 'gist_heat', ax = ax_2, alpha = 0.8)
ax_2.set_title("Dust Distribution in Disc")
plot_sinks(ax_2)
plt.show()


# TODO See if it is possible to have the heatmap be blue --> didn't find exact colour but picked another one
# TODO Centering accretion disc and moving all dust with it
# TODO Work on radial binning analysis


