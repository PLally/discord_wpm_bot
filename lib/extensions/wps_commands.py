from discord.ext import commands
from asyncio import sleep, Queue
from time import time
import random

WORDS = open("words_alpha.txt").read().split("\n")


async def countdown(messageable, seconds):
    while seconds > 0:
        await messageable.send(str(seconds)+"...")
        await sleep(1)
        seconds -= 1
    await messageable.send("Start!")
    await sleep(1)


class WordCounter(Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_words = []
        self.received_words = []
        self.current_word = None

    def next_word(self):
        word = random.choice(WORDS)
        self.current_word = word
        return word

    async def put(self, word):
        self.expected_words.append(self.current_word)
        self.received_words.append(word)
        return await super().put(word)


class WPSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counters = {}

    @commands.command(name="wps")
    async def wps_command(self, ctx):
        await ctx.send("Starting in 10 seconds.\nType the words sent to you by the bot")
        await sleep(5)
        await countdown(ctx, 5)
        w = WordCounter()
        self.message_counters[ctx.author.id] = w

        start = time()
        await ctx.send(w.next_word())
        while True:
            if w.empty():
                await sleep(0.01)
            else:
                _ = await w.get()
                word = w.next_word()
                await ctx.send(word)

            time_elapsed = time() - start
            if time_elapsed > 10:
                break

        await ctx.send("Times up!!")

        await ctx.send("Expected: "+str(w.expected_words))
        await ctx.send("Received: "+str(w.received_words))

    @commands.Cog.listener()
    async def on_message(self, message):
        q = self.message_counters.get(message.author.id, None)
        if not q:
            return

        await q.put(message.content)



def setup(bot):
    bot.add_cog(WPSCog(bot))
