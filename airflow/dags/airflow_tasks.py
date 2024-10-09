import pandas as pd
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable

POSTGRES_CONN_ID = 'postgres_local'
S3_CONN_ID = 'aws_s3_conn'

def extract_data(ti):
    """ Extract SMILES and related columns from a table
    for the current day """
    skip = ti.xcom_pull(
        task_ids='load_data',
        key='last_saved'
    )
    output_file = 'smiles.csv'
    postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    engine = postgres_hook.get_sqlalchemy_engine()
    df = pd.read_sql_table('molecules', engine)
    df.to_csv(output_file, index=False)
    return output_file


def transform_data(ti):
    """ Transform data, by adding column Molecular weight, logP,
    TPSA, H Donors, H Acceptors and Lipinski pass properties """
    # Grab, process data
    file_path = ti.xcom_pull(task_ids='extract_data')
    df = pd.read_csv(file_path)
    df.rename(columns=str.upper, inplace=True)
    df.drop_duplicates(subset='SMILES', inplace=True)
    print("The dataframe is:")
    print(df)
    processed_mols_df = compute_mol_props(df)
    print("\nTransform data, which would compute_mol_props(df)")
    print(processed_mols_df)
    # Save processed data to CSV
    output_file_path = 'output.csv'
    processed_mols_df.to_csv(output_file_path, index=False)
    ti.xcom_push(
            key='output_file_path',
            value=output_file_path 
    )


def compute_mol_props(chunk_df):
    chunk_df['mol'] = chunk_df['SMILES'].apply(AllChem.MolFromSmiles)
    mol_property_funcs = {
        'Molecular weight': Descriptors.MolWt,
        'logP': Descriptors.MolLogP,
        'TPSA': rdMolDescriptors.CalcTPSA,
        'H Donors': Descriptors.NumHDonors,
        'H Acceptors': Descriptors.NumHAcceptors
    }
    mol_properties = list(mol_property_funcs)
    chunk_df[mol_properties] = chunk_df.apply(
        lambda row: [mol_property_funcs[prop](row['mol'])
                     for prop in mol_properties],
        axis=1,
        result_type='expand'
    )
    chunk_df['Lipinski pass'] = (
        (chunk_df['Molecular weight'] < 500)
        & (chunk_df['logP'] < 5)
        & (chunk_df['H Acceptors'] < 10)
        & (chunk_df['H Donors'] < 5)
    )
    chunk_df.drop(columns=['mol'], inplace=True)
    first = ['SMILES', *mol_properties, 'Lipinski pass']
    chunk_df = chunk_df[first + list(chunk_df.columns.difference(first))]
    return chunk_df


# Use ti properties to get an info about the execution date
def load_data(ti, ds):
    """ Save resulting data as .xlsx file and load it to S3 """
    xlsx_file_name = f'SMILES and props {ds}.xlsx'
    file_path = ti.xcom_pull(
        task_ids='transform_data',
        key='output_file_path'
    )
    print(f'Converting data from {file_path} to {xlsx_file_name}.')
    df = pd.read_csv(file_path)
    print(df)
    df.to_excel(xlsx_file_name, index=False, header=True)
    # Instantiate cloud file storage connection, upload to S3 using predefined method
    bucket_name = Variable.get("bucket_name")
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
    s3_hook.load_file(
        xlsx_file_name,
        xlsx_file_name,
        bucket_name,
        replace=True
        )
    print('Check upload file')
