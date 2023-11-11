import discord
import ast
import os
import time
import datetime
from discord import app_commands
from discord.ext import commands

load_dotenv()

class Color:
    # Text
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    # Formatting
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    CONCEALED = "\033[8m"

intents = discord.Intents.all()
bot = commands.AutoShardedBot(intents=intents, command_prefix=commands.when_mentioned_or("nexus$"))
tree = bot.tree
token = os.getenv("DSC_TOKEN")
ownerid = int(os.getenv("OWNER_ID"))

@bot.event
async def on_ready():
    global utime
    utime = time.time()
    gs = bot.guilds
    gc = len(gs)
    mc = 0
    for g in gs:
        mc = mc + len(g.members)

    print(f"{Color.GREEN}[SUCCESS]{Color.CYAN} Logged in as {Color.BOLD}{bot.user.name}{Color.RESET}{Color.CYAN} at ID {Color.BOLD}{bot.user.id}{Color.RESET}{Color.CYAN}.\nIn {Color.BOLD}{gc}{Color.RESET}{Color.CYAN} guilds\nwith {Color.BOLD}{mc}{Color.RESET}{Color.CYAN} total members.\nShard count is {Color.BOLD}{bot.shard_count}{Color.RESET}{Color.CYAN}.\nInvite: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands{Color.RESET}")


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def is_owner(ctx: commands.Context):
    return ctx.author.id == 1092444113082785812

@bot.command(name="eval")
@commands.check(is_owner)
async def evalcmd(ctx: commands.Context, *, cmd: str):
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
    body = f"async def _eval_expr_():\n{cmd}"
    parsed = ast.parse(body)
    body = parsed.body[0].body
    insert_returns(body)
    env = {
        'bot': bot,
        'discord': discord,
        'ctx': ctx,
        'os': os,
        'tree': tree,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)
    try:
        result = (await eval(f"{fn_name}()", env))
    except Exception as e:
        result = f"Exception:\n{e}"
    result = f"```\n{result}\n```"
    await ctx.channel.send(result)

@bot.command(name="sync")
@commands.check(is_owner)
async def sync(ctx: commands.Context):
    print(f"{Color.CYAN}[INFO] {Color.RESET}Syncing Tree")
    await ctx.send("Syncing...")
    await tree.sync()
    await ctx.send("Synced!")
    print(f"{Color.GREEN}[SUCCESS] {Color.RESET}Tree Synced")

@bot.command(name="syncguild")
@commands.check(is_owner)
async def sync(ctx: commands.Context):
    print(f"{Color.CYAN}[INFO] {Color.RESET}Syncing Guild {ctx.guild.id}")
    await ctx.send(f"Syncing guild {ctx.guild.id}...")
    await tree.sync(guild=discord.Object(id=ctx.guild.id))
    await ctx.send("Synced!")
    print(f"{Color.GREEN}[SUCCESS] {Color.RESET}Tree Synced")


@tree.command(name="ping", description="Get the ping of the bot.")
async def ping(ctx: discord.Interaction):
    p = round(bot.latency * 1000)
    ut = str(datetime.timedelta(seconds=int(round(time.time()-utime))))
    await ctx.response.send_message(f"Pong!\nLatency is {p}ms.\nUptime is {ut} (H:M:S).")

async def on_tree_error(ctx, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await ctx.response.send_message(f"This command is on cooldown! Retry in {error.retry_after:.2f} second(s).")
        return
    elif isinstance(error, app_commands.MissingPermissions):
        await ctx.response.send_message("You do not have permission to execute this command.")
        return
    elif isinstance(error, app_commands.CheckFailure):
        await ctx.response.send_message("You do not have permission to execute this command.")
        return
    print(f"{Color.RED}[ERROR] {Color.RED}{error}\n[TRACEBACK]{Color.RESET}")
    traceback.print_tb(error.__traceback__)
    try:
        await ctx.response.send_message("There was an error while running this command. The error was logged and sent to developers.", ephemeral=True)
    except:
        await ctx.edit_original_response(content="There was an error while running this command. The error was logged and sent to developers.")
tree.on_error = on_tree_error

async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to execute this command.")
        return
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to execute this command.")
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing a required argument.")
        return
    print(f"{Color.RED}[ERROR] {Color.RED}{error}\n[TRACEBACK]{Color.RESET}")
    traceback.print_tb(error.__traceback__)
    await ctx.send("There was an error while running this command. The error was logged and sent to developers.")
bot.on_command_error = on_command_error

bot.run(token)
