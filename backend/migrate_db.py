from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as conn:
        print("Adding columns to analysis_runs...")
        try:
            conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN graph_data JSON"))
            print("Added graph_data")
        except Exception as e:
            print(f"Error adding graph_data: {e}")
            
        try:
            conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN heatmap_data JSON"))
            print("Added heatmap_data")
        except Exception as e:
            print(f"Error adding heatmap_data: {e}")
            
        try:
            conn.execute(text("ALTER TABLE analysis_runs ADD COLUMN refactor_data JSON"))
            print("Added refactor_data")
        except Exception as e:
            print(f"Error adding refactor_data: {e}")
        
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    run_migration()
