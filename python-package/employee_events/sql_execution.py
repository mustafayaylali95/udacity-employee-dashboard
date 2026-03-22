from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Using pathlib, create a `db_path` variable
# that points to the absolute path for the `employee_events.db` file
# Dosyanın bulunduğu klasörü alıp, veritabanı adıyla birleştiriyoruz
db_path = Path(__file__).resolve().parent / "employee_events.db"

# OPTION 1: MIXIN
# Define a class called `QueryMixin`


class QueryMixin:

    # Define a method named `pandas_query`
    # that receives an sql query as a string
    # and returns the query's result
    # as a pandas dataframe
    def pandas_query(self, query_string):
        """Veritabanına bağlanır, SQL sorgusunu çalıştırır ve Pandas DataFrame döndürür."""
        connection = connect(db_path)
        df = pd.read_sql_query(query_string, connection)
        connection.close()
        return df

    # Define a method named `query`
    # that receives an sql_query as a string
    # and returns the query's result as
    # a list of tuples. (You will need
    # to use an sqlite3 cursor)
    def query(self, query_string):
        """Veritabanına bağlanır, SQL sorgusunu çalıştırır ve Tuple listesi döndürür."""
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query
