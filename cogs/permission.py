import json
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup


def setup(bot):
    bot.add_cog(Permissions(bot))


def file_check():  # check if file exists, if not create it
    try:
        with open('permissions.json', 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        write_permissions({'owners': [], 'managers': [], 'members': []})


def write_permissions(data):  # writes to file
    with open('permissions.json', 'w') as json_file:
        json.dump(data, json_file)


def get_members(permission_group):
    return file_check().get(permission_group, [])  # returns list of members in permission group


def add_user(user: int, permission_group):  # adds user to permission group
    data = file_check()
    data[permission_group].append(user)
    write_permissions(data)


def delete_user(user: int, permission_group):  # deletes user from permission group
    data = file_check()
    data[permission_group].remove(user)
    write_permissions(data)


def check(user_id: int, permission_group):  # checks if user is in permission group
    return user_id in get_members(permission_group)


def get_groups():  # returns list of permission groups
    return list(file_check().keys())


def multiple_check(user_id: int, allowed_groups: list):
    for a in allowed_groups:
        if check(user_id, a):
            return True
    return False


file_check()  # DO NOT REMOVE UNLESS NECESSARY


class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    Permissions = SlashCommandGroup(name='permissions', description='Commands for managing permissions')

    @Permissions.command(name='list', description='Lists all users in a permission group')
    async def list(self,
                   ctx,
                   permission_group: discord.Option(str, choices=['owners', 'managers', 'members'])):
        if multiple_check(ctx.user.id, ['owners', 'managers', 'members']):  # permission check
            if permission_group in get_groups():
                members = []
                for member in get_members(permission_group):
                    members.append(self.bot.get_user(member).name)
                await ctx.respond(f'Users in {permission_group}: {members}')
            else:
                await ctx.respond(f'{permission_group} does not exist.')
        else:
            await ctx.respond('You are not authorized to perform this command.')

    @Permissions.command(name='add', description='Adds a user to a permission group')
    async def add(self,
                  ctx,
                  user: discord.User,
                  permission_group: discord.Option(str, choices=['owners', 'managers', 'members'])):
        if multiple_check(ctx.user.id, ['owners']):
            if permission_group in get_groups():
                add_user(user.id, permission_group)
                await ctx.respond(f'{user.name} has been added to {permission_group}.')
            else:
                await ctx.respond(f'{permission_group} does not exist.')
        else:
            await ctx.respond('You are not authorized to perform this command.')

    @Permissions.command(name='remove', description='Removes a user from a permission group')
    async def remove(self,
                     ctx,
                     user: discord.User,
                     permission_group: discord.Option(str, choices=['owners', 'managers', 'members'])):
        if multiple_check(ctx.user.id, ['owners']):
            if permission_group in get_groups():
                delete_user(user.id, permission_group)
                await ctx.respond(f'{user.name} has been removed from {permission_group}.')
            else:
                await ctx.respond(f'{permission_group} does not exist.')
        else:
            await ctx.respond('You are not authorized to perform this command.')

    @Permissions.command(name='check', description='checks all permission groups a user is in')
    async def check(self, ctx, user: discord.User):
        if multiple_check(ctx.user.id, ['owners', 'managers', 'members']):
            groups = []
            for group in get_groups():
                if check(user.id, group):
                    groups.append(group)
            await ctx.respond(f'{user.name} is in: {groups}')
        else:
            await ctx.respond('You are not authorized to perform this command.')
