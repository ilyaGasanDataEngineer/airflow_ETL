from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
import pandas as pd
from matplotlib import pyplot as plt


def get_data_from_sql(**kwargs):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="29892989",
        host="localhost",
        port="5432"
    )
    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT * FROM api_data_weather ORDER BY date_interested"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Передача данных через XCom
        kwargs['ti'].xcom_push(key='data', value=rows)
    finally:
        cursor.close()
        conn.close()


def agregation_data(**kwargs):
    # Получение данных из XCom
    data = kwargs['ti'].xcom_pull(task_ids='get_data_from_sql', key='data')

    # Преобразование данных в DataFrame
    df = pd.DataFrame(data, columns=['id', 'date_requested', 'date_interested', 'min_temp_C', 'max_temp_C', 'uv_index',
                                     'wind_kmph', 'visibility', 'temp_C', 'time'])

    # Агрегация данных
    df_agregated = df[
        ['date_interested', 'min_temp_C', 'max_temp_C', 'uv_index', 'wind_kmph', 'visibility', 'temp_C']].groupby(
        ['date_interested']).mean().reset_index()

    # Передача агрегированных данных через XCom
    kwargs['ti'].xcom_push(key='aggregated_data', value=df_agregated.to_dict(orient='records'))


def visualisation(**kwargs):
    # Получение агрегированных данных из XCom
    aggregated_data = kwargs['ti'].xcom_pull(task_ids='aggregate', key='aggregated_data')

    # Преобразование списка словарей обратно в DataFrame
    df = pd.DataFrame(aggregated_data)

    # Построение графика
    plt.figure(figsize=(15, 7))
    plt.plot(df['date_interested'], df['min_temp_C'], label='Min Temp C')
    plt.plot(df['date_interested'], df['max_temp_C'], label='Max Temp C')
    plt.plot(df['date_interested'], df['temp_C'], label='Temp C')

    plt.xlabel('Date Interested')
    plt.ylabel('Temperature (C)')
    plt.title('Temperature Trends')
    plt.legend()

    # Сохранение графика в файл
    plt.savefig('/tmp/temp_trends.png')


def add_aggrregated_data(**kwargs):
    # Получение агрегированных данных из XCom
    aggregated_data = kwargs['ti'].xcom_pull(task_ids='aggregate', key='aggregated_data')

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="29892989",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # SQL-запрос для вставки данных
        query = """
        INSERT INTO agregated_data_trends (date, min_temp, max_temp, uv_index, wind, visibility, temp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Выполнение запроса для каждой строки в агрегированных данных
        for record in aggregated_data:
            cursor.execute(query, (
                record['date_interested'],
                record['min_temp_C'],
                record['max_temp_C'],
                record['uv_index'],
                record['wind_kmph'],
                record['visibility'],
                record['temp_C']
            ))

        # Подтверждение изменений
        conn.commit()

    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
    finally:
        # Закрытие курсора и соединения
        cursor.close()
        conn.close()


default_args = {
    'owner': 'ilya',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 28),
}

with DAG('agregation_and_visualisation', description='aggregation data', schedule_interval='*/1 * * * *', catchup=False,
         default_args=default_args) as dag:
    get_data = PythonOperator(task_id='get_data_from_sql', python_callable=get_data_from_sql, provide_context=True)
    agregation = PythonOperator(task_id='aggregate', python_callable=agregation_data, provide_context=True)
    visualisate = PythonOperator(task_id='visualisate', python_callable=visualisation, provide_context=True)
    add_data = PythonOperator(task_id='add_data', python_callable=add_aggrregated_data, provide_context=True)

    get_data >> agregation
    agregation >> [visualisate, add_data]
