import discord
from discord.ext import commands
import decorator
from utils import load_data, dt_format
from datetime import datetime as dt
import json

@decorator.decorator
async def log_event(listener, *args, **kwargs):
    """ log event in proper channel """
    logs = args[0]  # get Logs object
    event = listener.__name__

    try:
        """ message_data being a dictionary of data to pass into
        channel.send, otherwise None if listener so specifies """
        message_data = await listener(*args, **kwargs)
        if not message_data:  # this will only happen if listener returns a false bool (eg. None)
            return
    except Exception as e:
        return print(e)

    with open(logs.config_file) as file:
        # get log channels, then get proper log channel ID, or None if not found
        channel_id = json.load(file).get(event, None)

    if not channel_id:
        return print(f"channel for event {event} not found in configuration file.")

    channel = None if not channel_id else logs.client.get_channel(channel_id)  # get actual log channel object
    if not channel:
        return print(f"channel of ID {channel_id} not found.")

    try:
        await channel.send(**message_data)
    except discord.Forbidden:
        return print(f"missing permission to send messages in {channel.name}")
    except Exception as e:
        return print(e)


class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config_file = "logging/log_config.json"

    @log_event
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        author = message.author
        embed = discord.Embed(
            title = f"Message deleted",
            description = message.content or "content not found (possible file)"
        )
        embed.set_author(name=f"@{author.name}#{author.discriminator}", icon_url=author.avatar_url)
        embed.set_footer(text=f"UID: {author.id}\nMID: {message.id}\n\nin: {message.channel} \nsent: {dt_format(message.created_at)}")

        return { "content":f"{message.author.mention}", "embed":embed }

    @log_event
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        cleanup = lambda s: s[:980] + "..." if len(s) > 980 else s  # to keep description within 2k character limit.
        before_content = cleanup(before.content)
        after_content = cleanup(after.content)
        embed = discord.Embed(
            title = "Message edited",
            description = f"**before:**\n{before_content}\n\n**after:**\n{after_content}"
        )
        embed.set_footer(text=f"UID: {before.author.id}\nMID: {before.id}\n\nin: {before.channel}\nsent: {dt_format(before.created_at)}")

        return { "content": f"{before.author.mention}", "embed": embed }

    @log_event
    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = dt.now()
        creation = member.created_at
        age = abs((now - creation).days)
        message = f"{member.mention}\n```ini\n[  {member.name}#{member.discriminator} ({member.id})  ]\n```\n```ml\nACCOUNT  CREATED: {dt_format(creation)}\nAPPROX. ACC. AGE: ~{age} days\n```"
        embed = discord.Embed(description=message)
        embed.set_author(name="Member joined.", icon_url=member.avatar_url)
        embed.set_footer(text=f"Joined at: {dt_format(now)} UTC")
        return { "embed":embed }

    @log_event
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        embed = discord.Embed(title = "Member banned")
        if isinstance(member, discord.Member):
            """ must be a member object, otherwise it will not have the joined_at attribute. """
            join_date = member.joined_at
            in_server_age = abs((dt.now() - join_date).days)
            embed.description = f"**joined at:** {dt_format(join_date)}\n**time in server:** approx. {in_server_age} days"

        embed.set_footer(text=f"UID: {member.id}\nat: {dt_format(dt.now())}")
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)

        return { "embed": embed }


def setup(client):
    return
    client.add_cog(Logs(client))
