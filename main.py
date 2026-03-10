import numpy as np
import pandas as pd
import sarracen as sar


if __name__ == '__main__':
    data = sar.read_phantom('prograde/prograde_00000')[0]
    print(data.columns.values.tolist())
    