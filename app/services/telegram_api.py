import httpx
from app import config


class TelegramAPIError(RuntimeError):
    pass


class TelegramAPI:
    def __init__(self, token=None):
        self.token = token or config.BOT_TOKEN
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.client = httpx.AsyncClient(timeout=45)

    async def close(self):
        await self.client.aclose()

    async def call(self, method, data=None, files=None):
        r = await self.client.post(f"{self.base}/{method}", data=data, files=files)
        payload = r.json()
        if not payload.get("ok"):
            raise TelegramAPIError(f"{method}: {payload.get('description')}")
        return payload["result"]

    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None, entities=None):
        data = {"chat_id": chat_id, "text": text}
        if parse_mode is not None:
            data["parse_mode"] = parse_mode
        if entities is not None:
            data["entities"] = __import__("json").dumps(entities)
        if reply_markup is not None:
            data["reply_markup"] = __import__("json").dumps(reply_markup)
        return await self.call("sendMessage", data=data)

    async def send_video(self, chat_id, video, caption="", reply_markup=None, parse_mode=None, entities=None):
        data = {"chat_id": chat_id, "caption": caption}
        if parse_mode is not None:
            data["parse_mode"] = parse_mode
        if entities is not None:
            data["caption_entities"] = __import__("json").dumps(entities)
        if reply_markup is not None:
            data["reply_markup"] = __import__("json").dumps(reply_markup)
        if isinstance(video, str) and video.startswith("http"):
            data["video"] = video
            return await self.call("sendVideo", data=data)
        with open(video, "rb") as f:
            files = {"video": ("snap.mp4", f, "video/mp4")}
            return await self.call("sendVideo", data=data, files=files)

    async def edit_message_text(self, chat_id, message_id, text, reply_markup=None, parse_mode=None, entities=None):
        data = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if parse_mode is not None:
            data["parse_mode"] = parse_mode
        if entities is not None:
            data["entities"] = __import__("json").dumps(entities)
        if reply_markup is not None:
            data["reply_markup"] = __import__("json").dumps(reply_markup)
        return await self.call("editMessageText", data=data)

    async def edit_message_caption(self, chat_id, message_id, caption, reply_markup=None, parse_mode=None, entities=None):
        data = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if parse_mode is not None:
            data["parse_mode"] = parse_mode
        if entities is not None:
            data["caption_entities"] = __import__("json").dumps(entities)
        if reply_markup is not None:
            data["reply_markup"] = __import__("json").dumps(reply_markup)
        return await self.call("editMessageCaption", data=data)

    async def edit_reply_markup(self, chat_id, message_id, reply_markup):
        return await self.call("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": __import__("json").dumps(reply_markup),
        })

    async def answer_callback(self, callback_id, text=None):
        data = {"callback_query_id": callback_id}
        if text:
            data["text"] = text
        return await self.call("answerCallbackQuery", data=data)
