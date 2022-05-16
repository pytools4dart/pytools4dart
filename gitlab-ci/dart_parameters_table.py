import pytools4dart as ptd
from path import Path
import pkgutil
param_file = Path(__file__).parent.parent / 'docs/DART_parameters.md'
with open(param_file, 'w') as f:
    labels = ptd.utils.get_labels()
    modules = [s.name for s in pkgutil.iter_modules(ptd.core_ui.__path__)]
    labels = labels[labels.dartnode.apply(lambda x: x.lower().split('.')[0] in modules)]
    # labels = labels.iloc[labels.dartnode.str.lower().argsort()] # not necessary, ordering already in datatable.js
    labels.columns = ['description', 'core node']
    html_table = labels.to_html(index=False, table_id='dartTable', col_space=300)
    html_table = html_table.replace('class="dataframe"', 'class="display compact"').replace('border="1"', 'style="width:100%"').replace('text-align: right;', 'text-align: left;')
    html_table = '**DART '+ptd.getdartversion()['build']+'**\n'+html_table
    f.write(html_table)