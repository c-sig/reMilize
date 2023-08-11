import asyncio
import json
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from cogs.permission import multiple_check
from cogs.chapter import get_series_list, get_chapter_list
from main import bot

status_list = ['Backlog', 'In Progress', 'Completed']


def get_time():
    import time
    return int(time.time())


def setup(bot):
    bot.add_cog(Job(bot))


def file_check():
    try:
        with open('database.json', 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        write_database({})


def write_database(data):
    with open('database.json', 'w') as json_file:
        json.dump(data, json_file)


async def get_job_list(ctx: discord.AutocompleteContext):
    group_name = ctx.options['group_name']
    series_name = ctx.options['series_name']
    # get job types from series
    return file_check()[group_name]['series_list'][series_name]['job_types'].keys()


file_check()


class Job(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    Job = SlashCommandGroup(name="job", description="Job-related commands")

    @Job.command(description="Claim a job")
    async def claim(self,
                    ctx,
                    group_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                    series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                    chapter_number: discord.Option(str,
                                                   autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                    job_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_job_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
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
        if chapter_number not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_number} is not in the database.")
            return
        # check if job is in database
        if job_name not in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
            'job_list']:
            await ctx.respond(f"Job {job_name} is not in the database.")
            return
        # check if job is already claimed by checking if user_id has a value
        if file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] is not None:
            await ctx.respond(f"Job {job_name} is already claimed.")
            return
        # claim job
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] = ctx.user.id
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'date_claimed'] = get_time()
        write_database(data)
        await ctx.respond(f"Job {job_name} claimed.")

    @Job.command(description="Unclaim a job")
    async def unclaim(self,
                      ctx,
                      group_name: discord.Option(str,
                                                 autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                      series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                      chapter_number: discord.Option(str,
                                                     autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                      job_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_job_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
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
        if chapter_number not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_number} is not in the database.")
            return
        # check if job is in database
        if job_name not in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
            'job_list']:
            await ctx.respond(f"Job {job_name} is not in the database.")
            return
        # check if job is not claimed by anyone or the user
        if file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] is None:
            await ctx.respond(f"Job {job_name} is not claimed.")
            return
        if file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] != ctx.user.id:
            await ctx.respond(f"Job {job_name} is not claimed by you.")
            return
        # unclaim job
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] = None
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'date_claimed'] = None
        write_database(data)
        await ctx.respond(f"Job {job_name} unclaimed.")

    @Job.command(description="Assign a job")
    async def assign(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     chapter_number: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                     job_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_job_list)),
                     user: discord.User):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
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
        if chapter_number not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_number} is not in the database.")
            return
        # check if job is in database
        if job_name not in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
            'job_list']:
            await ctx.respond(f"Job {job_name} is not in the database.")
            return
        # check if job is already claimed by checking if user_id has a value
        if file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] is not None:
            await ctx.respond(f"Job {job_name} is already claimed.")
            return
        # assign job
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] = user.id
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'date_claimed'] = get_time()
        write_database(data)
        await ctx.respond(f"Job {job_name} assigned to {user.display_name}.")

    @Job.command(description="Unassign a job")
    async def unassign(self,
                       ctx,
                       group_name: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                       series_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                       chapter_number: discord.Option(str,
                                                      autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                       job_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_job_list))):
        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
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
        if chapter_number not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_number} is not in the database.")
            return
        # check if job is in database
        if job_name not in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
            'job_list']:
            await ctx.respond(f"Job {job_name} is not in the database.")
            return
        # check if job is not claimed by anyone
        if file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] is None:
            await ctx.respond(f"Job {job_name} is not claimed.")
            return
        # unassign job
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'user_id'] = None
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'date_claimed'] = None
        write_database(data)
        await ctx.respond(f"Job {job_name} unassigned.")

    @Job.command(description="Update job status")
    async def update(self,
                     ctx,
                     group_name: discord.Option(str,
                                                autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                     series_name: discord.Option(str,
                                                 autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                     chapter_number: discord.Option(str,
                                                    autocomplete=discord.utils.basic_autocomplete(get_chapter_list)),
                     job_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_job_list)),
                     status: discord.Option(str, choices=status_list)):
        # get user_id of job
        user_id = \
            file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
                'user_id']
        if user_id is None:
            await ctx.respond(f"Job {job_name} is not claimed.")
            return
        if (not multiple_check(ctx.user.id, ['owners', 'managers'])) or (user_id != ctx.user.id):
            await ctx.respond(f"You can only update the status of jobs that you claimed.")
            return
        # update status
        data = file_check()
        data[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job_name][
            'status'] = status
        write_database(data)
        await ctx.respond(f"Job updated to {status}")
        # if marked completed, check if all jobs of the same order are completed, if yes, ping the next job of order
        # +1 using the role_id defined in the chapter
        if status == 'Completed':
            # get order of job
            order = \
                file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][
                    job_name][
                    'order']
            # get all jobs of the same order
            jobs = []
            for job in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list']:
                if \
                        file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
                            'job_list'][job][
                            'order'] == order:
                    jobs.append(job)
            # check if all jobs of the same order are completed
            for job in jobs:
                if \
                        file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
                            'job_list'][job][
                            'status'] != 'Completed':
                    return
            # ping the next job of order +1 using the role_id defined in the chapter
            next_order = int(order) + 1
            for job in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list']:
                if \
                        file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number][
                            'job_list'][job][
                            'order'] == next_order:
                    # await ctx.respond(f"<@&{file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job]['role_id']}>")
                    await ctx.respond("Still haven't figured out how to get roles to ping.")
                    return
            else:
                await ctx.respond(f"Job {job_name} status updated to {status}.")
                return

    @Job.command(description="List all jobs in a chapter as well as their assigned users with their status")
    async def list(self,
                   ctx,
                   group_name: discord.Option(str,
                                              autocomplete=discord.utils.basic_autocomplete(file_check().keys())),
                   series_name: discord.Option(str,
                                               autocomplete=discord.utils.basic_autocomplete(get_series_list)),
                   chapter_number: discord.Option(str,
                                                  autocomplete=discord.utils.basic_autocomplete(get_chapter_list))):
        # check if group is in database
        if group_name not in file_check():
            await ctx.respond(f"Group {group_name} is not in the database.")
            return
        # check if series is in database
        if series_name not in file_check()[group_name]['series_list']:
            await ctx.respond(f"Series {series_name} is not in the database.")
            return
        # check if chapter is in database
        if chapter_number not in file_check()[group_name]['series_list'][series_name]['chapter_list']:
            await ctx.respond(f"Chapter {chapter_number} is not in the database.")
            return
        # list jobs
        embed = discord.Embed(title=f"Jobs in {group_name} - {series_name} - {chapter_number}")
        for job in file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list']:
            user_id = \
                file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job][
                    'user_id']
            # convert user_id to user_name
            if user_id is None:
                user_id = 'Unassigned'
            else:
                user_id = await self.bot.fetch_user(user_id)
                user_id = user_id.display_name
            embed.add_field(name=job,
                            value=f"Assigned to: {user_id}\n"
                                  f"Status: {file_check()[group_name]['series_list'][series_name]['chapter_list'][chapter_number]['job_list'][job]['status']}",
                            inline=False)
        await ctx.respond(embed=embed)

    @Job.command(description="Looks for user in a job and lists all jobs that user is assigned to")
    async def todo(self, ctx, user_id: discord.User = None):
        if user_id is None:
            user_id = ctx.user

        if not multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            await ctx.respond("You do not have permission to use this command.")
            return

        # list jobs
        embed = discord.Embed(title=f"Jobs assigned to {user_id.display_name}")
        for group in file_check():
            for series in file_check()[group]['series_list']:
                for chapter in file_check()[group]['series_list'][series]['chapter_list']:
                    for job in file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list']:
                        if file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list'][job][
                            'user_id'] == user_id.id:
                            # only include jobs that are not marked completed
                            if file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list'][job][
                                'status'] != 'Completed':
                                embed.add_field(name=f"{group} - {series} - {chapter} - {job}",
                                                value=f"Status: {file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list'][job]['status']}",
                                                inline=False)
        await ctx.respond(embed=embed)

    # # function that checks for vacant jobs in every chapter and pings using the role_id provided in the database, should occur every hour
    #     @Job.command(description="Ping vacant jobs in every chapter")
    #     async def ping(self, ctx):
    #         if not multiple_check(ctx.user.id, ['owners', 'managers']):
    #             await ctx.respond("You do not have permission to use this command.")
    #             return
    #         while True:
    #             for group in file_check():
    #                 for series in file_check()[group]['series_list']:
    #                     for chapter in file_check()[group]['series_list'][series]['chapter_list']:
    #                         for job in file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list']:
    #                             if file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list'][job][
    #                                 'user_id'] is None:
    #                                 # ping the role, show series and chapter the vacancy is in
    #                                 # like this: <@&role_id> Series - Chapter - Job
    #                                 # should all be in one message
    #                                 await ctx.respond(
    #                                     f"<@&{file_check()[group]['series_list'][series]['chapter_list'][chapter]['job_list'][job]['role_id']}> {series} - {chapter} - {job}")
    #             await asyncio.sleep(3600)  # this is every hour
