# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import numpy as np
from os.path import join as pjoin
import pytools4dart as ptd


simu = ptd.simulation(name='use_case_1')

simu.add_bands({'wvl':np.linspace(.4, 1, 10), 'fwhm':0.01})

#### Define optical properties
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name ='op_prospect'
op_vegetation = {'type':'vegetation',
              'op_name': op_name,
              'db_name':'prospect.db',
              'op_name_in_db':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add_optical_property(op_vegetation)


#### Define mockup
simu.add_single_plot(op_name=op_name)

#### Define sequence
simu.add_prospect_sequence({'Cab': range(0,30,10)}, 'op_prospect',
                           name='prospect_sequence')

#### show simulation content
print(simu)

#### write simulation
simu.write(overwrite=True)
simu.run.full()
simu.run.sequence('prospect_sequence')




#### Figure of scene reflectance function of chlorophyll
simu.get_sequence_db_path("prospect_sequence")
conn = sqlite3.connect(simu.get_sequence_db_path("prospect_sequence"))
c=conn.cursor()

# extract reflectance and chlorophyll values
result=[]
for row in c.execute('''select  valueParameter, valueCentralWavelength, valueResult
from ScalarResult, DirectionalResult, Reflectance, SpectralBand, Combination, P_Cab
where directionalResult.IdViewAngle = 1
and scalarResult.idSpectralBand = SpectralBand.idSpectralBand
and scalarResult.IdScalarResult = DirectionalResult.IdScalarResult
and DirectionalResult.idDirectionalResult = reflectance.idDirectionalResult
and Combination.idCombination = scalarResult.idCombination
and P_Cab.idValueParameter = Combination.id_Cab
group by valueParameter, valueCentralWavelength
'''):
    result.append(row)

df = pd.DataFrame(result, columns=['chl', 'wavelength', 'reflectance'])
# df.chl = pd.to_numeric(df.chl)
df.wavelength = 10**9*df.wavelength
df.set_index('wavelength', inplace=True)
df.groupby('chl')['reflectance'].plot(legend=True)
plt.xlabel('Wavelength [nm]')
plt.ylabel('Reflectance')
plt.legend(title='Chl [mg/m3]')
plt.show()
# plt.savefig(pjoin(simu.getsimupath(), 'output', 'R_Chl.png'))
plt.close()
