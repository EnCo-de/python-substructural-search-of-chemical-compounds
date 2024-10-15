import pandas as pd

def main(wells_df: pd.DataFrame, plates_df: pd.DataFrame, experiments_df: pd.DataFrame):
    df = wells_df.loc[:, ~wells_df.columns.isin(['property_name', 'property_value'])]
    # df.merge(right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=None, indicator=False, validate=None)
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
    data.sort_values(by=['well_id', 'plate_id', 'experiment_id', 'property_name'],
                     inplace=True, ignore_index=True)
    # print(data)


    # Each well has a set of properties, which might vary according to experiments. It might be concentration, concentration_unit, type, channel, channel_order and any other properties
    # You should use pandas to read the content of tables and combine them in a result table,
    # which would contain columns well_id, well_row, well_column and properties for columns, specified in a property_name in wells, plates and experiments tables.
    # If some value is not defined for some well, you should place here a None value. Save results to .xlsx file.
    # Extra task: consider cases, then 2 properties are defined on 2 levels (for example, in well and plate tables), This way you should place the value from the lower level in a resulting table.
    result = data.merge(wells_df, how='outer', suffixes=('', '_'))
                        # on=['well_id', 'plate_id', 'property_name'])
    result = result.merge(plates_df, how='outer', suffixes=('', '_1'),
                        on=['plate_id', 'experiment_id', 'property_name'])
    result = result.merge(experiments_df, how='left', suffixes=('', '_2'),
                        on=['experiment_id', 'property_name'])
    
    result['values'] = result['property_value'].fillna(result['property_value_1']).fillna(result['property_value_2'])
    # result = result.pivot(index=['well_id', 'well_row', 'well_column', 'plate_id'], 
    result = result.pivot(index='well_id',
                          columns='property_name',
                          values='values').reset_index()
    print(result.fillna('').sort_values(
        by='well_id',
        ignore_index=True
        ))
    # table = result.drop(['property_value_1', 'property_value_2'], axis=1)


if __name__ == '__main__':
    wells_df=pd.DataFrame()
    plates_df=pd.DataFrame()
    experiments_df=pd.DataFrame()
    main(wells_df, plates_df, experiments_df)
