from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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

@app.get("/convert")
async def convert_currency(currency_name: str, amount: float):
    name = currency_name.upper()
    conn = await get_db()
    try:
        row = await conn.fetchrow("SELECT rate FROM currencies WHERE currency_name=$1", name)
        if not row:
            raise HTTPException(status_code=404, detail="Валюта не найдена")
        rate = row['rate']
        converted = round(amount * float(rate), 2)
    finally:
        await conn.close()

    return JSONResponse(content={"converted_amount": converted})


@app.get("/currencies")
async def list_currencies():
    conn = await get_db()
    try:
        rows = await conn.fetch("SELECT currency_name, rate FROM currencies")
        result = [{"currency_name": r["currency_name"], "rate": float(r["rate"])} for r in rows]
    finally:
        await conn.close()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab_6_data_manager:app", port=5002)
