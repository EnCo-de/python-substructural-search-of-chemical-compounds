from airflow import DAG
# from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import airflow_tasks

""" Airflow DAG, which would read data from the table
in you project and write results to S3 bucket.
DAG Schedule is to run on a daily basis.  """

with DAG(
    dag_id='smiles_descriptors_etl_dag',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 10, 8),
    # schedule='@daily',
    # start_date=datetime.today(),
    catchup=False,
    tags=['python_school', 'hw', 'etl_example']
) as dag:
    start_op = EmptyOperator(
        task_id='start'
    )
    extract_data_op = PythonOperator(
        task_id='extract_data',
        python_callable=airflow_tasks.extract_data
    )
    transform_data_op = PythonOperator(
        task_id='transform_data',
        python_callable=airflow_tasks.transform_data
    )
    load_data_op = PythonOperator(
        task_id='load_data',
        python_callable=airflow_tasks.load_data
    )
    finish_op = EmptyOperator(
        task_id='finish'
    )

    start_op >> extract_data_op >> transform_data_op
    transform_data_op >> load_data_op >> finish_op