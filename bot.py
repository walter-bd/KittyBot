#!/usr/bin/env python

import os
import dotenv, aiohttp
import hikari, lightbulb
import emoji_cache
from chatterbotpro import ChatBot
from chatterbotpro import languages

dotenv.load_dotenv()

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    prefix="+",
    banner=None,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=tuple(int(v) for v in os.environ["DEFAULT_GUILDS"].split(','))
)


if not os.path.exists(os.environ.get('ChatBotDB', '/data/chatbot.sqlite3')):
    from chatterbotpro.trainers import ChatterBotCorpusTrainer
    # from chatterbotpro.trainers import ListTrainer
    kittychat = ChatBot('Kitty', 
                        storage_adapter='chatterbotpro.storage.SQLStorageAdapter',
                        database_uri='sqlite:///'+os.environ.get('ChatBotDB', '/data/chatbot.sqlite3'),
                        logic_adapters=[
                            'chatterbotpro.logic.BestMatch'
                        ],tagger_language=languages.ENG)
    # Create a new trainer for the chatbot
    trainer = ChatterBotCorpusTrainer(kittychat)

    # Train based on the english corpus
    trainer.train("chatterbot.corpus.english")

    # Train based on english greetings corpus
    trainer.train("chatterbot.corpus.english.greetings")

    # Train based on the english conversations corpus
    trainer.train("chatterbot.corpus.english.conversations")
    
    # Train on specifics
    # trainer.train([
    # 'Hello, how are you?',
    # 'I am doing well.',
    # 'That is good to hear.',
    # 'Thank you'
    # ]) 


@bot.listen(hikari.StartedEvent)
async def botStartup(event):
    print("Bot has started up!")
    await emoji_cache.cache_all_custom(bot)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong during invocation of command `{event.context.command.name}`.")
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(
            f"This command is on cooldown for you {event.context.author.mention}. Try again in `{exception.retry_after:.2f}` seconds.")


"""
Below creates 2 listeners, one for when the bot is starting, and one for when the bot is stopping. 
When the bot is starting, it creates a new aiohttp.ClientSession named aio_session and stores it in the bot.d data store. 
When the bot is stopping, it closes the aio_session.
"""


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.aio_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.aio_session.close()


bot.load_extensions_from("./extensions/", must_exist=True)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot.run()
