import asyncio
import os

from dotenv import load_dotenv
from pyrogram import Client


load_dotenv()


async def create_session() -> None:
    api_id = os.getenv("API_ID", "").strip()
    api_hash = os.getenv("API_HASH", "").strip()
    phone_number = os.getenv("PHONE_NUMBER", "").strip() or os.getenv("TG_PHONE_NUMBER", "").strip()

    if not api_id:
        api_id = input("API_ID: ").strip()
    if not api_hash:
        api_hash = input("API_HASH: ").strip()
    if not phone_number:
        phone_number = input("Phone number (international format): ").strip()

    if not api_id or not api_hash or not phone_number:
        raise ValueError("API_ID, API_HASH, and phone number are required.")

    session_name = os.getenv("SESSION_NAME", "vth_music_bot")

    async with Client(session_name, api_id=int(api_id), api_hash=api_hash, in_memory=False) as app:
        sent_code = await app.send_code(phone_number)
        print("\nA login code has been sent to your Telegram account.")
        code = input("Enter the login code: ").strip()

        if getattr(sent_code, "phone_code_hash", None):
            await app.sign_in(
                phone_number=phone_number,
                phone_code_hash=sent_code.phone_code_hash,
                phone_code=code,
            )
        else:
            await app.sign_in(phone_number=phone_number, phone_code=code)

        session_string = await app.export_session_string()
        print(f"\nSTRING_SESSION={session_string}")
        print("\nAdd this value to your .env file.")


if __name__ == "__main__":
    try:
        asyncio.run(create_session())
    except KeyboardInterrupt:
        print("\nSession generation cancelled.")
    except Exception as exc:
        print(f"\nError: {exc}")
        raise SystemExit(1)
