from sigmar import * 


#----------------Sigma R of GAS---------------------
Snapshots = [10,11,12,16,20]
encounter = ['prograde', 'retrograde', 'incl_30']
for i in range(len(Snapshots)):
    for j in range(len(encounter)):
        sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{Snapshots[i]}')
        rVals, sigmaVals = calcSigma(sdfGas, n=30, rIn=10, rOut=150)
        plt.plot(rVals, sigmaVals, label=f'{encounter[j]}')
    plt.yscale('log')
    plt.title(f'Gas Surface Density Profile at Snapshot {Snapshots[i]}')
    plt.xlabel('Radius')
    plt.ylabel('Sigma')
    plt.legend()
    plt.show()


for i in range(len(Snapshots)):
    for j in range(len(encounter)):
        sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{Snapshots[i]}')
        rVals, sigmaVals = calcSigma(sdfDust1, n=30, rIn=10, rOut=150)
        plt.plot(rVals, sigmaVals, label=f'{encounter[j]} - Dust 1')
        rVals, sigmaVals = calcSigma(sdfDust2, n=30, rIn=10, rOut=150)
        plt.plot(rVals, sigmaVals, label=f'{encounter[j]} - Dust 2', linestyle='--')
    plt.yscale('log')
    plt.title(f'Dust Surface Density Profile at Snapshot {Snapshots[i]}')
    plt.xlabel('Radius')
    plt.ylabel('Sigma')
    plt.legend()
    plt.show()