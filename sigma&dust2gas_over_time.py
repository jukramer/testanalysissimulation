from sigmar import * 

encounter = ['prograde', 'retrograde', 'incl_30']
color = ['blue', 'gold', 'green']
time = np.linspace(0, 1, 21)

G =  6.67430e-11 # gravitational constant in m^3 kg^-1 s^-2
Msolar = 1.988475e30  # solar mass in kg
AU = 1.496e11   #au in meters
yr = 3.1536e7  #seconds in a year


# for j in range(len(encounter)):
#     sigmaavg = []
#     for i in range(21):
#         if i < 10:
#             sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_0000{i}')
#         else:
#             sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{i}')
#         rVals, sigmaVals, Avals = calcSigma(sdfGas, n=30, rIn=10, rOut=150)
#         sigmavals = np.array(sigmaVals)
#         A = np.array(Avals)
#         sigmaavg.append(np.sum(sigmavals*A))
#     plt.plot(time, sigmaavg, label=f'{encounter[j]}', color=color[j])
# plt.yscale('log')
# plt.title(f'Gas Surface Density Profile over time')
# plt.xlabel('Time')
# plt.ylabel('Sigma')
# # plt.ylim(3e-8, 1e-6)
# plt.legend()
# plt.show()

for j in range(len(encounter)):
    masstot = []
    for i in range(21):
        if i < 10:
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_0000{i}')
            sdfFilt = sdfGas[sdfGas['r'].between(0, 500)]
            mass = np.sum(sdfFilt['mass'].to_numpy())
            masstot.append(mass)
        else:
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{i}')
            sdfGas['Energy'] = 0.5*(sdfGas['vx']**2 + sdfGas['vy']**2 + sdfGas['vz']**2) * (AU ** 2) / ((2 * np.pi * yr)**2)  - G * Msolar / (sdfGas['r'] * AU)
            #sdfFilt = sdfGas[sdfGas['Energy']<0]
            sdfFilt = sdfGas[sdfGas['r'].between(0, 500)]
            mass = np.sum(sdfFilt['mass'].to_numpy())
            masstot.append(mass)
        
    plt.plot(time, masstot, label=f'{encounter[j]}', color=color[j])
plt.yscale('log')
plt.title(f'Gas mass Profile over time')
plt.xlabel('Time')
plt.ylabel('Mass')
# plt.ylim(3e-8, 1e-6)
plt.legend()
plt.show()



for j in range(len(encounter)):
    masstot = []
    for i in range(21):
        if i < 10:
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_0000{i}')
            sdfFilt1 = sdfDust1[sdfDust1['r'].between(0, 500)]
            sdfFilt2 = sdfDust2[sdfDust2['r'].between(0, 500)]
            mass = np.sum(sdfFilt1['mass'].to_numpy()) + np.sum(sdfFilt2['mass'].to_numpy())
            masstot.append(mass)
        else:
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{i}')

            sdfDust1['Energy'] = 0.5*(sdfDust1['vx']**2 + sdfDust1['vy']**2 + sdfDust1['vz']**2) - G * Msolar / sdfDust1['r']
            sdfDust2['Energy'] = 0.5*(sdfDust2['vx']**2 + sdfDust2['vy']**2 + sdfDust2['vz']**2) - G * Msolar / sdfDust2['r']
            sdfFilt1 = sdfDust1[sdfDust1['r'].between(0, 400)]
            sdfFilt2 = sdfDust2[sdfDust2['r'].between(0, 400)]
            mass = np.sum(sdfFilt1['mass'].to_numpy()) + np.sum(sdfFilt2['mass'].to_numpy())
            masstot.append(mass)
    plt.plot(time, masstot, label=f'{encounter[j]}', color=color[j])
plt.yscale('log')
plt.title(f'Dust mass Profile over time')
plt.xlabel('Time')
plt.ylabel('Mass')
# plt.ylim(3e-8, 1e-6)
plt.legend()
plt.show()