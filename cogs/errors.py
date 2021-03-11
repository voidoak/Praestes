import discord
from discord.ext import commands

def ignorable(error):
    """used to ignore certain errors that are unimportant to both users and devs"""
    ignored_errors = [
        commands.CommandNotFound, commands.NotOwner,
        discord.ConnectionClosed, commands.CheckFailure
    ]

    for ignored in ignored_errors:
        if isinstance(error, ignored):
            return True

class Errors(commands.Cog):
    def __init__(self, client):
        """error handling cog"""
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ignorable(error):
            return

        cause = error.__cause__
        embed = discord.Embed()

        if isinstance(cause, discord.Forbidden):
            embed.description = "```diff\n- I don't have permission to do that, either due to the role hierarchy or my lack of relevant perms.\n```"       
        else:
            embed.description = f"```diff\n- {error.__class__.__name__}: {error}\n```"

        await ctx.reply(embed=embed)


def setup(client):
    client.add_cog(Errors(client))
