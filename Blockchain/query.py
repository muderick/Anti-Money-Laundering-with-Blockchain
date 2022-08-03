import sqlite3

sqliteConnection = sqlite3.connect('Blockchain\database.db')
db = sqliteConnection
# def readSqliteTable():
#     try:
#         sqliteConnection
#         cursor = db.cursor()
#         print("Connected to SQLite")

#         sqlite_select_query = """SELECT amount, id from transactions"""
#         cursor.execute(sqlite_select_query)
#         records = cursor.fetchall()
#         print("Total amount transaction are:  ", len(records))
#         print(records)

#         cursor.close()

#     except sqlite3.Error as error:
#         print("Failed to read data from sqlite table", error)
#     finally:
#         if sqliteConnection:
#             sqliteConnection.close()
#             print("The SQLite connection is closed")

# readSqliteTable()

def alterSqliteTable():
    try:
        sqliteConnection
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        query = """ALTER TABLE bminers ADD miner_name VARCHAR(50) AFTER id"""
        cursor.execute(query)
        db.commit()
        results = cursor.fetchall()
        for row in results:
            print(row)

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to alter data in the sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

alterSqliteTable()


# def deleteRecord():
#     try:
#         sqliteConnection
#         cursor = sqliteConnection.cursor()
#         print("Connected to Database")

#         # Deleting single record now
#         sql_delete_query = """DELETE from transactions where id = """
#         cursor.execute(sql_delete_query)
#         sqliteConnection.commit()
#         print("Record deleted successfully ")
#         cursor.close()

#     except sqlite3.Error as error:
#         print("Failed to delete record from sqlite table", error)
#     finally:
#         if sqliteConnection:
#             sqliteConnection.close()
#             print("the sqlite connection is closed")