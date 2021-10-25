"""
Example DAG demonstrating the usage of DateTimeBranchOperator with datetime as well as time objects as
targets.
"""
import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}


with DAG(
    dag_id="genesis_dag",
    default_args=default_args,
    description='Test DAG',
    start_date=datetime.datetime(2021, 10, 25),
    catchup=False,
    tags=["test"],
    schedule_interval="@daily",
    owner="DataEngineeringLATAM"
) as dag:
    # [START howto_branch_datetime_operator]
    dummy_task_1 = DummyOperator(task_id='dummy_task_1', dag=dag)
    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    dag >> [dummy_task_1, t1]
    # [END howto_branch_datetime_operator]
