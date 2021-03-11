import discord
from discord.ext import commands
import utils

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # on cog reload, these attributes are lost; as such,
        # reinitialize them on first message after the reload.
        if not getattr(self, "visible_cogs", None) is None:
            return
        self.visible_cogs = { k:[] for k in ["info", "moderation", "utility"] }
        for cmd in self.client.commands:  # get all commands and pass into cog
            cog = cmd.cog_name
            if cog:
                if (cog:=cog.lower()) in self.visible_cogs.keys():
                    self.visible_cogs[cog].append(cmd)

        for cog in self.visible_cogs.keys():  # sort cog by command names
            self.visible_cogs[cog] = sorted(
                self.visible_cogs[cog], key=(lambda c: c.name)
            )

    @commands.command()
    async def help(self, ctx, *, cmd_or_cog:str="default"):
        """ display the help embed """
        # separate cog/command embed configuration
        cmd_or_cog = cmd_or_cog.lower()
        if (cog:=cmd_or_cog) in self.visible_cogs.keys():
            embed = self.generate_cog_embed(cog)
        elif cmd:=self.get_command(cmd_or_cog):
            embed = self.generate_command_embed(cmd)
        else:
            message = "\n\n".join(f"{cog}: {len(cmds)} commands" for cog, cmds in self.visible_cogs.items())

            embed = discord.Embed(description = f"```yaml\n---\n{message}\n---\n```")
            embed.set_author(**utils.requested(ctx))
            embed.set_footer(text="Run help [cog] to get a list of commands in a cog")

        embed.set_author(**utils.requested(ctx))
        return await ctx.send(embed=embed)

    def generate_command_embed(self, cmd):
        """ generates informatic embed for given command """
        description = \
        f"name: {cmd.name}\ncog: {cmd.cog_name}\ndescription:\n {cmd.short_doc}\n\n" \
        f"aliases:\n  - {', '.join(cmd.aliases) if cmd.aliases else 'None'}\n" + \
        f"\nusage: {cmd.name} {cmd.signature}"

        embed = discord.Embed(title="Command info")
        embed.description = f"```yaml\n---\n{description}\n---\n```"
        embed.set_footer(text="[optional], <required>, = denotes default value")
        return embed

    def generate_cog_embed(self, cog):
        """ generates informatic embed for given cog """
        commands = "\n-\n".join(f"{cmd.name}: {cmd.help}" for cmd in self.visible_cogs[cog])
        embed = discord.Embed(title="Cog info")
        embed.description = f"```yaml\n---\n{commands}\n---\n```"
        embed.set_footer(text="Run help [command] to learn more about a command")
        return embed

    def get_command(self, command:str):
        """ Returns a Command object, based on string. Works on either an alias or name. """
        for cmd in self.client.commands:
            if command in [cmd.name] + cmd.aliases:
                return cmd


def setup(client):
    client.add_cog(Help(client))
