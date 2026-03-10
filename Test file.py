import sarracen
import pandas
import matplotlib.pyplot as plt


sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00000')


sdf.calc_density()
# sdf.describe()
# print(sdf)
# print(sdf_sinks)
# print(sdf['itype'].value_counts())

ax = sdf[sdf.itype == 1].render('rho', xlim=(-820, -650), ylim=(1000, 1170), log_scale=True, xsec=0.0)
plt.show()