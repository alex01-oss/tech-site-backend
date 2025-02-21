import psycopg2

try:
    conn = psycopg2.connect(
        dbname="construction",
        user="postgres",
        password="admin",
        host="localhost",
        client_encoding="UTF8"  # Додаємо це для явного вказування кодування
    )
    print("Connected successfully!")

    cursor = conn.cursor()

    query = "SELECT * FROM your_table_name LIMIT 10;"  # Замінити на ім'я вашої таблиці
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        rows = cursor.fetchall()
    for row in rows:
        print([cell.decode('utf-8', 'replace') if isinstance(cell, bytes) else cell for cell in row])


    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e)}")
