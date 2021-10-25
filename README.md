# Airflow-StudyClub
Grupo de estudio Apache Airflow



## iniciar desde /Airflow/docker-compose-yaml

```bash
cd Airflow
pwd 
```
```.../Airflow-StudyClub/Airflow```

Initializing Environment
Before starting Airflow for the first time, You need to prepare your environment, i.e. create the necessary files, directories and initialize the database.

Setting the right Airflow user
On Linux, the quick-start needs to know your host user id and needs to have group id set to 0. Otherwise the files created in dags, logs and plugins will be created with root user. You have to make sure to configure them for the docker-compose:

```bash
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

For other operating systems, you will get warning that AIRFLOW_UID is not set, but you can ignore it. You can also manually create the .env file in the same folder your docker-compose.yaml is placed with this content to get rid of the warning:


``` AIRFLOW_UID=50000 ```


## Initialize the database

On all operating systems, you need to run database migrations and create the first user account. To do it, run.

```docker-compose up airflow-init```


After initialization is complete, you should see a message like below.

``` bash
airflow-init_1       | User "airflow" created with role "Admin"
airflow-init_1       | 2.2.0
airflow_airflow-init_1 exited with code 0
```


## Running Airflow

```docker-compose up```


```bash
airflow-webserver_1  | 127.0.0.1 - - [25/Oct/2021:03:49:23 +0000] "GET /health HTTP/1.1" 200 187 "-" "curl/7.64.0"
airflow-webserver_1  | 127.0.0.1 - - [25/Oct/2021:03:49:33 +0000] "GET /health HTTP/1.1" 200 187 "-" "curl/7.64.0"
airflow-webserver_1  | 127.0.0.1 - - [25/Oct/2021:03:49:44 +0000] "GET /health HTTP/1.1" 200 187 "-" "curl/7.64.0"
airflow-webserver_1  | 127.0.0.1 - - [25/Oct/2021:03:49:54 +0000] "GET /health HTTP/1.1" 200 187 "-" "curl/7.64.0"
```



-------------------------------

## Cleaning-up the environment
The docker-compose we prepare is a "Quick-start" one. It is not intended to be used in production and it has a number of caveats - one of them being that the best way to recover from any problem is to clean it up and restart from the scratch.

```docker-compose down --volumes --remove-orphans```

## Cleaning up

To stop and delete containers, delete volumes with database data and download images, run:

```docker-compose down --volumes --rmi all```



more details http://airflow.apache.org/docs/apache-airflow/stable/start/docker.html
