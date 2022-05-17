import pytools4dart as ptd
from path import Path
import pkgutil
param_file = Path(__file__).parent.parent / 'docs/DART_parameters.md'
with open(param_file, 'w') as f:
    labels = ptd.utils.get_labels()
    modules = [s.name for s in pkgutil.iter_modules(ptd.core_ui.__path__)]
    labels = labels[labels.dartnode.apply(lambda x: x.lower().split('.')[0] in modules)]
    labels = labels.iloc[labels.dartnode.str.lower().argsort()]  # not necessary, ordering already in datatable.js
    labels.reset_index(drop=True, inplace=True)
    l = labels.dartnode.to_list()
    labels['type'] = 'node'
    labels.loc[labels.dartnode.apply(lambda x: sum([True for n in l if x in n]))==1, 'type']='attrib'
    labels['name'] = labels.dartnode.apply(lambda x: ('.'*(len(x.split('.'))-1)) + x.split('.')[-1])
    labels.rename(columns = {'label':'description', 'dartnode': 'path'}, inplace=True)
    labels = labels[['description', 'name', 'type', 'path']]
    labels.rename(columns={'name': 'name (dots = node level)'}, inplace=True)
    html_table = labels.to_html(index=False, table_id='dartTable',
                                col_space=[300, 100, 50, 300],
                                classes="display compact",
                                justify="left")
    html_table = html_table.replace('border="1"', 'style="width:100%"')#.replace('text-align: right;', 'text-align: left;')
    html_table = '**DART '+ptd.getdartversion()['build']+'**\n'+html_table
    f.write(html_table)