import dependencies as deps
from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv
import aiohttp
import discord as ds
import discord.abc as ds_abc
import classes as cls
import logging
from sqlite3 import connect as con
from sqlite3 import Row

def sql_creates():
    try:
        with deps.main_db as connect:
            cursor = connect.cursor()

            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS "messages" (
                                "original"	TEXT,
                                "anothers"	TEXT
                            )
                        """)

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "shares" (
                                "name"	TEXT UNIQUE,
                                "description"	TEXT,
                                "channels"	TEXT,
                                "guilds"	TEXT,
                                "bots"	TEXT DEFAULT NULL
                            );
                            """)
            
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "guild-partner" (
                                "name"	TEXT,
                                "description"	TEXT,
                                "piar_text"	TEXT,
                                "channel_id"	INTEGER,
                                "marks"	TEXT,
                                "id"	INTEGER UNIQUE
                            );
                           """)

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "users" (
                                "user_id"	TEXT UNIQUE,
                                "muted_up"	TEXT,
                                "where_muted"	TEXT
                            )
                        """)
            connect.commit()
            cursor.close()
        
        with deps.economic_db as connect:
            cursor = connect.cursor()

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "user_balances" (
                                "user_id"	INTEGER UNIQUE,
                                "money"	INTEGER
                            );
                           """)
            
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "guild_balances" (
                                "guild_id"	INTEGER UNIQUE,
                                "balance"	INTEGER
                            );
                           """)
            
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS "shop" (
                                "guild_id"	INTEGER,
                                "item_name"	TEXT,
                                "item_id"	INTEGER UNIQUE,
                                "description"	TEXT,
                                "price"	INTEGER,
                                "currency"	TEXT NOT NULL DEFAULT 'k'
                            );
                           """)
            connect.commit()
            cursor.close()
    except Exception as e:
        logging.error(f'Ошибка при создании таблиц: {e}')
        return

def firstConfig():
    load_dotenv()

    # deps.intents = ds.Intents()
    # deps.intents.members = True
    # deps.intents.message_content = True
    # deps.intents.dm_messages = True
    # deps.intents.guild_messages = True
    # deps.intents.webhooks = True
    deps.intents = ds.Intents.all()


    deps.PREFIX = ('stc ', 'stc.', 'stc. ', '$$', '$$ ', ';;', ';; ', '₽₽', '₽₽ ', '₴₴', '₴₴ ')
    # deps.PREFIX = ('voulran ', 'voulran')
    deps.automod_exceptions = ('https://cdn.discordapp.com/', 'https://tenor.com/', 'https://youtube.com/')
    deps.commission = 0.3

    deps.bot = deps.Bot(command_prefix=deps.PREFIX, intents=deps.intents, help_command=None)
    deps.TOKEN = getenv('TOKEN') # TOKEN HERE
    deps.version = '1.0.1'

    test_mode = 'test_mode_'
    deps.DATABASE_MAIN_PATH      =  'databases/' + 'main.db'
    deps.DATABASE_ECONOMIC_PATH  =  'databases/economic.db'
    deps.main_db                 =  con(deps.DATABASE_MAIN_PATH, check_same_thread=False)
    deps.economic_db             =  con(deps.DATABASE_ECONOMIC_PATH, check_same_thread=False)
    deps.main_db.row_factory     =  Row
    deps.economic_db.row_factory =  Row
    sql_creates()

    ds.Member.from_capital      = cls.NewMember.from_capital
    ds.Member.is_a_transguild   = cls.NewMember.is_a_transguild
    ds.Member.is_m_transguild   = cls.NewMember.is_m_transguild
    ds.Member.is_a_shop         = cls.NewMember.is_a_shop
    ds.Member.is_OPSK           = cls.NewMember.is_OPSK
    ds.Member.is_citadel_leader = cls.NewMember.is_citadel_leader
    ds.Member.muted             = cls.NewMember.muted
    ds.Member.where_muted       = cls.NewMember.where_muted
    ds.Member.mute_web          = cls.NewMember.mute_web
    ds.Member.unmute_web        = cls.NewMember.unmute_web
    ds.Member.get_money         = cls.NewMember.get_money
    ds.Member.set_money         = cls.NewMember.set_money
    ds.Member.add_money         = cls.NewMember.add_money
    ds.Member.blocked_by        = cls.NewMember.blocked_by
    ds.Member.set_blocked_by    = cls.NewMember.set_blocked_by
    ds.Member.add_blocked_by    = cls.NewMember.add_blocked_by
    ds.Member.remove_blocked_by = cls.NewMember.remove_blocked_by
    

    ds.User.from_capital        = cls.NewUser.from_capital
    ds.User.is_a_transguild     = cls.NewUser.is_a_transguild
    ds.User.is_m_transguild     = cls.NewUser.is_m_transguild
    ds.User.is_a_shop           = cls.NewUser.is_a_shop
    ds.User.is_OPSK             = cls.NewUser.is_OPSK
    ds.User.is_citadel_leader   = cls.NewUser.is_citadel_leader
    ds.User.muted               = cls.NewUser.muted
    ds.User.where_muted         = cls.NewUser.where_muted
    ds.User.mute_web            = cls.NewUser.mute_web
    ds.User.unmute_web          = cls.NewUser.unmute_web
    ds.User.get_money           = cls.NewUser.get_money
    ds.User.set_money           = cls.NewUser.set_money
    ds.User.add_money           = cls.NewUser.add_money
    ds.User.blocked_by          = cls.NewUser.blocked_by
    ds.User.set_blocked_by      = cls.NewUser.set_blocked_by
    ds.User.add_blocked_by      = cls.NewUser.add_blocked_by
    ds.User.remove_blocked_by   = cls.NewUser.remove_blocked_by



    ds.Guild.get_money          = cls.NewGuild.get_money
    ds.Guild.set_money          = cls.NewGuild.set_money
    ds.Guild.add_money          = cls.NewGuild.add_money
    ds.Guild.guild_partner      = cls.NewGuild.guild_partner


    ds_abc.GuildChannel.get_all_webs = cls.New_TextChannel.get_all_webs

    deps.Web                    =   cls.Web
    deps.WebhookMessageSended   =   cls.WebhookMessageSended
    deps.WebhookMessagesSended  =   cls.WebhookMessagesSended
    deps.ShopItem               =   cls.ShopItem
    deps.GuildShopItems         =   cls.GuildShopItems
    deps.Shop                   =   cls.Shop
    deps.ItemsView              =   cls.ItemsView
    deps.GuildPartner           =   cls.GuildPartner

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def secondConfig():
    deps.global_http  = aiohttp.ClientSession()
    deps.second_http  = aiohttp.ClientSession()
    deps.capital      = await deps.bot.fetch_guild      (1473038842704429180)
    deps.a_transguild = await deps.capital.fetch_role   (1476193110592716880)
    deps.m_transguild = await deps.capital.fetch_role   (1476633956945363196)
    deps.a_shop       = await deps.capital.fetch_role   (1476896358542741639)
    deps.OPSK_role    = await deps.capital.fetch_role   (1483718963283099649)
    deps.leader_role  = await deps.capital.fetch_role   (1473362769599528992)
    deps.economicLogs = await deps.capital.fetch_channel(1479402331241189408)
    deps.mutesLogs    = await deps.capital.fetch_channel(1490670194107093115)
