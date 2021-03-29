import discord
from discord.ext import commands
import utils

VISIBLE_COGS = [ "info", "moderation", "utility", "embed" ]

class HelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        desc = []
        for cog, cmds in mapping.items():
            if cog is None or cog.qualified_name.lower() not in VISIBLE_COGS:
                continue

            name = cog.qualified_name
            cmds = await self.filter_commands(cmds, sort=True)

            desc.append(f"{cog.qualified_name}: {len(cmds)} commands")

        desc = "\n-\n".join(desc)

        embed = discord.Embed(title="All Commands")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text=f"Run {self.clean_prefix}{self.invoked_with} [cog] to learn more about a cog and its commands")
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        desc = ""
        cmds = await self.filter_commands(group.commands, sort=True)
        for c in cmds:
            desc += f"{c.qualified_name}: {c.short_doc or 'no help information listed'}\n"

        embed = discord.Embed(title=f"Group info: {group.qualified_name}")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text=f"Run {self.clean_prefix}{self.invoked_with} [command] to learn more about a command")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, cmd):
        desc = \
        f"name: {cmd.name}\ncog: {cmd.cog_name}\ndescription:\n {cmd.help or cmd.short_doc}\n\n" \
        f"aliases:\n - {', '.join(cmd.aliases) if cmd.aliases else 'None'}\n\n" \
        f"usage: {cmd.name} {cmd.signature}"

        embed = discord.Embed(title=f"Command info: {cmd.qualified_name}")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text="[optional], <required>, = denotes default value")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        cmds = await self.filter_commands(cog.get_commands(), sort=True)
        cmds = "\n-\n".join(f"{cmd.name}: {cmd.help}" for cmd in cmds)
        embed = discord.Embed(title=f"Cog info: {cog.qualified_name}")
        embed.description = f"```yaml\n---\n{cmds}\n---\n```"
        embed.set_footer(text=f"Run {self.clean_prefix}{self.invoked_with} [command] to learn more about a command")
        await self.get_destination().send(embed=embed)


def setup(client):
    client._default_help_command = client.help_command
    client.help_command = HelpCommand()


def teardown(client):
    client.help_command = client._default_help_command
