import os
import logging

import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение и краткая помощь."""
    text = (
        "Привет! Я калькулятор-бот.\n\n"
        "Доступные команды:\n"
        "/add a b – сложение\n"
        "/sub a b – вычитание\n"
        "/mul a b – умножение\n"
        "/div a b – деление\n\n"
        "Например:\n"
        "/add 2 3"
    )
    await update.message.reply_text(text)


async def _call_api(operation: str, a: float, b: float) -> float:
    """Вспомогательная функция: ходит в FastAPI-сервис."""
    url = f"{API_BASE_URL}/{operation}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(url, json={"a": a, "b": b})
        resp.raise_for_status()
        data = resp.json()
        return data["result"]


async def _parse_args(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Разбор аргументов команды /add 2 3 -> (2.0, 3.0) или сообщение об ошибке."""
    if len(context.args) != 2:
        await update.message.reply_text("Использование: /команда <a> <b>")
        return None, None

    try:
        a = float(context.args[0])
        b = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Аргументы <a> и <b> должны быть числами.")
        return None, None

    return a, b


async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    a, b = await _parse_args(update, context)
    if a is None:
        return

    try:
        result = await _call_api("add", a, b)
    except httpx.HTTPError as e:
        logger.exception("Ошибка при вызове API /add")
        await update.message.reply_text("⚠️ Ошибка сервера. Попробуйте позже.")
        return

    await update.message.reply_text(f"{a} + {b} = {result}")


async def sub_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    a, b = await _parse_args(update, context)
    if a is None:
        return

    try:
        result = await _call_api("sub", a, b)
    except httpx.HTTPError:
        logger.exception("Ошибка при вызове API /sub")
        await update.message.reply_text("⚠️ Ошибка сервера. Попробуйте позже.")
        return

    await update.message.reply_text(f"{a} - {b} = {result}")


async def mul_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    a, b = await _parse_args(update, context)
    if a is None:
        return

    try:
        result = await _call_api("mul", a, b)
    except httpx.HTTPError:
        logger.exception("Ошибка при вызове API /mul")
        await update.message.reply_text("⚠️ Ошибка сервера. Попробуйте позже.")
        return

    await update.message.reply_text(f"{a} * {b} = {result}")


async def div_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    a, b = await _parse_args(update, context)
    if a is None:
        return

    try:
        result = await _call_api("div", a, b)
    except httpx.HTTPStatusError as e:
        # здесь ловим 400 от FastAPI при делении на 0
        if e.response.status_code == 400:
            detail = e.response.json().get("detail", "Division error")
            await update.message.reply_text(f"Ошибка: {detail}")
        else:
            logger.exception("HTTP-ошибка при вызове API /div")
            await update.message.reply_text("⚠️ Ошибка сервера. Попробуйте позже.")
        return
    except httpx.HTTPError:
        logger.exception("Сетевая ошибка при вызове API /div")
        await update.message.reply_text("⚠️ Ошибка соединения с сервисом.")
        return

    await update.message.reply_text(f"{a} / {b} = {result}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Переменная окружения TELEGRAM_BOT_TOKEN не задана")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("sub", sub_cmd))
    app.add_handler(CommandHandler("mul", mul_cmd))
    app.add_handler(CommandHandler("div", div_cmd))

    logger.info("Бот запущен. Ожидаю сообщения...")
    app.run_polling()


if __name__ == "__main__":
    main()
