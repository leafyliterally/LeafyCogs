import discord
from redbot.core import commands, checks
from redbot.core.utils.chat_formatting import humanize_number

__version__ = "1.0.2"
__author__ = "Leafy"
max_drag = 61

class Guild(commands.Cog):    
    """
    Cookie Run Kingdom Guild Related Command
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def drag(self, ctx, level: int, percentage: int):
        """
        Count Dragon Health Remaining.

        Dragon Level varies from **1** to **61**.
        Percentage varies from **1** to **100**.
        """
        if (level <= 0 or level > max_drag):
            description = f"<:error:785047391257624596> Level capped between **1** and **{max_drag}**"
            embed = discord.Embed(description=description, color=15747399)
            await ctx.send(embed=embed)
            return

        if (percentage <= 0 or percentage > 100):
            description = "<:error:785047391257624596> Percentage capped between **1** and **100**"
            embed = discord.Embed(description=description, color=15747399)
            await ctx.send(embed=embed)

        dragon_health = {
            1: 3000000,
            2: 3150000,
            3: 3474000,
            4: 3648000,
            5: 3830000,
            6: 4022000,
            7: 4224000,
            8: 4436000,
            9: 4658000,
            10: 4890000,
            11: 5134000,
            12: 5390000,
            13: 5660000,
            14: 5944000,
            15: 6242000,
            16: 6554000,
            17: 6682000,
            18: 7226000,
            19: 7588000,
            20: 8366000,
            21: 9224000,
            22: 10170000,
            23: 11212000,
            24: 12360000,
            25: 13626000,
            26: 15024000,
            27: 16564000,
            28: 18262000,
            29: 20134000,
            30: 22198000,
            31: 24474000,
            32: 26982000,
            33: 29748000,
            34: 32798000,
            35: 35472000,
            36: 37632000,
            37: 39922000,
            38: 42354000,
            39: 44932000,
            40: 47206000,
            41: 49114000,
            42: 51098000,
            43: 53162000,
            44: 55310000,
            45: 57262000,
            46: 58992000,
            47: 60774000,
            48: 61612000,
            49: 64504000,
            50: 66456000,
            51: 68464000,
            52: 70532000,
            53: 72664000,
            54: 74860000,
            55: 77122000,
            56: 79452000,
            57: 81854000,
            58: 84328000,
            59: 86876000,
            60: 89502000,
            61: 92206000
        }

        min_hp = dragon_health[level] * ((percentage - 1) / 100)
        max_hp = dragon_health[level] * percentage / 100
        description = None
        if percentage == 100:
            description = f"<:success:785047433716957194> Lv. {level} Dragon at {percentage}% is **{humanize_number(max_hp)}**"
        elif percentage == 99:
            description = f"<:success:785047433716957194> Lv. {level} Dragon at {percentage}% varies between **{humanize_number(min_hp)}** and **{humanize_number(dragon_health[level] - 1)}**"
        else:
            description = f"<:success:785047433716957194> Lv. {level} Dragon at {percentage}% varies between **{humanize_number(min_hp)}** and **{humanize_number(max_hp)}**"
        embed = discord.Embed(description=description, color=4437377)
        return await ctx.send(embed=embed)

    @commands.command()
    def calculateKey(self, ctx, start: int, end: int):
        """
        Count Cake Tower Key Needed from level to level.

        Cake Tower Level varies from **1** to **150**.
        2 Chests can be found at Tray 11, 26, 41, 56, 71, 86, 101, 116, 131, 146
        An additional level can be found at Tray 8, 23, 38, 53, 68, 83, 98, 113, 128, 143
        """
        if (start <= 0 or start > 150 or end <= 0 or end > 150):
            description = "<:error:785047391257624596> Tray Level capped between **1** and **150**"
            embed = discord.Embed(description=description, color=15747399)
            await ctx.send(embed=embed)
            return
        
        chest = [11, 26, 41, 56, 71, 86, 101, 116, 131, 146]
        extra = [8, 23, 38, 53, 68, 83, 98, 113, 128, 143]

        key_min = 0
        key_max = 0

        for key in chest:
            if start <= key <= end:
                if key < 50:
                    key_min += 6
                    key_max += 24
                elif key < 100:
                    key_min += 8
                    key_max += 32
                else:
                    key_min += 10
                    key_max += 40

        for key in extra:
            if start <= key <= end:
                if key < 50:
                    key_max += 6
                elif key < 100:
                    key_max += 8
                else:
                    key_max += 10

        for key in range(start, end + 1):
            if key < 50:
                key_min += 6
                key_max += 6
            elif key < 100:
                key_min += 8
                key_max += 8
            else:
                key_min += 10
                key_max += 10

        description = f"You need **{humanize_number(key_min)} keys** from **Tray {start}** to **Tray {end}** assuming you choose all left chests.\n"
        description += f"Assuming you want to unlock all trays available, you will need **{humanize_number(key_max)} keys**!"
        embed = discord.Embed(description=description, color=4437377)
        return await ctx.send(embed=embed)
        
        
