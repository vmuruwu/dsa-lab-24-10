from fastapi import FastAPI, HTTPException, Request
import asyncpg

app = FastAPI()

async def get_db():
    return await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='tg_bot_vt',
        host='localhost',
        port=5432
    )

@app.post("/add_admin")
async def add_admin(request: Request):
    data = await request.json()
    chat_id = data['chat_id']

    conn = await get_db()
    try:
        await conn.execute("INSERT INTO admins (chat_id) VALUES ($1)", chat_id)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Админ уже существует")
    finally:
        await conn.close()

    return {"status": "Админ добавлен"}

@app.delete("/remove_admin/{chat_id}")
async def remove_admin(chat_id: str):
    conn = await get_db()
    try:
        result = await conn.execute("DELETE FROM admins WHERE chat_id = $1", chat_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Админ не найден")
    finally:
        await conn.close()

    return {"status": "Админ удалён"}

@app.get("/is_admin/{chat_id}")
async def check_admin(chat_id: str):
    conn = await get_db()
    try:
        exists = await conn.fetchval("SELECT 1 FROM admins WHERE chat_id = $1", chat_id)
    finally:
        await conn.close()

    return {"is_admin": bool(exists)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab_6_admin_manager:app", port=5003)