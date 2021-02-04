import discord, asyncio
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        return not ctx.guild is None

    @commands.command(aliases=["del"])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def delete(self, ctx, count:int=1):
        """ delete up to 100 messages in context channel """
        if 0 >= count or count > 100:
            raise Exception("you cannot delete more than 100 messages, or less than 1.")

        chnl = ctx.channel
        await chnl.delete_messages([ctx.message])
        messages = await chnl.history(limit=count).flatten()
        await chnl.delete_messages(messages)

        msg = await ctx.send(f"Message{'s' * int(bool(int(count) - 1))} deleted.")
        await asyncio.sleep(1.2)
        await chnl.delete_messages([msg])

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def setnick(self, ctx, member:discord.Member, *, new_nick:str):
        """ change given user's nickname """
        old_nick = member.display_name
        await member.edit(nick=new_nick)
        embed = discord.Embed(description=f"Updated **{member.name}**'s nickname.")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ar"])
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member:discord.Member, *, role:discord.Role):
        """ add role to a given member, by mention or ID """
        await member.add_roles(role)
        await ctx.reply(f"Added role `{role}` to **{member}**.")

    @commands.command(aliases=["rr"])
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member:discord.Member, *, role:discord.Role):
           """ remove role from a given member, by mention or ID """
           await member.remove_roles(role)
           await ctx.reply(f"Removed role `{role}` from **{member}**")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, *, reason:str="no given reason"):
        """ kick a given user, by ID or mention """
        if self.member_remove_fail(ctx, user): return

        await member.kick()
        embed = discord.Embed(title=f"Reason for kick:", description=reason)
        embed.set_author(name=f"{member} kicked", icon_url=member.avatar_url)
        embed.set_footer(text=f"Kicked by {ctx.author}\nUID: {member.id}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user:discord.User, *, reason:str="no given reason"):
        """ ban a given user, whether in guild or not, by ID or mention """
        if member:=discord.utils.get(ctx.guild.members, id=user.id):
            if self.member_remove_fail(ctx, member): return

        await ctx.guild.ban(discord.Object(id=user.id))
        embed = discord.Embed(title=f"Reason for ban:", description=reason)
        embed.set_author(name=f"{user} banned", icon_url=user.avatar_url)
        embed.set_footer(text=f"Banned by {ctx.author}\nUID: {user.id}")
        await ctx.send(embed=embed)

    def member_remove_fail(self, ctx, member:discord.Member):
        return not ctx.author.top_role > member.top_role or ctx.author.id == member.id


def setup(client):
    client.add_cog(Moderation(client))

