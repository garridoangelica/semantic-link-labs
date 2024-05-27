import sempy
import sempy.fabric as fabric
import pandas as pd
from .ListFunctions import list_tables
from .HelperFunctions import format_dax_object_name

def show_unsupported_direct_lake_objects(dataset: str, workspace: str | None = None):

    """
    
    Documentation is available here: https://github.com/microsoft/semantic-link-labs?tab=readme-ov-file#show_unsupported_direct_lake_objects

    """

    pd.options.mode.chained_assignment = None

    if workspace == None:
        workspace_id = fabric.get_workspace_id()
        workspace = fabric.resolve_workspace_name(workspace_id)

    dfT = list_tables(dataset, workspace)
    dfC = fabric.list_columns(dataset = dataset, workspace = workspace)
    dfR = fabric.list_relationships(dataset = dataset, workspace = workspace)

    # Calc tables
    dfT_filt = dfT[dfT['Type'] == 'Calculated Table']
    dfT_filt.rename(columns={'Name': 'Table Name'}, inplace=True)
    t = dfT_filt[['Table Name', 'Type']]

    # Calc columns
    dfC_filt = dfC[(dfC['Type'] == 'Calculated') | (dfC['Data Type'] == 'Binary')]
    c = dfC_filt[['Table Name', 'Column Name', 'Type', 'Data Type', 'Source']]

    # Relationships
    dfC['Column Object'] = format_dax_object_name(dfC['Table Name'], dfC['Column Name'])
    dfR['From Object'] = format_dax_object_name(dfR['From Table'], dfR['From Column'])
    dfR['To Object'] = format_dax_object_name(dfR['To Table'], dfR['To Column'])
    merged_from = pd.merge(dfR, dfC, left_on='From Object', right_on='Column Object', how='left')
    merged_to = pd.merge(dfR, dfC, left_on='To Object', right_on='Column Object', how='left')

    dfR['From Column Data Type'] = merged_from['Data Type']
    dfR['To Column Data Type'] = merged_to['Data Type']

    dfR_filt = dfR[((dfR['From Column Data Type'] == 'DateTime') | (dfR['To Column Data Type'] == 'DateTime')) | (dfR['From Column Data Type'] != dfR['To Column Data Type'])]
    r = dfR_filt[['From Table', 'From Column', 'To Table', 'To Column', 'From Column Data Type', 'To Column Data Type']]

    #print('Calculated Tables are not supported...')
    #display(t)
    #print("Learn more about Direct Lake limitations here: https://learn.microsoft.com/power-bi/enterprise/directlake-overview#known-issues-and-limitations")
    #print('Calculated columns are not supported. Columns of binary data type are not supported.')
    #display(c)
    #print('Columns used for relationship cannot be of data type datetime and they also must be of the same data type.')
    #display(r)

    return t, c, r