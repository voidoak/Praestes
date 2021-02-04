class Checks:
    def __init__(self, client):
        self.client = client

    def is_manager(self, ctx) -> bool:
        return ctx.author.id in self.client.config["managers"]

    def guild_is_luminus(self, ctx):
        if ctx.guild:
            return ctx.guild.id == self.config["luminus"]
        return True
