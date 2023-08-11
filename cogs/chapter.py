import json
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from cogs.permission import multiple_check


def setup(bot):
    bot.add_cog(Chapter(bot))


def file_check():  # check if file exists, if not create it
    try:
        with open('database.json', 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        write_database({})


def write_database(data):  # writes to file
    with open('database.json', 'w') as json_file:
        json.dump(data, json_file)


async def get_series_list(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    if group_name not in file_check():
        return []
    else:  # return list of series in group
        return file_check()[group_name]["series_list"].keys()


async def get_chapter_list(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    if group_name not in file_check():
        return []
    elif series_name not in file_check()[group_name]['series_list']:
        return []
    else:  # return list of chapters in series
        return file_check()[group_name]['series_list'][series_name]['chapter_list'].keys()


class Chapter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    Chapter = SlashCommandGroup(name="chapter", description="Chapter-related commands")

    @Chapter.command(description="Adds a chapter to the database")
    async def add(self,
                  ctx,
                  group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                  series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                  chapter_name: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # check if chapter is in database
        if chapter_name in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_name} is already in the database.")
            return
        # check if series has data inside "job_types": []
        if not file_check()[group_name]['series_list'][series_name]['job_types']:
            await ctx.respond(f"Series {series_name} does not have any job types. Please add job types to the series "
                              f"using /series add_job_type.")
            return
        # add chapter to database and then write job_types to a job_list under chapter
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_name] = {}
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'] = {}
        for job_type in data[group_name]['series_list'][series_name]['job_types']:
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type] = {}
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['user_id'] = None
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['date_claimed'] = None
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['status'] = "Backlog"
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['role_id'] = \
                data[group_name]["series_list"][series_name]["job_types"][job_type]['role_id']
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['order'] = \
                data[group_name]["series_list"][series_name]["job_types"][job_type]["order"]
            if data[group_name]["series_list"][series_name]["job_types"][job_type] != 1:
                data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['locked'] = True
            else:
                data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['job_list'][job_type]['locked'] = False
        write_database(data)
        await ctx.respond(f"Chapter {chapter_name} has been added to the database.")

    @Chapter.command(description="Deletes a chapter from the database")
    async def delete(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     chapter_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(get_chapter_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # check if chapter is in database
        if chapter_name not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_name} is not in the database.")
            return
        # delete chapter from database
        data = file_check()
        del data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]
        write_database(data)
        await ctx.respond(f"Chapter {chapter_name} has been deleted from the database.")

    @Chapter.command(description="Renames a chapter in the database")
    async def rename(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     chapter_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                     new_chapter_name: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # check if chapter is in database
        if chapter_name not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_name} is not in the database.")
            return
        # check if new chapter name is in database
        if new_chapter_name in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {new_chapter_name} is already in the database.")
            return
        # rename chapter in database
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][new_chapter_name] = \
            data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]
        del data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]
        write_database(data)
        await ctx.respond(f"Chapter {chapter_name} has been renamed to {new_chapter_name}.")

    @Chapter.command(description="List all chapters in a series in the database")
    async def list(self,
                   ctx,
                   group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                   series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list))):
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # list chapters in series
        chapter_list = ""
        for chapter in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            chapter_list += f"{chapter}\n"
        await ctx.respond(f"Chapters in {series_name}:\n{chapter_list}")

    @Chapter.command(description="Changes the status of a chapter in the database")
    async def status(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     chapter_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                     chapter_status: discord.Option(str, choices=["Backlog", "In Progress", "Complete"])):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # check if chapter is in database
        if chapter_name not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_name} is not in the database.")
            return
        # check if chapter status is already set to that
        if chapter_status == file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['chapter_status']:
            await ctx.respond(f"Chapter {chapter_name} is already set to {chapter_status}.")
            return
        # change chapter status in database
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_name]['chapter_status'] = chapter_status
        write_database(data)
        await ctx.respond(f"Chapter {chapter_name} has been set to {chapter_status}.")
