import discord, base64
from discord.ext import commands
from random import randint


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.encodings = ["b16", "b32", "b64", "b85"]

    def cog_check(self, ctx):
        return not ctx.guild is None

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def say(self, ctx, *, message:str):
        """ safely make the bot repeat what you say """
        embed = discord.Embed(description=message, colour=ctx.author.top_role.colour)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["clr", "color"])
    async def colour(self, ctx, clr:discord.Colour=None):
        """ see a passed in colour or leave blank for a random colour """
        clr = clr or discord.Colour.random()
        embed = discord.Embed(title=str(clr), colour=clr, url=f"http://google.com/search?q={str(clr).replace('#', '%23')}&tbm=isch")
        await ctx.send(embed=embed)

    @commands.command(aliases=["roll"])
    async def dice(self, ctx, _type:str):
        """ roll dice """
        if _type.count("d") != 1:
            return await ctx.reply(f"The type of and amount of dice should be in this format: `nds`," \
            "where `n` is the amount of dice you'd like to roll, and `s` is the amount of sides for the dice." \
            "An example would be `3d10`, which is rolling 3 10 sided dice.")
        if len((dice:=tuple(_type.split("d")))) != 2:
            return await ctx.reply(f"Incorrect formatting of dice: `{_type}`.")

        try:
            amount, sides = (int(i) for i in dice)
        except:
            return await ctx.reply("Both the amount of dice and sides must be whole integers.")

        if not amount >= 1:
            return await ctx.reply("At least one die is required to run this command.")
        elif amount > 20:
            return await ctx.reply("Maximum 20 dice to run this command.")

        if not sides >= 4:
            return await ctx.reply("Minimum die side count is 4.")
        elif sides > 100:
            return await ctx.reply("Maximum die side count is 20.")

        rolled_score = sum(randint(1, sides) for i in range(amount))
        embed = discord.Embed(title=f"Rolled {_type} :game_die:", colour=discord.Colour.random())
        embed.description = f"You roll {_type}, and got **{rolled_score}**."
        await ctx.reply(embed=embed)

    @commands.command(name="encode", aliases=["enc"])
    async def str_to_encoding(self, ctx, encoding:str, *, _input:str):
        """ encode a passed in string to encodings b16, b32, b64, or b85 """
        output = self.enc_or_dec("encode", encoding, _input)
        embed = discord.Embed(title=f"Encoded input to {encoding}")
        embed.description = f"```\n{output}\n```"
        await ctx.reply(embed=embed)

    @commands.command(name="decode", aliases=["dec"])
    async def encoding_to_str(self, ctx, encoding:str, *, _input:str):
        """ decode a string from an encoding of either b16, b32, b64, or b85 """
        output = self.enc_or_dec("decode", encoding, _input)
        embed = discord.Embed(title=f"Decoded {encoding} input to utf-8")
        embed.description = f"```\n{output}\n```"
        await ctx.reply(embed=embed)

    def enc_or_dec(self, conversion_type, encoding, _input):
        """ handle encoding/decoding """
        if encoding not in self.encodings:
            raise commands.BadArgument(f"improper encoding for {ctx.command.name} command: {encoding}")

        converter = getattr(base64, f"{encoding}{conversion_type}")  # get either encoding or decoding function attr
        output = str(converter(bytes(_input, "utf-8")))[2:-1]  # get rid of b' ' in output

        if len(output) > 1996:  # keep within discord content size bounds
            raise commands.BadArgument("Input must be between 1 and 1996 characters, inclusive.")

        return output


def setup(client):
    client.add_cog(Utility(client))
