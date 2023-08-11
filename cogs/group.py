import json
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from cogs.permission import multiple_check


def setup(bot):
    bot.add_cog(Group(bot))


def file_check():  # check if file exists, if not create it
    try:
        with open('database.json', 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        write_database({})


def write_database(data):  # writes to file
    with open('database.json', 'w') as json_file:
        json.dump(data, json_file)


async def get_group_info(ctx: discord.AutocompleteContext):
    # Return keys in group_info
    group_name = ctx.options['group_name']
    return file_check()[group_name]['group_info'].keys()


file_check()  # DO NOT REMOVE UNLESS NECESSARY


class Group(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    Group = SlashCommandGroup(name="group", description="Group-related commands")

    @Group.command(description="Adds a release group to the database")
    async def add(self,
                  ctx,
                  group_name: str, ):
        if not multiple_check(ctx.user.id, ['owners']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is already in database
        if group_name in file_check():
            await ctx.respond(f"Group {group_name} is already in the database.")
            return
        # add group to database
        data = file_check()
        data[group_name] = {"series_list": {}, "group_info": {}}
        write_database(data)
        await ctx.respond(f"Group {group_name} has been added to the database.")

    @Group.command(description="Deletes a release group from the database")
    async def delete(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys()))):
        if not multiple_check(ctx.user.id, ['owners']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # delete group from database
        data = file_check()
        del data[group_name]
        write_database(data)
        await ctx.respond(f"Group {group_name} has been deleted from the database.")

    @Group.command(description="Renames a release group in the database")
    async def rename(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     new_group_name: str):
        if not multiple_check(ctx.user.id, ['owners']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # rename group in database
        data = file_check()
        data[new_group_name] = data[group_name]
        del data[group_name]
        write_database(data)
        await ctx.respond(f"{group_name} has been renamed to {new_group_name}.")

    @Group.command(description="Lists all release groups in the database")
    async def list(self,
                   ctx):
        groups = ""
        for group in file_check().keys():
            groups += f"{group}\n"
        await ctx.respond(f"Release groups in the database:\n{groups}")

    @Group.command(description="Add info to a group")
    async def add_info(self,
                       ctx,
                       group_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                       info_type: str,
                       info: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # add info to group
        data = file_check()
        data[group_name]["group_info"][info_type] = info
        write_database(data)
        await ctx.respond(f"Info {info_type} has been added to {group_name}.")

    @Group.command(description="Delete info from a group")
    async def delete_info(self,
                          ctx,
                          group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(
                              file_check().keys())),
                          info_type: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_group_info))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # delete info from group
        data = file_check()
        del data[group_name]["group_info"][info_type]
        write_database(data)
        await ctx.respond(f"Info {info_type} has been deleted from {group_name}.")

    @Group.command(description="Show group info")
    async def show_info(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        info_type: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_group_info))):
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # show group info
        await ctx.respond(f"{group_name} {info_type}: {file_check()[group_name]['group_info'][info_type]}")

    @Group.command(description="Edit group info")
    async def edit_info(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        info_type: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_group_info)),
                        info: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # edit group info
        data = file_check()
        data[group_name]["group_info"][info_type] = info
        write_database(data)
        await ctx.respond(f"{group_name} {info_type} has been edited to {info}.")
