from sigmar import * 


#----------------Sigma R of GAS---------------------
Snapshots = [10,11,12,16,20]
encounter = ['prograde', 'retrograde', 'incl_30']
color = ['cornflowerblue', 'navajowhite', 'tab:green']

# for i in range(len(Snapshots)):
#     for j in range(len(encounter)):
#         sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{Snapshots[i]}')
#         rVals, sigmaVals, area = calcSigma(sdfGas, n=30, rIn=10, rOut=150)
#         plt.plot(rVals, sigmaVals, label=f'{encounter[j]}', color=color[j])
#     plt.yscale('log')
#     plt.title(f'Gas Surface Density Profile at Snapshot {Snapshots[i]}')
#     plt.xlabel('Radius [au]')
#     plt.ylabel('density []')
#     plt.ylim(3e-8, 1e-6)
#     plt.legend()
#     plt.show()

# #----------------Sigma R of dust---------------------
# for i in range(len(Snapshots)):
#     for j in range(len(encounter)):
#         sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{Snapshots[i]}')
#         rVals, sigmaVals = calcSigma(sdfDust1, n=30, rIn=10, rOut=150)
#         plt.plot(rVals, sigmaVals, label=f'{encounter[j]} - Dust 1', color=color[j])
#         rVals, sigmaVals = calcSigma(sdfDust2, n=30, rIn=10, rOut=150)
#         plt.plot(rVals, sigmaVals, label=f'{encounter[j]} - Dust 2', color=color[j], linestyle='--')
#     plt.yscale('log')
#     plt.title(f'Dust Surface Density Profile at Snapshot {Snapshots[i]}')
#     plt.xlabel('Radius')
#     plt.ylabel('Sigma')
#     plt.ylim(5e-10, 5e-8)
#     plt.legend()
#     plt.show()

#----------------dust-to-gas ratio---------------------
for i in range(len(Snapshots)):
    for j in range(len(encounter)):
        sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{Snapshots[i]}')
        rVals, sigmaValsgas, area = calcSigma(sdfGas, n=30, rIn=10, rOut=150)
        rVals, sigmaValsdust1, area = calcSigma(sdfDust1, n=30, rIn=10, rOut=150)
        rVals, sigmaValsdust2, area = calcSigma(sdfDust2, n=30, rIn=10, rOut=150)

        sigmaValsgas = np.array(sigmaValsgas)
        sigmaValsdust1 = np.array(sigmaValsdust1)
        sigmaValsdust2 = np.array(sigmaValsdust2)
        
        sigmaValsdust = sigmaValsdust1 + sigmaValsdust2

        sigmaRatio = sigmaValsdust / sigmaValsgas
        plt.plot(rVals, sigmaRatio, label=f'{encounter[j]}', color=color[j])
    plt.yscale('log')
    plt.title(f'Dust-to-gas ratio profile at Snapshot {Snapshots[i]}')
    plt.xlabel('Radius [au]')
    plt.ylabel('dust-to-gas ratio')
    plt.legend()
    plt.show()
