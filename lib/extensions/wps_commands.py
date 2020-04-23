from discord.ext import commands
from discord import Embed
from asyncio import sleep, Queue
from time import time
import random

WORDS = open("/usr/share/dict/words_alpha.txt").read().split("\n")
test_length = 10


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

    @property
    def wpm(self):
        return int(self.words_typed / test_length * 60)

    @property
    def words_typed(self):
        return len(self.received_words)

    @property
    def percent_correct(self):
        return int(self.words_correct / self.words_typed * 100)

    @property
    def words_correct(self):
        correct = 0
        for expected, received in zip(self.expected_words, self.received_words):
            if expected == received:
                correct += 1

        return correct


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
            if time_elapsed > test_length:
                break

        await ctx.send("Times up!!")

        description = f"**Words Typed**: {w.words_typed}\n" \
                      f"**Words Correct**: {w.words_correct}\n" \
                      f"**Percent Correct**: {w.percent_correct}%\n" \
                      f"**Time Elapsed**: {test_length}\n"\
                      f"**Words Per Minute**: {w.wpm}\n"
        e = Embed(
            title="Results",
            description=description,
            Color=0x1111AA
        )

        await ctx.send("", embed=e)

    @commands.Cog.listener()
    async def on_message(self, message):
        q = self.message_counters.get(message.author.id, None)
        if not q:
            return

        await q.put(message.content)



def setup(bot):
    bot.add_cog(WPSCog(bot))
