import sarracen
import pandas


sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00000')


sdf.calc_density()
# sdf.describe()
print(sdf)
# print(sdf_sinks)
# print(sdf['itype'].value_counts())

# sdf[sdf.itype == 1].render('rho', xlim=(-1000, 1000), ylim=(-1000, 1000), log_scale=True, xsec=0.0)