import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .ai_client import ChatSession, Model

logger = logging.getLogger(__name__)

MODEL_LABELS: dict[Model, str] = {
    Model.GEMINI_FLASH: "Gemini 2.0 Flash",
    Model.DEEPSEEK: "DeepSeek V3",
    Model.LLAMA: "Llama 3.3 70B",
    Model.QWEN: "Qwen 2.5 72B",
    Model.MISTRAL: "Mistral Small",
}

# {user_id: ChatSession}
_sessions: dict[int, ChatSession] = {}


async def _get_session(user_id: int) -> ChatSession:
    if user_id not in _sessions:
        session = ChatSession()
        await session.start()
        _sessions[user_id] = session
    return _sessions[user_id]


async def _replace_session(user_id: int, model: Model) -> ChatSession:
    if user_id in _sessions:
        await _sessions.pop(user_id).close()
    session = ChatSession(model=model)
    await session.start()
    _sessions[user_id] = session
    return session


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! I'm Poly 🦆\n\n"
        "I give you free access to multiple AI models.\n\n"
        "Just send me a message to start chatting.\n\n"
        "/new — fresh conversation\n"
        "/model — switch AI model\n"
        "/help — show this message"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)


async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session = await _get_session(user_id)
    session.reset()
    await update.message.reply_text("Done — fresh conversation started.")


async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"model:{model.value}")]
        for model, label in MODEL_LABELS.items()
    ]
    await update.message.reply_text(
        "Choose a model:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def on_model_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    model_value = query.data.split(":", 1)[1]
    model = Model(model_value)
    await _replace_session(update.effective_user.id, model)
    await query.edit_message_text(
        f"Switched to {MODEL_LABELS[model]}. Conversation reset."
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        session = await _get_session(user_id)
        reply = await session.chat(text)
        await update.message.reply_text(reply)
    except Exception:
        logger.exception("Error handling message for user %d", user_id)
        await update.message.reply_text(
            "Something went wrong talking to the AI service. Try /new to reset."
        )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error", exc_info=context.error)


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CallbackQueryHandler(on_model_select, pattern=r"^model:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_error_handler(on_error)
    return app
