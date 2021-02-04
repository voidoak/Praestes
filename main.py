import os
import yaml
from datetime import datetime as dt
import discord
from discord.ext import commands
import utils

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
        try:
            with open("config.yaml", "r") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            config = {}

        config.update(os.environ)

        return config

    def load_extensions(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")

    async def on_ready(self):
        print(f"{self.user.name} brought online at {dt.now()}.")
        self.invite = f"https://discord.com/oauth2/authorize?client_id={self.user.id}&scope=bot&permissions=2147483647"
        activity = discord.Activity(type=discord.ActivityType.watching, name="the lost... protecting the weary.")
        await self.change_presence(status=discord.Status.dnd, activity=activity)


if __name__ == "__main__":
    praestes = Praestes()
    praestes.run(praestes.config["token"])
