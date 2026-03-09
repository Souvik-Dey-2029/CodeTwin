from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

def check_table(table_name):
    print(f"\n--- Columns in '{table_name}' ---")
    columns = inspector.get_columns(table_name)
    for column in columns:
        print(f"Name: {column['name']}, Type: {column['type']}")

if "analysis_runs" in inspector.get_table_names():
    check_table("analysis_runs")
if "repositories" in inspector.get_table_names():
    check_table("repositories")
