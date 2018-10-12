
import lxml.etree as etree
import cProfile
import pytools4dart as ptd
from pytools4dart.xsdschema.utils import get_gs_troot, update_node
import timeit
troot = get_gs_troot('plots', 'DartFile')
# creation d'un plots.xml par defaut
tic=timeit.default_timer()
plots = ptd.plots_gds.DartFile()
# update_node(plots, troot)
# toc=timeit.default_timer()


# print(etree.tostring(plots.to_etree(), pretty_print=True))
plots.Plots.add_Plot(ptd.plots_gds._Plot())
plots.Plots.add_Plot(ptd.plots_gds._Plot())
plots.Plots.Plot[0].set_form(1)

print(etree.tostring(plots.to_etree(), pretty_print=True))
toc=timeit.default_timer()
print(toc - tic)
tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(ptd.plots_gds._Plot())
toc=timeit.default_timer()
print(toc - tic)
