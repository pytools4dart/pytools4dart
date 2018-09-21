# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import numpy as np
from os.path import join as pjoin
import pytools4dart as ptd


simu = ptd.simulation(name='use_case_1')

simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

dic = {'CBrown': 0.0, 'Cab': range(0,30,10), 'Car': 5,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 0}

simu.add_prospect_sequence(dic, 'proprieteoptpros', name='prospect_sequence')
simu.add_single_plot(opt_name='proprieteoptpros')

print(simu)

simu.write_xmls()
simu.run.full()
simu.run.sequence('prospect_sequence')




###
simu.get_sequence_db_path("prospect_sequence")

conn = sqlite3.connect(simu.get_sequence_db_path("prospect_sequence"))

c=conn.cursor()

# Create table
result=[]
for row in c.execute('''select  idCombination,  valueCentralWavelength, valueResult
from ScalarResult, DirectionalResult, Reflectance, SpectralBand
where directionalResult.IdViewAngle = 1
and scalarResult.idSpectralBand = SpectralBand.idSpectralBand
and scalarResult.IdScalarResult = DirectionalResult.IdScalarResult
and DirectionalResult.idDirectionalResult = reflectance.idDirectionalResult
group by idCombination, valueCentralWavelength
'''):
    result.append(row)

df = pd.DataFrame(result, columns=['id', 'wavelength', 'reflectance'])
df.set_index('wavelength', inplace=True)
df.groupby('id')['reflectance'].plot(legend=True)
plt.show()
plt.ylabel('reflectance')

plt.savefig(pjoin(simu.getsimupath(), 'output', 'R_Chl.png'))
plt.close()
