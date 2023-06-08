import snowflake.connector
import json

# QUERY_ITERATIONS is the number of query iterations to be performed
QUERY_ITERATIONS = 10

# init_external_function creates an external function


def init_external_function(conn, databaseName, apiIntegrationName, invocationURL):
    try:

        conn.cursor().execute(f"USE DATABASE {databaseName}")
        query = f"""
        create or replace external function skyflow_snowflake_detokenization(value string)
        returns variant
        RETURNS NULL ON NULL INPUT
        api_integration = {apiIntegrationName}
         headers = ('method'='detokenize')
         MAX_BATCH_ROWS = 100
         as '{invocationURL}'
         ;
         """

        conn.cursor().execute(query)

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error creating external function: {e}")

# get_external_function_last_query_avg_latency gets the average latency of the last query


def get_external_function_last_query_avg_latency(conn, count, key):

    try:
        queryProfileQuery = "SELECT OPERATOR_STATISTICS:external_functions FROM TABLE(GET_QUERY_OPERATOR_STATS(LAST_QUERY_ID()))"
        queryProfileCursor = conn.cursor()
        queryProfileCursor.execute(queryProfileQuery)
        queryProfile = queryProfileCursor.fetchall()
        queryProfileTup = queryProfile[1]
        res = json.loads(queryProfileTup[0])
        if len(res) < 2:
            raise ValueError(
                "Query profile did not return expected number of rows")
        if "rows_received" or "average_latency" not in res:
            raise ValueError("Expected keys missing from query profile")
        if res["rows_received"] != count:
            raise ValueError(
                f"Number of rows received are not equal to number of rows present in column: {key}")
        else:
            return res["average_latency"]

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error running benchmark: {e}")


# external_function_snowflake performs detokenization benchmarking


def benchmark(conn, tableName):

    columnLatencyValues = {key: [] for key in [
        'first_name', 'last_name', 'email_id', 'ssn', 'card_number']}

    try:

        for key in columnLatencyValues:
            queryCountQuery = f"select count({key}) from {tableName};"
            queryCountCursor = conn.cursor()
            queryCountCursor.execute(queryCountQuery)
            queryCountProfile = queryCountCursor.fetchall()
            count = queryCountProfile[0][0]

            LatencySum = 0

            for i in range(QUERY_ITERATIONS):
                query = f"select skyflow_snowflake_detokenization({key}), {key} from {tableName};"
                conn.cursor().execute(query)
                average_latency = get_external_function_last_query_avg_latency(
                    conn, count, key)

                LatencySum = LatencySum + average_latency

            columnLatencyValues[key] = LatencySum/QUERY_ITERATIONS

        # in millisec
        print("The average latency for detokenizing the First Name (TokenFormat_DETERMINISTIC_UUID) is ",
              columnLatencyValues['first_name'])
        print("The average latency for detokenizing the Last Name (TokenFormat_NON_DETERMINISTIC_UUID) is ",
              columnLatencyValues['last_name'])
        print("The average latency for detokenizing the Email ID Email Id (TokenFormat_DETERMINISTIC_FPT) is ",
              columnLatencyValues['email_id'])
        print("The average latency for detokenizing the SSN (TokenFormat_NON_DETERMINISTIC_FPT) is ",
              columnLatencyValues['ssn'])
        print("The average latency for detokenizing the Card Number (TokenFormat_DETERMINISTIC_PRESERVE_LEFT_6_RIGHT_4) is ",
              columnLatencyValues['card_number'])

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error running benchmark: {e}")

    except Exception as error:
        print(f"An error occurred: {error}")
