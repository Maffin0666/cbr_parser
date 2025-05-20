import psycopg2

try:
    conn = psycopg2.connect(
        dbname="cbr_data",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432"
    )
    print("✅ Подключение к PostgreSQL успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")