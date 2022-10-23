import io
from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from custom.postgres_to_s3_operator import PostgresToS3Operator


def _crunch_numbers():
    s3 = S3Hook(aws_conn_id='remotes3')

    # Get list of all objects
    objects = [
        obj
        for obj in s3.list_keys(bucket_name="bkt-airflow-study-group-dev", prefix="raw/listing")
    ]
    print(f"files: {objects}")

    df = pd.DataFrame()
    for obj in objects:
        response = s3.get_key(
            bucket_name="bkt-airflow-study-group-dev", key=obj
        )
        temp_df = pd.read_csv(
            io.BytesIO(response.get()['Body'].read()),
            usecols=["id", "price", "download_date"],
            parse_dates=["download_date"],
        )

        df = df.append(temp_df)

    print(f"df: {df.shape}")

    # Per id, get the price increase/decrease
    # There's probably a nicer way to do this
    min_max_per_id = (
        df.groupby(["id"])
        .agg(
            download_date_min=("download_date", "min"),
            download_date_max=("download_date", "max"),
        )
        .reset_index()
    )
    df_with_min = (
        pd.merge(
            min_max_per_id,
            df,
            how="left",
            left_on=["id", "download_date_min"],
            right_on=["id", "download_date"],
        )
        .rename(columns={"price": "oldest_price"})
        .drop("download_date", axis=1)
    )
    df_with_max = (
        pd.merge(
            df_with_min,
            df,
            how="left",
            left_on=["id", "download_date_max"],
            right_on=["id", "download_date"],
        )
        .rename(columns={"price": "latest_price"})
        .drop("download_date", axis=1)
    )

    df_with_max = df_with_max[
        df_with_max["download_date_max"] != df_with_max["download_date_min"]
    ]
    df_with_max["price_diff_per_day"] = (
        df_with_max["latest_price"] - df_with_max["oldest_price"]
    ) / ((df_with_max["download_date_max"] - df_with_max["download_date_min"]).dt.days)
    df_with_max[["price_diff_per_day"]] = df_with_max[["price_diff_per_day"]].apply(
        pd.to_numeric
    )
    biggest_increase = df_with_max.nlargest(5, "price_diff_per_day")
    biggest_decrease = df_with_max.nsmallest(5, "price_diff_per_day")

    # We found the top 5, write back the results.
    biggest_increase_json = biggest_increase.to_json(orient="records")
    print(f"Biggest increases: {biggest_increase_json}")
    biggest_increase_bytes = biggest_increase_json.encode("utf-8")
    s3.load_bytes(
        bytes_data=biggest_increase_bytes,
        bucket_name="bkt-airflow-study-group-dev",
        key="processed/biggest_increase.json",
        replace=True
    )

    biggest_decrease_json = biggest_decrease.to_json(orient="records")
    print(f"Biggest decreases: {biggest_decrease_json}")
    biggest_decrease_bytes = biggest_decrease_json.encode("utf-8")
    s3.load_bytes(
        bytes_data=biggest_decrease_bytes,
        bucket_name="bkt-airflow-study-group-dev",
        key="processed/biggest_decrease.json",
        replace=True
    )


with DAG(
    dag_id="chapter7_insideairbnb_py",
    start_date=datetime(2021, 3, 4),
    end_date=datetime(2022, 3, 27),
    schedule_interval="@monthly",
    tags=['chapter7', 'data-engineering-LATAM'],
    # catchup=False  # temp

) as dag:

    download_from_postgres = PostgresToS3Operator(
        task_id="download_from_postgres",
        postgres_conn_id="inside_airbnb",
        query="SELECT * FROM listings WHERE download_date BETWEEN '{{ prev_ds }}' AND '{{ ds }}'",
        s3_conn_id="remotes3",
        s3_bucket="bkt-airflow-study-group-dev",
        s3_key="raw/listing-{{ ds }}.csv",
    )

    crunch_numbers = PythonOperator(
        task_id="crunch_numbers", python_callable=_crunch_numbers
    )


download_from_postgres >> crunch_numbers
