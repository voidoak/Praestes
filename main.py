import os, utils, discord
from datetime import datetime as dt
from discord.ext import commands

class Praestes(commands.Bot):
    def __init__(self):
        self.config = self.get_config()
        super().__init__(
            command_prefix = commands.when_mentioned_or(*self.config["prefixes"]),
            case_insensitive = True,
            intents = discord.Intents.all()
        )
        self.remove_command("help")
        self.load_extensions()
        self.checks = utils.checks(self)

    def get_config(self):
        """ return dict of configuration data """
        return {
            "token": os.environ.get('BOT_TOKEN'),
            "managers": (703746149722357770, 588720566370828307),  # IDs of manager accounts
            "prefixes": [","],
            "blacklist_file": "blacklisted.json"  # file where blacklisted UIDs are stored
        }

    def load_extensions(self):
        """ at initialization, load all cogs """
        self.load_extension("jishaku")
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")

    async def is_owner(self, user:discord.User):
        """ override `is_owner` check so all managers can use `jsk` """
        if user.id in self.config["managers"]:
            return True  # managers have owner permissions

        return await super().is_owner(user)

    async def on_ready(self):
        """ when bot first logs in """
        print(f"{self.user.name} brought online at {dt.now()}.")
        self.invite = f"https://discord.com/oauth2/authorize?client_id={self.user.id}&scope=bot&permissions=2147483647"
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{self.config['prefixes'][0]}help")
        await self.change_presence(status=discord.Status.dnd, activity=activity)


if __name__ == "__main__":
    praestes = Praestes()
    praestes.run(praestes.config["token"])
