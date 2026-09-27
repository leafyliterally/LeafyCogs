from .autopurgebot import AutoPurgeBot

__red_end_user_data_statement__ = (
    "This cog does not persistently store end-user data. It stores "
    "per-guild configuration only (a channel ID, an enabled flag, and "
    "the ID of its own warning message)."
)


async def setup(bot):
    cog = AutoPurgeBot(bot)
    bot.add_cog(cog)
