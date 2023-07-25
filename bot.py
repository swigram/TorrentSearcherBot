from swibots import BotApp, RegisterCommand, BotContext, CommandEvent, InlineKeyboardButton, InlineMarkup, filters, CallbackQueryEvent
from tpblite import TPB
from logging import INFO, basicConfig, getLogger
from traceback import format_exc
import os

BOT_TOKEN = ""

basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] : %(message)s",
    level=INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
LOGS = getLogger(__name__)


try:
    LOGS.info("Trying Connect With Switch")
    bot = BotApp(BOT_TOKEN, "Torrent Searcher")
    LOGS.info("Successfully Connected with Switch")
    LOGS.info("Initialisation Torrent Searcher Client")
    torrent_searcher = TPB()
    LOGS.info("Initialised Torrent Searcher Client")
except Exception as e:
    LOGS.critical(str(e))
    exit()

# Registering Switch Commands

bot.register_command([
    RegisterCommand("torrents", "To Search On Torrents", True),
    RegisterCommand("besttorrent", "ToGet Best Torrent", True),
])

DATA = {}
FORMAT = """
*Torrent Title:* *{title}*

*Uploader:* `{uploader}`
*File Size:* `{filesize}`
*Number of Seeders:* `{seeders}`
*Number of Leechers:* `{leechers}`
"""

@bot.on_command("torrents")
async def src_tor(ctx: BotContext[CommandEvent]):
    event = ctx.event.message
    if not ctx.event.params.strip():
        return await event.reply_text("`Query Not Found!!`")
    xn = await event.reply_text("`Processing...`")
    torrents = torrent_searcher.search(ctx.event.params.strip())
    if len(torrents) == 0 or not torrents:
        return await xn.edit_text("`No Result Found!!!`")
    results = []
    for torrent in torrents:
        text = FORMAT.format(
            title=torrent.title,
            uploader=torrent.uploader,
            filesize=torrent.filesize,
            seeders=torrent.seeds,
            leechers=torrent.leeches
        )
        results.append([text, torrent.magnetlink])
    if len(results) > 1:
        DATA[int(event.id)] = results
        result = results[0]
        btn = [
            [InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_0_{event.id}_{event.user_id}")],
            [
                # InlineKeyboardButton("<< Back", callback_data=f"back_0_{event.id}_{event.user_id}"),
                InlineKeyboardButton("Next >>", callback_data=f"next_0_{event.id}_{event.user_id}")
            ]
        ]
        return await xn.edit_text(result[0], inline_markup=InlineMarkup(inline_keyboard=btn))
    result = results[0]
    await xn.edit_text(result[0], inline_markup=InlineMarkup([[InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_{id}_{event.id}_{event.user_id}")]]))

@bot.on_command("besttorrent")
async def best_src_tor(ctx: BotContext[CommandEvent]):
    event = ctx.event.message
    if not ctx.event.params.strip():
        return await event.reply_text("`Query Not Found!!`")
    xn = await event.reply_text("`Processing...`")
    torrents = torrent_searcher.search(ctx.event.params.strip())
    torrent  = torrents.getBestTorrent()
    text = FORMAT.format(
        title=torrent.title,
        uploader=torrent.uploader,
        filesize=torrent.filesize,
        seeders=torrent.seeds,
        leechers=torrent.leeches
    )
    # await xn.edit_text(text, inline_markup=InlineMarkup([[InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_{id}_{msg_id}_{user_id}")]]))


@bot.on_callback_query(filters.regexp(r"back_"))
async def _bck(ctx: BotContext[CallbackQueryEvent]):
    query = ctx.event.callback_data
    user = ctx.event.message.user.id
    spl = query.split("_")
    index, msg_id, user_id = int(spl[1]), int(spl[2]), int(spl[3])
    if int(user) != user_id:
        return
    if index > 0:
        results = DATA[msg_id]
        id  = index - 1
        if id == 0:
            result = results[id]
            btn = [
                [InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_{id}_{msg_id}_{user_id}")],
                [
                    InlineKeyboardButton("Next >>", callback_data=f"next_{id}_{msg_id}_{user_id}")
                ]
            ]
        else:
            result = results[id]
            btn = [
                [InlineKeyboardButton("Manget Link 🔗", url= result[1])],
                [
                    InlineKeyboardButton("<< Back", callback_data=f"back_{id}_{msg_id}_{user_id}"),
                    InlineKeyboardButton("Next >>", callback_data=f"next_{id}_{msg_id}_{user_id}")
                ]
            ]
        return await ctx.event.message.edit_text(result[0], InlineMarkup(inline_keyboard=btn))


@bot.on_callback_query(filters.regexp(r"next_"))
async def _nxt(ctx: BotContext[CallbackQueryEvent]):
    query = ctx.event.callback_data
    user = ctx.event.message.user.id
    spl = query.split("_")
    index, msg_id, user_id = int(spl[1]), int(spl[2]), int(spl[3])
    if int(user) != user_id:
        return print(user, user_id)
    results = DATA[msg_id]
    id  = index + 1
    result = results[id]
    if results[-1] == result:
        btn = [
            [InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_{id}_{msg_id}_{user_id}")],
            [
                InlineKeyboardButton("<< Back", callback_data=f"back_{id}_{msg_id}_{user_id}"),
            ]
        ]
    else:
        btn = [
            [InlineKeyboardButton("Manget Link 🔗", callback_data=f"link_{id}_{msg_id}_{user_id}")],
            [
                InlineKeyboardButton("<< Back", callback_data=f"back_{id}_{msg_id}_{user_id}"),
                InlineKeyboardButton("Next >>", callback_data=f"next_{id}_{msg_id}_{user_id}")
            ]
        ]
    return await ctx.event.message.edit_text(result[0], InlineMarkup(inline_keyboard=btn))

@bot.on_callback_query(filters.regexp(r"link_"))
async def _lnk(ctx: BotContext[CallbackQueryEvent]):
    query = ctx.event.callback_data
    user = ctx.event.message.user.id
    spl = query.split("_")
    index, msg_id, user_id = int(spl[1]), int(spl[2]), int(spl[3])
    if int(user) != user_id:
        return print(user, user_id)
    results = DATA[msg_id]
    result = results[index]
    btn = [[
        InlineKeyboardButton("<< Back", callback_data=f"back_{index+1}_{msg_id}_{user_id}")
    ]]
    return await ctx.event.message.edit_text(result[1], InlineMarkup(inline_keyboard=btn))
    

bot.run()