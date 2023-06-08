import snowflake.connector
import os

# FILE_PATH is the relative file path of the generated snowflake_benchmark_testing.csv which is constant
FILE_PATH = 'snowflake_benchmark_testing.csv'

# insert_snowflake inserts the tokens into the newly created table in snowflake


def insert_snowflake(conn, databaseName, tableName):

    # csvFilepath is the path of the csv file containing the tokens that have to be copied into Snowflake
    csvFilePath = os.path.abspath(FILE_PATH)

    # Create database, table and copy csv data into table
    try:
        conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")
        conn.cursor().execute(f"USE DATABASE {databaseName}")
        conn.cursor().execute(
            "CREATE OR REPLACE TABLE "
            f"{tableName}(first_name string, last_name string, email_id string, ssn string, card_number string)")
        conn.cursor().execute(
            "CREATE OR REPLACE STAGE snowflake_benchmark_testing COPY_OPTIONS = (ON_ERROR='continue')")
        put_file = f"PUT file://{csvFilePath} @snowflake_benchmark_testing"
        conn.cursor().execute(put_file)
        conn.cursor().execute(
            f"COPY INTO {tableName} FROM @snowflake_benchmark_testing")
        print("finished inserting tokens into Snowflake")

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error creating database: {e}")

    if os.path.exists(csvFilePath):
        os.remove(csvFilePath)
