import pandas as pd
import sarracen
import matplotlib.pyplot as plt



def render(filename, limits=400, itype=1, sectionview=False):
    """
    Limits show limits of plot, itype refers to gas / dust / dust and finally sectionview enables for a column density or
    """
    
    sdf, sdf_sinks = sarracen.read_phantom(filename)
    sdf.calc_density()

    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']

    x_sink_0 = sdf_sinks.at[0, 'x']
    y_sink_0 = sdf_sinks.at[0, 'y']

    x_sink_1 = sdf_sinks.at[1, 'x']
    y_sink_1 = sdf_sinks.at[1, 'y']

    if sectionview:
        ax = sdf[sdf.itype == itype].render('rho', xlim=(-limits, limits), ylim=(-limits, limits), log_scale=True, xsec=0.00)
    else:
        ax = sdf[sdf.itype == itype].render('rho', xlim=(-limits,  limits), ylim=(-limits, limits), log_scale=True)

    # Sink particles visualisation
    ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
    ax.scatter(x=x_sink_1, y=y_sink_1, color='white')

    ax.set_xlim([-limits, limits])
    ax.set_ylim([-limits, limits]) 
    return plt

# Testing function
# output = render("prograde/prograde_00011", sectionview=True)
# output.show()