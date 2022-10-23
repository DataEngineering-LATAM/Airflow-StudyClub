with DAG(
    "MyDAG",
    max_active_runs=1,
    schedule_interval='8 5 * * 2-6',
    start_date=datetime(2021, 4, 19),
    default_args=default_args,
    catchup=False
) as dag:
    if(True):
        # DUMMY
        create_report = DummyOperator(task_id='CREATE_REPORT')
        copy_into_s3 = DummyOperator(task_id='COPY_INTO_S3')
        save_status = DummyOperator(task_id='SAVE_STATUS')
    elif(1==1):
        # CREATE REPORT
        create_report = MyOperator(
            task_id='CREATE_REPORT',
            sql='.sql',
            params=params_definition
        )
        # COMPY INTO S3
        copy_into_s3 = MyOperator(
            task_id='COPY_INTO_S3',
            sql='COPY_INTO_S3.sql',
            params={'date': yesterday,
                    'schema': schema}
        )
        # SAVE STATUS
        save_status = MyOperator(
            task_id='SAVE_STATUS',
            sql='.sql',
            params={'date': yesterday,
                    'schema': schema}
        )

    # PROCESSING
    dag >> create_report >> copy_into_s3 >> save_status