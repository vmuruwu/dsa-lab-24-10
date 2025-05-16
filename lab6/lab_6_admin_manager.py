from fastapi import FastAPI, HTTPException, Request
import asyncpg
import logging

app = FastAPI()

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        existing = await conn.fetchrow(
            "SELECT * FROM admins WHERE chat_id = $1",
            chat_id
        )

        if existing:
            logger.warning(f"Попытка добавить существующего админа: {chat_id}")
            raise HTTPException(status_code=400, detail="Админ уже существует")

        await conn.execute(
            "INSERT INTO admins (chat_id) VALUES ($1)",
            chat_id
        )
        logger.info(f"Добавлен новый админ: {chat_id}")
        return {"status": "Админ добавлен"}

    except asyncpg.UniqueViolationError:
        logger.warning(f"Конфликт уникальности для chat_id: {chat_id}")
        raise HTTPException(status_code=400, detail="Админ уже существует")
    except Exception as e:
        logger.error(f"Ошибка при добавлении админа: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    finally:
        await conn.close()


@app.delete("/remove_admin/{chat_id}")
async def remove_admin(chat_id: str):
    conn = await get_db()
    try:
        existing = await conn.fetchrow(
            "SELECT * FROM admins WHERE chat_id = $1",
            chat_id
        )

        if not existing:
            logger.warning(f"Попытка удалить несуществующего админа: {chat_id}")
            raise HTTPException(status_code=404, detail="Админ не найден")

        await conn.execute(
            "DELETE FROM admins WHERE chat_id = $1",
            chat_id
        )
        logger.info(f"Удален админ: {chat_id}")
        return {"status": "Админ удалён"}

    except Exception as e:
        logger.error(f"Ошибка при удалении админа: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    finally:
        await conn.close()


@app.get("/is_admin/{chat_id}")
async def check_admin(chat_id: str):
    conn = await get_db()
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM admins WHERE chat_id = $1",
            chat_id
        )
        logger.debug(f"Проверка админа {chat_id}: {'найден' if exists else 'не найден'}")
        return {"is_admin": bool(exists)}
    except Exception as e:
        logger.error(f"Ошибка при проверке админа: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    finally:
        await conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("lab_6_admin_manager:app", host="0.0.0.0", port=5003)