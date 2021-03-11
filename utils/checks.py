class Checks:
    def __init__(self, client):
        self.client = client

    def is_manager(self, ctx) -> bool:
        """check if ctx.author is a bot manager"""
        return ctx.author.id in self.client.config["managers"]
