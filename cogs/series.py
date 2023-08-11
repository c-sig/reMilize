import json
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from cogs.permission import multiple_check

default_job_types = ["Translator", "Proofreader", "Cleaner", "Redrawer", "Typesetter", "Quality Checker"]


def setup(bot):
    bot.add_cog(Series(bot))


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


async def get_info_list(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    if group_name not in file_check():
        return []
    elif series_name not in file_check()[group_name]["series_list"]:
        return []
    else:  # return list of info in series
        return file_check()[group_name]["series_list"][series_name]["series_info"].keys()


async def get_fonts(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    if group_name not in file_check():
        return []
    elif series_name not in file_check()[group_name]["series_list"]:
        return []
    else:  # return list of fonts in series
        return file_check()[group_name]["series_list"][series_name]["font_list"].keys()


async def get_job_types(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    if group_name not in file_check():
        return []
    elif series_name not in file_check()[group_name]["series_list"]:
        return []
    else:  # return list of job types in series
        return file_check()[group_name]["series_list"][series_name]["job_types"]


async def get_font_style(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    font_name = ctx.options['font_name']
    if group_name not in file_check():
        return []
    elif series_name not in file_check()[group_name]["series_list"]:
        return []
    elif font_name not in file_check()[group_name]["series_list"][series_name]["font_list"]:
        return []
    else:  # return list of font styles in font
        return file_check()[group_name]["series_list"][series_name]["font_list"][font_name].keys()


file_check()  # DO NOT REMOVE UNLESS NECESSARY


class Series(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    Series = SlashCommandGroup(name="series", description="Series-related commands")

    @Series.command(description="Adds a series to the database")
    async def add(self,
                  ctx,
                  name: str,
                  group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(file_check().keys()))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if name is already under group
        if name in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {name} is already under group {group_name}.")
            return
        # add series to database
        data = file_check()
        data[group_name]["series_list"][name] = {"chapter_list": {}, "series_info": {}, "font_list": {},
                                                 "job_types": {}}
        write_database(data)
        await ctx.respond(f"Series {name} has been added to group {group_name}.")

    @Series.command(description="Deletes a series from the database")
    async def delete(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # delete series from database
        data = file_check()
        del data[group_name]["series_list"][series_name]
        write_database(data)
        await ctx.respond(f"Series {series_name} has been deleted from group {group_name}.")

    @Series.command(description="Renames a series in the database")
    async def rename(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     new_series_name: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # rename series in database
        data = file_check()
        data[group_name]["series_list"][new_series_name] = data[group_name]["series_list"][series_name]
        del data[group_name]["series_list"][series_name]
        write_database(data)
        await ctx.respond(f"Series {series_name} has been renamed to {new_series_name} in group {group_name}.")

    @Series.command(description="Changes the group a series is under")
    async def move(self,
                   ctx,
                   group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                   series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                   new_group_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(file_check().keys()))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # move series to new group
        data = file_check()
        data[new_group_name]["series_list"][series_name] = data[group_name]["series_list"][series_name]
        del data[group_name]["series_list"][series_name]
        write_database(data)
        await ctx.respond(f"Series {series_name} has been moved to group {new_group_name}.")

    @Series.command(description="Adds information to a series.")
    async def add_info(self,
                       ctx,
                       group_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                       series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                       title: str,
                       info: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # if title already exists, send error
        if title in file_check()[group_name]["series_list"][series_name]["series_info"]:
            await ctx.respond(f"{title} already exists in series {series_name}.")
            return
        # add info to series
        data = file_check()
        data[group_name]["series_list"][series_name]["series_info"][title] = info
        write_database(data)
        await ctx.respond(f"{title} has been added to series {series_name}.")

    @Series.command(description="Deletes information from a series.")
    async def delete_info(self,
                          ctx,
                          group_name: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(
                                                         file_check().keys())),
                          series_name: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                          title: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_info_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # delete info from series
        data = file_check()
        del data[group_name]["series_list"][series_name]["series_info"][title]
        write_database(data)
        await ctx.respond(f"{title} has been deleted from series {series_name} in group {group_name}.")

    @Series.command(description="Renames info title in a series.")
    async def rename_info(self,
                          ctx,
                          group_name: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(
                                                         file_check().keys())),
                          series_name: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                          title: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_info_list)),
                          new_title: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # rename title in series
        data = file_check()
        data[group_name]["series_list"][series_name]["series_info"][new_title] = data[group_name]["series_list"][
            series_name]["series_info"][title]
        del data[group_name]["series_list"][series_name]["series_info"][title]
        write_database(data)
        await ctx.respond(f"{title} has been renamed to {new_title} in series {series_name} in group {group_name}.")

    @Series.command(description="Lists all information in a series.")
    async def list_info(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        series_name: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_series_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # list all information in series
        list_of_info = ""
        for info in file_check()[group_name]["series_list"][series_name]["series_info"]:
            list_of_info += f"{info}\n"
        await ctx.respond(f"Information in series {series_name} in group {group_name}:\n{list_of_info}")

    @Series.command(description="Show information in a specific title under a series")
    async def show_info(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        series_name: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                        title: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_info_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # show info in series
        await ctx.respond(
            f"{title} in series {series_name} in group {group_name}:\n{file_check()[group_name]['series_list'][series_name]['series_info'][title]}")

    @Series.command(description="List all series in a group.")
    async def list(self,
                   ctx,
                   group_name: discord.Option(str,
                                              autocomplete=discord.utils.basic_autocomplete(file_check().keys()))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if group exists
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} does not exist.")
            return
        # list all series in group
        list_of_series = ""
        for series in file_check()[group_name]["series_list"]:
            list_of_series += f"{series}\n"
        await ctx.respond(f"Series in group {group_name}:\n{list_of_series}")

    @Series.command(description="List all series.")
    async def list_all(self, ctx):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # list all series
        list_of_series = ""
        for group in file_check():
            for series in file_check()[group]["series_list"]:
                list_of_series += f"{series}\n"
        await ctx.respond(f"Series:\n{list_of_series}")

    @Series.command(description="Adds a font to a series.")
    async def add_font(self,
                       ctx,
                       group_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                       series_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                       font_description: str,
                       font_style: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # add font to series under font list
        data = file_check()
        data[group_name]["series_list"][series_name]["font_list"][font_description] = font_style
        write_database(data)
        await ctx.respond(f"{font_description} has been added to series {series_name}.")

    @Series.command(description="Deletes a font from a series.")
    async def delete_font(self,
                          ctx,
                          group_name: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(
                                                         file_check().keys())),
                          series_name: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                          font_description: discord.Option(str,
                                                           autocomplete=discord.utils.basic_autocomplete(get_fonts))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # delete font from series under font list
        data = file_check()
        del data[group_name]["series_list"][series_name]["font_list"][font_description]
        write_database(data)
        await ctx.respond(f"{font_description} has been deleted from series {series_name}.")

    @Series.command(description="Renames a font in a series.")
    async def rename_font(self,
                          ctx,
                          group_name: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(
                                                         file_check().keys())),
                          series_name: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                          font_description: discord.Option(str,
                                                           autocomplete=discord.utils.basic_autocomplete(get_fonts)),
                          new_font_description: str):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # check if new font description is already in use
        if new_font_description in file_check()[group_name]["series_list"][series_name]["font_list"]:
            await ctx.respond(f"{new_font_description} is already in use.")
            return
        # rename font in series under font list
        data = file_check()
        data[group_name]["series_list"][series_name]["font_list"][new_font_description] = \
            data[group_name]["series_list"][
                series_name]["font_list"][font_description]
        del data[group_name]["series_list"][series_name]["font_list"][font_description]
        write_database(data)
        await ctx.respond(f"{font_description} has been renamed to {new_font_description} in series {series_name}.")

    @Series.command(description="Edit font in a series.")
    async def edit_font(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        series_name: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                        font_description: discord.Option(str,
                                                         autocomplete=discord.utils.basic_autocomplete(get_fonts)),
                        font: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_font_style))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # edit font style in series under font list
        data = file_check()
        data[group_name]["series_list"][series_name]["font_list"][font_description] = font
        write_database(data)
        await ctx.respond(f"{font_description} has been edited in series {series_name}.")

    @Series.command(description="List all fonts in a series.")
    async def list_font(self,
                        ctx,
                        group_name: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                        series_name: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_series_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # list all fonts in series
        list_of_fonts = ""
        for font in file_check()[group_name]["series_list"][series_name]["font_list"]:
            list_of_fonts += f"{font}\n"
        await ctx.respond(f"Fonts in series {series_name}:\n{list_of_fonts}")

    @Series.command(description="Add a job type to a series with order value and role id.")
    async def add_job_type(self,
                           ctx,
                           group_name: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(
                                                          file_check().keys())),
                           series_name: discord.Option(str,
                                                       autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                           job_type: str,
                           order: int,
                           role_id: discord.Role):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # check if job_type is already in use
        if job_type in file_check()[group_name]["series_list"][series_name]["job_types"]:
            await ctx.respond(f"{job_type} is already in use.")
            return
        # write job_type to series under job_types
        data = file_check()
        data[group_name]["series_list"][series_name]["job_types"][job_type] = {"order": order, "role_id": role_id.id}
        write_database(data)
        await ctx.respond(f"{job_type} has been added to series {series_name}.")
        return

    @Series.command(description="Delete a job type from a series.")
    async def delete_job_type(self,
                              ctx,
                              group_name: discord.Option(str,
                                                         autocomplete=discord.utils.basic_autocomplete(
                                                             file_check().keys())),
                              series_name: discord.Option(str,
                                                          autocomplete=discord.utils.basic_autocomplete(
                                                              get_series_list)),
                              job_type: discord.Option(str,
                                                       autocomplete=discord.utils.basic_autocomplete(get_job_types))):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # check if job_type is in use
        if job_type not in file_check()[group_name]["series_list"][series_name]["job_types"]:
            await ctx.respond(f"{job_type} is not in use.")
            return
        # delete job_type from series under job_types
        data = file_check()
        del data[group_name]["series_list"][series_name]["job_types"][job_type]
        write_database(data)
        await ctx.respond(f"{job_type} has been deleted from series {series_name}.")

    @Series.command(description="Edit job type order in a series.")
    async def edit_order(self,
                         ctx,
                         group_name: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(
                                                        file_check().keys())),
                         series_name: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                         job_type: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(get_job_types)),
                         order: int):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # check if job_type is in use
        if job_type not in file_check()[group_name]["series_list"][series_name]["job_types"]:
            await ctx.respond(f"{job_type} is not in use.")
            return
        # edit job_type order in series under job_types
        data = file_check()
        data[group_name]["series_list"][series_name]["job_types"][job_type] = order
        write_database(data)
        await ctx.respond(f"{job_type} has been edited in series {series_name} with order {order}.")

    @Series.command(description="Edit job type in a series")
    async def edit_job_type(self,
                            ctx,
                            group_name: discord.Option(str,
                                                       autocomplete=discord.utils.basic_autocomplete(
                                                           file_check().keys())),
                            series_name: discord.Option(str,
                                                        autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                            job_type: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(get_job_types)),
                            new_job_type: discord.Option(str, choices=default_job_types)):
        if not multiple_check(ctx.user.id, ['owners', 'managers']):
            await ctx.respond("You do not have permission to use this command.")
            return
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # check if job_type is in use
        if job_type not in file_check()[group_name]["series_list"][series_name]["job_types"]:
            await ctx.respond(f"{job_type} is not in use.")
            return
        # check if new_job_type is already in use
        if new_job_type in file_check()[group_name]["series_list"][series_name]["job_types"]:
            await ctx.respond(f"{new_job_type} is already in use.")
            return
        # edit job_type in series under job_types
        data = file_check()
        data[group_name]["series_list"][series_name]["job_types"][new_job_type] = \
            data[group_name]["series_list"][series_name]["job_types"][job_type]
        del data[group_name]["series_list"][series_name]["job_types"][job_type]
        write_database(data)
        await ctx.respond(f"{job_type} has been edited in series {series_name} to {new_job_type}.")

    @Series.command(description="List job types in a series.")
    async def list_job_types(self,
                             ctx,
                             group_name: discord.Option(str,
                                                        autocomplete=discord.utils.basic_autocomplete(
                                                            file_check().keys())),
                             series_name: discord.Option(str,
                                                         autocomplete=discord.utils.basic_autocomplete(
                                                             get_series_list))):
        # check if series is under group
        if series_name not in file_check()[group_name]["series_list"]:
            await ctx.respond(f"Series {series_name} is not under group {group_name}.")
            return
        # list job_types in series under job_types
        data = file_check()
        job_types = data[group_name]["series_list"][series_name]["job_types"]
        job_types_list = ""
        for job_type in job_types:
            job_types_list += f"{job_type}\n"
        await ctx.respond(f"Job types in series {series_name}:\n{job_types_list}")
