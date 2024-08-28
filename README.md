### README.md

```markdown
# Weather Data Aggregation and Visualization Project

## Описание проекта

Этот проект представляет собой автоматизированную систему для сбора, агрегации, визуализации и хранения данных о погоде. С помощью Apache Airflow выполняется последовательность задач (DAG), которая автоматизирует извлечение данных с использованием API, агрегацию, построение графиков и сохранение результатов в базе данных PostgreSQL.

### Основные шаги ETL процесса:
1. **Извлечение данных**: Получение данных о погоде из внешнего API и сохранение их в базу данных PostgreSQL.
2. **Агрегация данных**: Агрегация погодных данных по дням, включая расчеты минимальных и максимальных температур, средней скорости ветра и других параметров.
3. **Визуализация данных**: Построение графиков на основе агрегированных данных с использованием Matplotlib.
4. **Сохранение данных**: Сохранение агрегированных данных в таблицу для последующего анализа.

## Установка и настройка

### 1. Клонирование репозитория

Для начала, склонируйте репозиторий на свой компьютер:

```bash
git clone https://github.com/ilyaGasanDataEngineer/airflow_ETL.git
```

### 2. Установка зависимостей

Проект требует установки Python-зависимостей. Все необходимые библиотеки перечислены в файле `requirements.txt`. Используйте следующую команду для их установки:

```bash
pip install -r requirements.txt
```

### 3. Настройка PostgreSQL

Убедитесь, что у вас установлен и настроен PostgreSQL. Выполните следующие шаги для создания базы данных и таблиц:

1. **Создайте базу данных**:

```sql
CREATE DATABASE weather_db;
```

2. **Создайте таблицы**:

```sql
CREATE TABLE api_data_weather (
    id SERIAL PRIMARY KEY,
    date_requested DATE,
    date_interested DATE,
    min_temp_C FLOAT,
    max_temp_C FLOAT,
    uv_index INTEGER,
    wind_kmph FLOAT,
    visibility FLOAT,
    temp_C FLOAT,
    time INTEGER
);

CREATE TABLE agregated_data_trends (
    id SERIAL PRIMARY KEY,
    date DATE,
    min_temp FLOAT,
    max_temp FLOAT,
    uv_index INTEGER,
    wind FLOAT,
    visibility FLOAT,
    temp FLOAT
);

alter table api_data_weather
add constraint unique_date_time
unique (date_interested, time);
```

### 4. Настройка Apache Airflow

Для работы с проектом необходимо настроить Apache Airflow. Следуйте следующим шагам:

1. **Установите Airflow**: Используйте официальный гайд по установке [Airflow Installation Guide](https://airflow.apache.org/docs/apache-airflow/stable/installation.html).

2. **Настройте `airflow.cfg`**: Обновите конфигурационный файл Airflow, указав параметры подключения к базе данных PostgreSQL, например:

```ini
[core]
sql_alchemy_conn = postgresql+psycopg2://username:password@localhost:5432/weather_db
```

3. **Скопируйте DAG-файлы в папку Airflow**: Переместите файлы DAG (например, `dags/agregation_and_visualisation.py`) в директорию `dags` вашей установки Airflow.

### 5. Запуск Airflow

1. **Запустите веб-сервер Airflow**:

```bash
airflow webserver --port 8080
```

2. **Запустите планировщик Airflow**:

```bash
airflow scheduler
```

3. **Откройте веб-интерфейс Airflow**: Перейдите в браузере по адресу `http://localhost:8080`, активируйте ваш DAG и запустите его вручную, чтобы проверить, что все работает корректно.

## Структура проекта

- **dags/**: Содержит DAG-файлы, которые управляют последовательностью задач в Airflow.
- **scripts/**: Включает Python-скрипты для извлечения данных, агрегации, визуализации и записи в базу данных.
- **requirements.txt**: Список Python-зависимостей, необходимых для выполнения проекта.
- **README.md**: Этот файл с инструкциями.

## Использование

После того как DAG будет активирован и запущен в Airflow, следующие задачи будут выполнены автоматически:

1. **Сбор данных**: Взаимодействие с API для получения данных о погоде и их сохранение в базе данных PostgreSQL.
2. **Агрегация данных**: Расчет средних значений для различных параметров погоды, таких как температура, скорость ветра и т.д.
3. **Визуализация данных**: Построение графиков на основе агрегированных данных и сохранение их в виде изображений.
4. **Сохранение данных**: Запись агрегированных данных в отдельную таблицу PostgreSQL для последующего анализа.

Вы можете отслеживать выполнение задач, проверять логи и результаты через веб-интерфейс Apache Airflow.

