```python
import telegram
import asyncio

"""
pip install python-telegram-bot
"""

key = ""
chat_id = ""
text = ""

async def sendMsg(text):
    bot = telegram.Bot(token=key)
    async with bot:
        print(await bot.send_message(chat_id=chat_id, text = text))

# loop = asyncio.get_event_loop()
# loop.create_task(sendMsg(text))
asyncio.run(sendMsg(text))
```

[telegram-bot文档](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html#telegram.Bot.send_message)