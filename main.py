import logging
import os

from dotenv import load_dotenv

from polyduckai.bot import build_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    load_dotenv()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = build_app(token)
    app.run_polling()


if __name__ == "__main__":
    main()
