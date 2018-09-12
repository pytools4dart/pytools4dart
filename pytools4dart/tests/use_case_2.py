import pandas as pd
import pytools4dart as pt4d

inventory_file = '/home/boissieu/Florian/IRSTEA/Software/DART_5-7-1_v1061/database/trees.txt'
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

simu = pt4d.simulation('use_case_2')

simu.addtrees(inventory)

