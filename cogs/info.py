import discord, time, asyncio
from discord.ext import commands
from utils import dt_format, requested, separate, guild_repr
from datetime import datetime as dt

from prettytable import PrettyTable as PT

PERMS_LIST = ['add_reactions', 'administrator', 'attach_files', 'ban_members',
    'change_nickname', 'connect', 'create_instant_invite', 'deafen_members',
    'embed_links', 'external_emojis', 'kick_members', 'manage_channels',
    'manage_emojis', 'manage_guild', 'manage_messages', 'manage_nicknames',
    'manage_permissions', 'manage_roles', 'manage_webhooks', 'mention_everyone',
    'move_members', 'mute_members', 'priority_speaker', 'read_message_history',
    'read_messages', 'send_messages', 'send_tts_messages', 'speak', 'stream',
    'use_external_emojis', 'use_voice_activation', 'view_audit_log',
    'view_channel', 'view_guild_insights']  # permissions to check for.

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        """ get bot latency """
        before = time.monotonic()
        before_ws = int(round(self.client.latency * 1000, 3))
        msg = await ctx.send("Pinging...")
        _ping = (time.monotonic() - before) * 1000

        embed = discord.Embed(title="Latency", description=f"```yaml\nWS:\n  - {before_ws}ms\nREST:\n  - {int(_ping)}ms\n```")
        await msg.edit(content="", embed=embed)

    @commands.command(aliases=["perms"])
    async def permissions(self, ctx, *, member:discord.Member=None):
        """ get guild permissions for a given member """
        member = member or ctx.author
        perms = member.guild_permissions

        message = ""
        embed = discord.Embed(title=f"Guild permissions for {member}.")
        for perm in PERMS_LIST:
            if getattr(perms, perm):
                message += f"  - {perm.replace('_', ' ')}\n"

        embed.description = f"```yaml\nall perms set to true:\n{message}\n```"
        embed.set_footer(text=f"Permissions code: {perms.value}")
        if not message:
            embed.description = "No guild permissions given to this member."

        await ctx.send(embed=embed)

    @commands.command(aliases=["rperms"])
    async def roleperms(self, ctx, *, role:discord.Role):
        """ see permissions for a given role """
        perms = role.permissions

        message = ""
        embed = discord.Embed(title=f"Permissions for {role.name} role.")
        for perm in PERMS_LIST:
            if getattr(perms, perm):
                message += f"  - {perm.replace('_', ' ')}\n"

        embed.description = f"```yaml\nall perms set to true:\n{message}\n```"
        embed.set_footer(text=f"Permissions code: {perms.value}")
        if not message:
            embed.description = "No guild permissions assigned to this role."

        await ctx.send(embed=embed)

    @commands.command(aliases=["roles"])
    async def rolestats(self, ctx):
        """ get simple stats on all roles in server """
        roles = ctx.guild.roles
        role_groups = separate(roles, 30)
        for i, rg in enumerate(role_groups):
            pt = PT()
            pt.field_names = ["role", "members", "%"]  # add field names for rows
            pt.align = "l"  # left align PrettyTable
            embed = discord.Embed()
            for role in rg:
                name = role.name[:15] + ("..." if len(role.name) > 15 else "")  # keep role name < 15 chars
                members = len(role.members)  # get role member count
                percentage = len(role.members) / len(ctx.guild.members) * 100  # get members:server members ratio

                pt.add_row([name, members, f"{(percentage):.2f}"])  # add to PT

            if i == 0: embed.title = "Role stats"
            embed.description = f"```\n{pt}\n```"
            await ctx.send(embed=embed)
            await asyncio.sleep(0.51)

    @commands.command(aliases=["inv"])
    async def invite(self, ctx):
        """ get bot invite """
        embed = discord.Embed(title="Bot invite")
        embed.description=f"Invite {self.client.user.name} to your server with [this link]({self.client.invite})"
        embed.set_image(url=self.client.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["who"])
    @commands.guild_only()
    async def whois(self, ctx, *, member:discord.Member=None):
        """ get a given user's info """
        member = member or ctx.author

        now = dt.utcnow()
        acc_age = (now - member.created_at).days
        since_join = (now - member.joined_at).days

        activity = member.activity
        if activity:
            # handle the activity bc it has to be so complicated doesn't it
            _type = str(activity.type).replace("ActivityType.", "")
            _type = (f"{_type} " if not _type == "custom" else "").title()  # I just didn't want Custom in the message
            activity = _type + str(activity.name)

        message = \
        f"created: {dt_format(member.created_at)} (~{acc_age} days)\n" \
        f"joined: {dt_format(member.joined_at)} (~{since_join} days)\n---\n" \
        f"display: {member.display_name}\n" \
        f"top role: {member.top_role} ({member.top_role.id})\n" \
        f"role count: {len(member.roles)}\n---\n" \
        f"bot: {member.bot}\n" \
        f"online status: {member.status}\n" \
        f"custom status: {activity}"

        embed = discord.Embed(
            title = f"@{member.name}#{member.discriminator}",
            description = f"```yaml\n---\n{message}\n---\n```"
        )
        embed.set_image(url=member.avatar_url)
        embed.set_author(**requested(ctx))
        embed.set_footer(text=f"UID: {member.id}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["av", "ava", "pfp"])
    @commands.guild_only()
    async def avatar(self, ctx, *,  member:discord.Member=None):
        """ get a given user's avatar """
        member = member or ctx.author
        await ctx.reply(member.avatar_url)

    @commands.command(aliases=["role"])
    @commands.guild_only()
    async def roleinfo(self, ctx, *, role:discord.Role):
        """ get info on a given role """
        created = f"created: {dt_format(role.created_at)} (~{(dt.utcnow() - role.created_at).days} days)"
        members, percentage = len(role.members), len(role.members) / len(ctx.guild.members) * 100
        members = f"members: {members} | {percentage:.2f}%"  # defined separately to be able to perform logic on them
        attrs = ["colour", "position", "id", "mentionable"]
        attrs = "\n".join([f"{attr}: {getattr(role, attr)}" for attr in attrs])

        embed = discord.Embed(title=f"Role info", colour=role.colour)
        embed.set_author(**requested(ctx))
        embed.description = f"```yaml\n---\nname: {role.name}\n{created}\n{members}\n---\n{attrs}\n---\n```"
        await ctx.send(embed=embed)

    @commands.command(aliases=["server", "guild", "guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """ get info on the guild in context """
        embed = discord.Embed(title="Server info")
        embed.description = guild_repr(ctx)
        embed.set_author(**requested(ctx))
        embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    async def emojis(self, ctx):
        """ get a list of emojis from the guild in context """
        lis = separate(ctx.guild.emojis, 64)
        if not lis:
            return await ctx.reply("This guild has no emojis.")

        for i in lis:
            embed = discord.Embed(description = "".join(list(map(str, i))))
            await ctx.send(embed=embed)
            await asyncio.sleep(0.51)

    @commands.command(aliases=["bot"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def botstats(self, ctx):
        """ get bot information """
        owner = (await self.client.application_info()).owner
        description = \
        f"---\nname: {self.client.user.name}\nid: {self.client.user.id}\n" \
        f"guilds: {len(self.client.guilds)}\nusers: {len(self.client.users)}\n" \
        f"---\ncommands: {len(self.client.commands)}\nlib: discord.py\n---"

        embed = discord.Embed(title=f"Info on {self.client.user.name}")
        embed.set_footer(text=f"owner: {owner.name}#{owner.discriminator}", icon_url=owner.avatar_url)
        embed.set_image(url=self.client.user.avatar_url)
        embed.description = f"```yaml\n{description}\n```"

        await ctx.reply(embed=embed)


def setup(client):
    client.add_cog(Info(client))
