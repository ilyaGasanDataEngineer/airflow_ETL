from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import xmltodict
import psycopg2


def getting_data(**kwargs):
    url = 'https://api.worldweatheronline.com/premium/v1/weather.ashx?key=45b084f9b45d4deca56125148242608&q=61.783673,%2034.328678&num_of_days=2000&format=xml'
    response = requests.get(url)
    response_json = xmltodict.parse(response.text)
    data = response_json['data']['weather']
    data_list = []
    for date in data:
        data_to_send = {
            'windspeedKmph': [],
            'visibility': [],
            'tempC': [],
            'time': [],
            'date_request': datetime.now().date(),
            'min_temp': date['mintempC'],
            'max_temp': date['maxtempC'],
            'uv_Index': date['uvIndex'],
            'date_interested': date['date']
        }
        for time in date['hourly']:
            data_to_send['windspeedKmph'].append(float(time['windspeedKmph']))
            data_to_send['visibility'].append(float(time['visibility']))
            data_to_send['tempC'].append(float(time['tempC']))
            data_to_send['time'].append(float(time['time']))
        data_list.append(data_to_send)
    print(data_list)
    kwargs['ti'].xcom_push(key='weather_data', value=data_list)


def data_transform(**kwargs):
    data = kwargs['ti'].xcom_pull(key='weather_data', task_ids='extract_data')
    kwargs['ti'].xcom_push(key='weather_data', value=data)
    


def push_data(**kwargs):
    data = kwargs['ti'].xcom_pull(key='weather_data', task_ids='transform_data')
    if data is None:
        print("No data received from XCom.")
        return 
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="29892989",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO api_data_weather (date_request, date_interested, min_temp, max_temp, uv_Index, windspeedKmph, visibility, tempC, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
        
            for record in data:
                date_request = record['date_request']
                for i in range(len(record['time'])):
                    cursor.execute(insert_query, (
                        date_request,
                        record['date_interested'],
                        float(record['min_temp']),
                        float(record['max_temp']),
                        int(record['uv_Index']),
                        record['windspeedKmph'][i],
                        record['visibility'][i],
                        record['tempC'][i],
                        record['time'][i]
                    ))
        except Exception as e:
            print('Looks like th same data it mean that constrain in ps saied not unique')
            print(e)
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")




default_args = {
    'owner': 'ilya',
    'start_date': datetime(2024, 8, 28),
}

with DAG('ETL_porocces_weather', description='ETL weather', schedule_interval='*/1 * * * *', catchup=False,
         default_args=default_args) as dag:
    extract_data = PythonOperator(task_id='extract_data', python_callable=getting_data, provide_context=True)
    transform_data = PythonOperator(task_id='transform_data', python_callable=data_transform, provide_context=True)
    push_data_op = PythonOperator(task_id='push_data', python_callable=push_data, provide_context=True)

    extract_data >> transform_data >> push_data_op
