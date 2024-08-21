import os
import json
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
            cur.execute(
                """ 
                CREATE TABLE IF NOT EXISTS message_broker (
                    id SERIAL PRIMARY KEY,
                    message JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    picked_at TIMESTAMP,
                    deleted_at TIMESTAMP,
                    heartbeat TIMESTAMP,
                    receipt_handle UUID DEFAULT uuid_generate_v4()
                );
            """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_message_broker_heartbeat ON message_broker (heartbeat);"
            )
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
                data.append(
                    {
                        "id": row[0],
                        "message": row[1],
                        "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                        "picked_at": row[3],
                        "deleted_at": row[4],
                        "heartbeat": row[5],
                        "receipt_handle": row[6],
                    }
                )
        # Access the resource initialized during startup
    return JSONResponse(content={"data": data}, status_code=status.HTTP_200_OK)


@app.post("/message")
async def create_message(message: dict):
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO message_broker (message) VALUES (%s) RETURNING id;",
                (json.dumps(message),),
            )
            id = cur.fetchone()[0]
            cur.execute("SELECT * FROM message_broker WHERE id = %s;", (id,))
            receipt_id = cur.fetchone()[-1]
    return JSONResponse(
        content={
            "message": "Message created successfully",
            "reciept_handle": receipt_id,
        },
        status_code=status.HTTP_201_CREATED,
    )


@app.delete("/message/{receipt_handle}")
async def delete_message(receipt_handle: str):
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE message_broker SET deleted_at = CURRENT_TIMESTAMP WHERE receipt_handle = %s RETURNING id;",
                (receipt_handle,),
            )
            id = cur.fetchone()[0]
    return JSONResponse(
        content={"message": "Message deleted successfully", "id": id},
        status_code=status.HTTP_200_OK,
    )


@app.get("/message")
async def get_message():
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM message_broker WHERE deleted_at IS NULL AND picked_at IS NULL ORDER BY created_at ASC LIMIT 5 FOR UPDATE SKIP LOCKED;"
            )
            rows = cur.fetchall()
            for row in rows:
                print("inside")
                if row:
                    cur.execute(
                        "UPDATE message_broker SET picked_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING receipt_handle;",
                        (row[0],),
                    )
                    receipt_handle = cur.fetchone()[0]
                    return JSONResponse(
                        content={"message": row[1], "receipt_handle": receipt_handle},
                        status_code=status.HTTP_200_OK,
                    )
            else:
                return JSONResponse(
                    content={"message": "No message available"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )


if "__main__" == __name__:
    import uvicorn

    print(f"Starting Server at http://{os.getenv('HOST')}:{os.getenv('PORT')}")
    uvicorn.run("main:app", port=8080, reload=True, workers=4)
