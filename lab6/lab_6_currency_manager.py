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

@app.post("/load")
async def load_currency(request: Request):
    data = await request.json()
    name = data['currency_name'].upper()
    rate = data['rate']

    conn = await get_db()
    try:
        existing = await conn.fetchrow("SELECT * FROM currencies WHERE currency_name=$1", name)
        if existing:
            raise HTTPException(status_code=400, detail="Currency already exists")
        await conn.execute("INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)", name, rate)
    finally:
        await conn.close()

    return {"Статус": "Валюта добавлена"}

@app.post("/update_currency")
async def update_currency(request: Request):
    data = await request.json()
    name = data['currency_name'].upper()
    rate = data['rate']

    conn = await get_db()
    try:
        existing = await conn.fetchrow("SELECT * FROM currencies WHERE currency_name=$1", name)
        if not existing:
            raise HTTPException(status_code=404, detail="Валюта не найдена")
        await conn.execute("UPDATE currencies SET rate=$1 WHERE currency_name=$2", rate, name)
    finally:
        await conn.close()

    return {"Статус": "Курс валюты обновлён"}

@app.post("/delete")
async def delete_currency(request: Request):
    data = await request.json()
    name = data['currency_name'].upper()

    conn = await get_db()
    try:
        existing = await conn.fetchrow("SELECT * FROM currencies WHERE currency_name=$1", name)
        if not existing:
            raise HTTPException(status_code=404, detail="Валюта не найдена")
        await conn.execute("DELETE FROM currencies WHERE currency_name=$1", name)
    finally:
        await conn.close()

    return {"Статус": "Валюта удалена"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab_6_currency_manager:app", port=5001)
