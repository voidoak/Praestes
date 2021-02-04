import discord, os, json, asyncio
from discord.ext import commands
from utils import separate

class Manager(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.add_check(self.blacklist_check)

    def cog_check(self, ctx):
        return self.client.checks.is_manager(ctx)

    @commands.command(aliases=["blist"])
    async def blacklist(self, ctx, *, user:discord.User):
        """ blacklist a user from the bot """
        if user.id == ctx.author.id:
            return await ctx.reply("You cannot blacklist yourself.")
        elif user.id in self.client.config["managers"]:
            return await ctx.reply("This user is a bot manager, and cannot be blacklisted.")
        elif user.bot:
            return await ctx.reply("You cannot blacklist a bot.")

        _id = str(user.id)
        bl_file = self.client.config["blacklist_file"]
        with open(bl_file, "r") as file:
            bl_users = json.load(file)

        if _id in bl_users:
            return await ctx.reply(f"User `{user}` has already been blacklisted.")

        bl_users.append(_id)
        with open(bl_file, "w") as file:
            json.dump(bl_users, file)

        await ctx.reply(f"User `{user}` has been successfully blacklisted.")

    @commands.command(aliases=["wlist"])
    async def whitelist(self, ctx, *, user:discord.User):
        """ remove a user from blacklist """
        _id = str(user.id)
        bl_file = self.client.config["blacklist_file"]
        with open(bl_file, "r") as file:
            bl_users = json.load(file)

        if _id not in bl_users:
            return await ctx.reply(f"User `{user}` has not yet been blacklisted.")

        bl_users.remove(_id)
        with open(bl_file, "w") as file:
            json.dump(bl_users, file)

        await ctx.reply(f"User `{user}` has been successfully removed from blacklist.")

    @commands.command(aliases=["lbl"])
    async def listblisted(self, ctx):
        """ list blacklisted members """
        with open(self.client.config["blacklist_file"]) as file:
            bl_users = json.load(file)

        bl_users = { int(_id): discord.utils.get(self.client.users, id=int(_id)) for _id in bl_users }
        users = [f"{user.name}#{user.discriminator} ({_id})" for _id, user in bl_users.items()]

        if len(users) == 0:
            return await ctx.reply("There are no users blacklisted at this time.")

        embed = discord.Embed()
        user_groups = separate(users, 41)
        for i, group in enumerate(user_groups):
            if i == 0:
                embed.title = "Blacklisted users"

            embed.description = "```\n" + "\n".join(group) + "\n```"
            await ctx.send(embed=embed)
            await asyncio.sleep(0.51)

    @commands.command()
    async def botwarn(self, ctx, user:discord.User, *, reason:str):
        """ warn a user for abusing the bot """
        try:
            embed = discord.Embed(title="You are being warned by the bot developers for:")
            embed.description = f"```\n{reason}\n```"
            embed.set_footer(text="Continued abuse may result in blacklisting.")
            await user.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"Could not warn `{user}`, either due to DMs being blocked, or no shared guilds.")
            return

        await ctx.send(f"Warned `{user}`.")

    @commands.command(aliases=["ul"])
    async def unload(self, ctx, extension:str="all"):
        """ unload given cog, or all cogs """
        await self.handle_cog(ctx, self.client.unload_extension, extension)

    @commands.command(aliases=["rl", "rel"])
    async def reload(self, ctx, extension:str="all"):
        """ reload given cog, or all cogs """
        await self.handle_cog(ctx, self.client.reload_extension, extension)

    @commands.command()
    async def load(self, ctx, extension:str="all"):
        """ load given cog, or all cogs """
        await self.handle_cog(ctx, self.client.load_extension, extension)

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send(f"`{self.client.user}` shut down by `{ctx.author}`.")
        await self.client.logout()

    async def handle_cog(self, ctx, func, extension):
        """ load/unload/reload given cog, or all cogs, based on func arg """
        extension = extension.lower()

        func_name = {
            "unload_extension": "unload",
            "reload_extension": "reload",
            "load_extension": "load"
        }[func.__name__]  # get proper function name to use it like a verb

        if extension == "all":
            message = ""
            for i, file in enumerate(os.listdir("./cogs")):
                if file.endswith(".py"):
                    file = file[:-3]
                    try:
                        func(f"cogs.{file}")
                        message += f"+ [{i}] cog \"{file}\" {func_name}ed successfully\n"
                    except Exception as e:
                        message += f"- [{i}] unable to {func_name} cog \"{file}\". {e.__class__.__name__}: {e}\n"

            embed = discord.Embed(description=f"```diff\n{message}\n```")
            return await ctx.reply(embed=embed)

        try:
            func(f"cogs.{extension}")
            embed = discord.Embed(description=f"```diff\n+ cog \"{extension}\" {func_name}ed successfully\n```")
            await ctx.reply(embed=embed)
        except Exception as e:
            embed= discord.Embed(description=f"```diff\n- unable to {func_name} cog \"{extension}\". {e.__class__.__name__}: {e}```\n")
            await ctx.reply(embed=embed)

    def blacklist_check(self, ctx):
        with open(self.client.config["blacklist_file"], "r") as file:
            bl_users = json.load(file)

        return not str(ctx.author.id) in bl_users


def setup(client):
    client.add_cog(Manager(client))
