import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import status
from contextlib import asynccontextmanager
from db import Database
db = None
@asynccontextmanager
async def lifespan(app: FastAPI):

    global db
    print("Starting up...")
    db = Database()
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # cur.execute("""SELECT EXISTS (
            #     SELECT 1
            #     FROM pg_catalog.pg_tables
            #     WHERE schemaname = 'public'
            #     AND tablename = 'your_table_name'
            # );"""
            # )
            # is_table_exists, = cur.fetchone()
            # if is_table_exists:
                # pass
            cur.execute("BEGIN;")
            cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS message_broker (
                    id SERIAL PRIMARY KEY,
                    message JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    picked_at TIMESTAMP,
                    deleted_at TIMESTAMP,
                    heartbeat TIMESTAMP,
                    receipt_handle UUID DEFAULT uuid_generate_v4()
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_message_broker_heartbeat ON message_broker (heartbeat);")
            cur.execute("COMMIT;")
                
    app.state.my_resource = "Some resource"
    
    yield  # The application is running at this point
    
    # Shutdown logic here (e.g., close database connections)
    print("Shutting down...")
    db.close_all_connections()
    # Example: Clean up the resource
    del app.state.my_resource

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_all_messages():
    data = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # cur.execute("SELECT * from students ")
            cur.execute("""SELECT * FROM message_broker;""")
            all_rows = cur.fetchall()
            for row in all_rows:
                data.append({
                    "id" : row[0],
                    "message" : row[1],
                    "created_at" : row[2].strftime("%Y-%m-%d %H:%M:%S"),
                    "picked_at" : row[3],
                    "deleted_at" : row[4],
                    "heartbeat" : row[5],
                    "receipt_handle" : row[6]
                })
        # Access the resource initialized during startup
    return JSONResponse(content={"data" : data}, status_code=status.HTTP_200_OK)


if "__main__" == __name__ : 
    import uvicorn
    print(f"Starting Server at http://{os.getenv('HOST')}:{os.getenv('PORT')}")
    uvicorn.run("main:app",port=8080,reload=True)
