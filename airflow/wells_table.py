import pandas as pd

def main(wells_df: pd.DataFrame, plates_df: pd.DataFrame, experiments_df: pd.DataFrame):
    """
    Each well has a set of properties, which might vary according to experiments. It might be concentration, concentration_unit, type, channel, channel_order and any other properties.
    
    You should use pandas to read the content of tables and combine them in a result table,
    which would contain columns well_id, well_row, well_column and properties for columns, specified in a property_name in wells, plates and experiments tables.
    If some value is not defined for some well, you should place here a None value. Save results to .xlsx file.
    
    Extra task: consider cases, then 2 properties are defined on 2 levels (for example, in well and plate tables), This way you should place the value from the lower level in a resulting table.
    """
    df = wells_df.loc[:, ~wells_df.columns.isin(['property_name', 'property_value'])]
    df = df.merge(plates_df[['plate_id', 'experiment_id']], how='left', on='plate_id')
    df.drop_duplicates(inplace=True)

    df1 = df.merge(wells_df[['plate_id', 'well_id', 'property_name']], how='left',
                  sort=True, suffixes=('', '_1'),
                  on=['plate_id', 'well_id'])
    df2 = df.merge(plates_df[['plate_id', 'experiment_id', 'property_name']], how='left',
                  sort=True, suffixes=('', '_2'),
                  on=['plate_id', 'experiment_id'])
    df3 = df.merge(experiments_df[['experiment_id', 'property_name']], how='left',
                  sort=True, suffixes=('', '_3'),
                  on='experiment_id')
    data = pd.concat([df1, df2, df3], ignore_index=True)
    data.drop_duplicates(inplace=True)

    result = data.merge(wells_df, how='outer', suffixes=('', '_'))
                        # on=['well_id', 'plate_id', 'property_name'])
    result = result.merge(plates_df, how='outer', suffixes=('', '_1'),
                        on=['plate_id', 'experiment_id', 'property_name'])
    result = result.merge(experiments_df, how='left', suffixes=('', '_2'),
                        on=['experiment_id', 'property_name'])

    result['values'] = result['property_value'].fillna(result['property_value_1']).fillna(result['property_value_2'])
    result = result.pivot(index=['well_id', 'well_row', 'well_column'],
                          columns='property_name',
                          values='values').reset_index()
    result.to_excel('Wells table.xlsx', index=False, na_rep=None)
    print(result.fillna(''))


if __name__ == '__main__':
    wells_df=pd.DataFrame({
        'well_id': [1001, 1002, 2003, 2004, 1005, 2001, 1006],
        'well_row': [1, 1, 2, 2, 2, 2, 2],
        'well_column': [1, 2, 3, 4, 1, 1, 2],
        'plate_id': [101, 101, 203, 203, 102, 203, 102],
        'property_name': ['density', 'concentration', 'concentration', 'unit', 'unit', 'color', 'concentration'],
        'property_value': ['123', '2', '3', 'fl. oz', 'fl. oz', 'cyan', None]
    })

    plates_df = pd.DataFrame({
        'plate_id': [101, 102, 203, 203],
        'experiment_id': [1, 1, 2, 2],
        'property_name': ['density', 'color', 'density', 'state'],
        'property_value': ['0', 'green', '203', 'liquid']
    })

    experiments_df = pd.DataFrame({
        'experiment_id': [1, 2, 2, 3],
        'property_name': ['unit', 'unit', 'stability', 'none'],
        'property_value': ['ul', 'ul', 'true', 'none']
    })

    main(wells_df, plates_df, experiments_df)
