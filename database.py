import psycopg2
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def initConnection(username='app',
                   password='temptemp123',
                   hostname='localhost',
                   port='5432',
                   dbname='GroceryStore'):
    try:
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            dbname=dbname,
            user=username,
            password=password,
            client_encoding='utf-8',
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}")
        return None

def runQuery(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        return data, colnames

def getAllTables(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='grocery'")
        data = cursor.fetchall()
        tables = [row[0] for row in data]
        print(f"Debug: Tables found in grocery schema: {tables}")  # Debug output
        return tables

def getTableData(conn, tableName):
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM grocery."{tableName}"')
            data = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            logging.debug(f"Column names for {tableName}: {colnames}")
            return data, colnames
    except Exception as e:
        logging.error(f"Error getting table data for {tableName}: {str(e)}")
        return [], []

def addRecord(conn, tableName, keys, values):
    with conn.cursor() as cursor:
        try:
            placeholders = ', '.join(['%s'] * len(values))
            query = f'INSERT INTO grocery."{tableName}" {keys} VALUES ({placeholders})'
            cursor.execute(query, values)
            return None
        except psycopg2.Error as e:
            return f"Error adding record: {str(e)}"

def deleteRecord(conn, tableName, parameters):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f'DELETE FROM grocery."{tableName}" WHERE {parameters}')
            return None
        except psycopg2.Error as e:
            return f"Error deleting record: {str(e)}"

def getPrimaryKeys(conn, table_name):
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = 'grocery."{}"'::regclass AND i.indisprimary
            """.format(table_name)
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error getting primary keys for {table_name}: {str(e)}")
        return []

def updateRecord(conn, table_name, columns, values, whereClause, whereValues):
    try:
        with conn.cursor() as cursor:
            setClause = ', '.join(f'"{col}" = %s' for col in columns)
            query = f'UPDATE grocery."{table_name}" SET {setClause} WHERE {whereClause}'
            logging.debug(f"Executing update query: {query}")
            logging.debug(f"Parameters: values={values}, whereValues={whereValues}")
            cursor.execute(query, values + whereValues)
            if cursor.rowcount == 0:
                logging.warning(f"No rows updated for table {table_name}")
                return "No rows matched the update condition", 0
            conn.commit()
            logging.debug(f"Updated {cursor.rowcount} rows")
            return None, cursor.rowcount
    except Exception as e:
        logging.error(f"Error updating record: {str(e)}")
        return str(e), 0

def getTables(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'grocery'")
            tables = [row[0] for row in cursor.fetchall()]
            logging.debug(f"Retrieved tables: {tables}")
            return tables
    except Exception as e:
        logging.error(f"Error getting tables: {str(e)}")
        return []

def createTable(conn, tableName, columns):
    with conn.cursor() as cursor:
        try:
            # Ensure columns is a list of (name, type) tuples
            columns_def = ", ".join([f'"{col[0]}" {col[1]}' for col in columns])
            cursor.execute(f'CREATE TABLE grocery."{tableName}" ({columns_def})')
            logging.info(f"Table '{tableName}' created successfully")
            return None
        except psycopg2.Error as e:
            logging.error(f"Error creating table '{tableName}': {str(e)}")
            return f"Failed to create table: {str(e)}"

def dropTable(conn, tableName):
    with conn.cursor() as cursor:
        try:
            # Create a backup before dropping
            backupTable(conn, tableName)
            # Execute DROP TABLE with CASCADE to handle dependencies
            cursor.execute(f'DROP TABLE grocery."{tableName}" CASCADE')
            logging.info(f"Table '{tableName}' dropped successfully")
            return None
        except psycopg2.Error as e:
            logging.error(f"Error dropping table '{tableName}': {str(e)}")
            return f"Failed to drop table: {str(e)}"

def addColumn(conn, table_name, column_name, column_type):
    try:
        with conn.cursor() as cursor:
            query = f'ALTER TABLE grocery."{table_name}" ADD COLUMN "{column_name}" {column_type}'
            logging.debug(f"Executing query: {query}")
            cursor.execute(query)
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding column: {str(e)}")
        return str(e)
    return None

def dropColumn(conn, tableName, columnName):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f'ALTER TABLE grocery."{tableName}" DROP COLUMN {columnName}')
            return None
        except psycopg2.Error as e:
            return f"Error dropping column: {str(e)}"

def renameColumn(conn, tableName, oldName, newName):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f'ALTER TABLE grocery."{tableName}" RENAME COLUMN "{oldName}" TO "{newName}"')
            return None
        except psycopg2.Error as e:
            return f"Error renaming column: {str(e)}"

def changeColumnType(conn, tableName, columnName, newType):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f'ALTER TABLE grocery."{tableName}" ALTER COLUMN "{columnName}" TYPE {newType}')
            return None
        except psycopg2.Error as e:
            return f"Error changing column type: {str(e)}"

def renameTable(conn, oldName, newName):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f'ALTER TABLE grocery."{oldName}" RENAME TO "{newName}"')
            return None
        except psycopg2.Error as e:
            return f"Error renaming table: {str(e)}"

def backupTable(conn, tableName):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    filename = f"{backup_dir}/{tableName}_{timestamp}.sql"

    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_schema = 'grocery' AND table_name = '{tableName}'"
        )
        columns = cursor.fetchall()
        columns_def = ", ".join([f'"{col[0]}" {col[1]}' for col in columns])

        data, colnames = getTableData(conn, tableName)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'DROP TABLE IF EXISTS grocery."{tableName}" CASCADE;\n')
            f.write(f'CREATE TABLE grocery."{tableName}" ({columns_def});\n')
            if data:
                quoted_cols = ','.join(f'"{col}"' for col in colnames)
                values = [
                    "(" + ", ".join(
                        [cursor.mogrify('%s', (val,)).decode() if val is not None else 'NULL' for val in row]
                    ) + ")"
                    for row in data
                ]
                insert_stmt = f'INSERT INTO grocery."{tableName}" ({quoted_cols}) VALUES\n' + ",\n".join(values) + ";"
                f.write(insert_stmt + "\n")

    return filename

def backupDatabase(conn, tableName=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    def write_backup(cursor, table, filepath):
        cursor.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_schema = 'grocery' AND table_name = '{table}'"
        )
        columns = cursor.fetchall()
        columns_def = ", ".join([f'"{col[0]}" {col[1]}' for col in columns])

        data, colnames = getTableData(conn, table)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'DROP TABLE IF EXISTS grocery."{table}" CASCADE;\n')
            f.write(f'CREATE TABLE grocery."{table}" ({columns_def});\n')
            if data:
                quoted_cols = ','.join(f'"{col}"' for col in colnames)
                values = [
                    "(" + ", ".join(
                        [cursor.mogrify('%s', (val,)).decode() if val is not None else 'NULL' for val in row]
                    ) + ")"
                    for row in data
                ]
                insert_stmt = f'INSERT INTO grocery."{table}" ({quoted_cols}) VALUES\n' + ",\n".join(values) + ";"
                f.write(insert_stmt + "\n")

    with conn.cursor() as cursor:
        if tableName:
            filename = f"{backup_dir}/{tableName}.sql"
            write_backup(cursor, tableName, filename)
            return filename
        else:
            tables = getAllTables(conn)
            for table in tables:
                filepath = f"{backup_dir}/{table}.sql"
                write_backup(cursor, table, filepath)
            return backup_dir

def restoreTable(conn, tableName, backup_file):
    try:
        with conn.cursor() as cursor:
            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.execute(sql_script)
            return None
    except psycopg2.Error as e:
        return f"Error restoring table: {str(e)}"
    except Exception as e:
        return f"Error reading backup file: {str(e)}"

def restoreDatabase(conn, backup_dir):
    try:
        with conn.cursor() as cursor:
            tables = getAllTables(conn)
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS grocery."{table}" CASCADE;')

            for filename in sorted(os.listdir(backup_dir)):
                if filename.endswith('.sql'):
                    with open(os.path.join(backup_dir, filename), 'r', encoding='utf-8') as f:
                        sql_script = f.read()
                        cursor.execute(sql_script)
            return None
    except psycopg2.Error as e:
        return f"Error restoring database: {str(e)}"
    except Exception as e:
        return f"Error reading backup directory: {str(e)}"

def exportToCSV(data, colnames, filename):
    import csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(data)

def getColumnInfo(conn, tableName):
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_schema = 'grocery' AND table_name = '{tableName}'"
        )
        return cursor.fetchall()