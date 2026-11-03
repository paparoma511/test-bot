import os
import re
import json
import time
import sqlite3
import asyncio
import disnake
import datetime
import websockets
from disnake.ext import commands, tasks
from colorama import Fore as c

# ==================== CONFIG ====================

CONFIG_PATH = "ScpPySettings.json"

# Футер по умолчанию.
# Также настраивается через ScpPySettings.json -> Footer
DEFAULT_FOOTER = "✦ Archive SCP NoRules"

DEFAULT_CONFIG = {
    "BotToken": "Your-bot-token",
    "ServerId": 0,
    "IpAdress": "127.0.0.1",
    "Port": 9000,
    "CommandSenderRole": 0,

    "Footer": DEFAULT_FOOTER,

    # Интервалы отправки WS-логов в Discord (в секундах).
    # 0 или отсутствие ключа = отправлять мгновенно.
    # >0 = буферизировать и отправлять раз в N секунд (последнее сообщение).
    "WSLogIntervals": {
        "player_count": 120,
        "log": 0,
        "check_roles": 0,
        "command_response": 0,
        "check_roles_response": 0
    },

    "ChannelIds": {
        "CommandsLog": 0,
        "GameLogs": 0,
        "BanLogs": 0,
        "ReportLogs": 0,
        "StaffCopyLogs": 0,
        "ErrorLogs": 0,
        "WSLogs": 0,
        "CallAdmin": 0,
        "AdminStats": 0
    },

    "Messages": {
        "ConfigCreated": "Config created. Please set it up before running.",

        # ==================== WS LOGS ====================

        "WSLogTitle": "Archive SCP • WebSocket",
        "WSLogColor": 3447003,

        "WebSocketConnected": "[WS] Plugin connected from {address}",
        "WebSocketDisconnected": "[WS] Plugin disconnected",
        "WebSocketInvalidJson": "[WS] Received invalid JSON",

        # ==================== CHANNELS ====================

        "ChannelNotFound": "[WARN] Канал {channel_id} не найден. Проверьте ID.",
        "ChannelDoesNotExist": "[ERROR] Канал {channel_id} не существует.",
        "ChannelNoPermission": "[ERROR] У бота нет прав писать в канал {channel_id}.",

        # ==================== BOT ====================

        "BotConnected": "Bot connected as {bot} (Guild {server_id})",

        # ==================== REGISTER ====================

        "RegistrationInvalidSteamId": "Неверный формат SteamID. Нужно 17 цифр, например: 76561198012345678",
        "RegistrationAlreadyExists": "Вы уже зарегистрированы с SteamID: {steam_id}",
        "RegistrationSteamAlreadyUsed": "Этот SteamID уже зарегистрирован под другим пользователем.",
        "RegistrationSuccess": "Вы успешно зарегистрировались на сервере под SteamID: {steam_id}",

        # ==================== UNREGISTER ====================

        "UnregisterNotRegistered": "Вы не зарегистрированы в базе данных.",
        "UnregisterSuccess": "Вы успешно удалили свои данные из базы.",

        # ==================== DELETE ====================

        "DeleteNoPermission": "Отказано в доступе: у вас нет необходимых прав для выполнения этой команды.",
        "DeleteSuccess": "Пользователь был успешно удалён из базы данных.",
        "DeleteNotFound": "Пользователь с идентификатором {identifier} не найден в базе данных.",

        # ==================== DELETEUSER ====================

        "DeleteUserInvalidSteamId": "Неверный формат SteamID. Нужно 17 цифр, например: 76561198012345678",

        # ==================== CALL ADMIN / ADMIN STATS ====================

        "CallAdminTitle": "[AS] NoRules Вызов администратора!",
        "CallAdminDescription": "Поступил новый вызов администратора.",
        "CallAdminPlayer": "👤 Игрок",
        "CallAdminReason": "📝 Причина",
        "CallAdminAdminsOnline": "🛡️ Администраторы онлайн",
        "AdminStatsTitle": "Admin Statistics",

        # ==================== LIST ====================

        "ListTitle": "Онлайн",
        "ListEmpty": "На сервере сейчас никого нет.",
        "ListError": "Не удалось получить список игроков: {error}",
        "ListNotYours": "Эти кнопки доступны только тому, кто вызвал команду.",

        # ==================== SHOW ====================

        "ShowNoPermission": "Отказано в доступе: у вас нет необходимых прав для выполнения этой команды.",
        "ShowEmptyDatabase": "База данных пуста.",
        "ShowUser": "DiscordId: {discord_id} (<@{discord_id}>), SteamId: {steam_id}",
        "ShowNotFound": "Пользователь с идентификатором {identifier} не найден.",
        "ShowAllTitle": "Все пользователи",
        "ShowResultTitle": "Результат поиска",

        # ==================== EXECUTE ====================

        "ExecuteNotRegistered": "❌ Вы не найдены в базе данных. Пожалуйста, привяжите свой профиль.",
        "ExecuteNoPermission": "❌ У вас нет прав для использования этой команды.",
        "ExecutePluginOffline": "Плагин игрового сервера не подключен по WebSocket!",
        "ExecuteError": "Произошла ошибка: {error}",
        "ExecutePage": "✦ Archive SCP NoRules | Страница {current}/{total}",

        # ==================== STATUS ====================

        "ServerRestarting": "Сервер перезапускается или сдох :(",
        "PlayersStatus": "Игроков {players}/{max_players}",

        # ==================== CHECK ROLES ====================

        "CheckRolesUserNotFound": "User not found",
        "CheckRolesMemberNotFound": "Member not found",

        # ==================== WS ACTIONS ====================

        "WsRemoveGroup": "[WS] Отправлено remove_group для {steam_id} (снята админ-роль)",
        "WsRemoveGroupError": "[WS Error] Ошибка при отправке remove_group: {error}",

        # ==================== ERRORS ====================

        "UpdateStatusError": "update_status error: {error}",
        "SendLogError": "[ERROR] send_log_message: {error}"
    },

    "AdminGroups": {
        "adminlvla": [1124991470772948992, 1136953948801077288],
        "adminlvlb": [1180525684150517871, 1136953948801077288],
        "adminlvlc": [1124991343656181800, 1136953948801077288],
        "adminlvld": [1124991163905097848, 1136953948801077288],
        "admin": [1107351632389349454, 1136953948801077288],
        "glavb": [1149738203109138523, 1136953948801077288],
        "glav": [1114861946479587338, 1136953948801077288],
        "ruk": [1114862856396083231],
        "coo": [1266086702309576884]
    }
}


def load_or_create_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(
                DEFAULT_CONFIG,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"{c.RED}"
            f"{DEFAULT_CONFIG['Messages']['ConfigCreated']}"
            f"{c.RESET}"
        )

        exit()

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        loaded_config = json.load(f)

    changed = False

    # ==================== FOOTER ====================

    if "Footer" not in loaded_config:
        loaded_config["Footer"] = DEFAULT_FOOTER
        changed = True

    # ==================== WS LOG INTERVALS ====================

    if "WSLogIntervals" not in loaded_config:
        loaded_config["WSLogIntervals"] = DEFAULT_CONFIG["WSLogIntervals"]
        changed = True
    else:
        for key, value in DEFAULT_CONFIG["WSLogIntervals"].items():
            if key not in loaded_config["WSLogIntervals"]:
                loaded_config["WSLogIntervals"][key] = value
                changed = True

    # ==================== CHANNEL IDS ====================

    if "ChannelIds" not in loaded_config:
        loaded_config["ChannelIds"] = DEFAULT_CONFIG["ChannelIds"]
        changed = True
    else:
        for key, value in DEFAULT_CONFIG["ChannelIds"].items():
            if key not in loaded_config["ChannelIds"]:
                loaded_config["ChannelIds"][key] = value
                changed = True

    # ==================== MESSAGES ====================

    if "Messages" not in loaded_config:
        loaded_config["Messages"] = DEFAULT_CONFIG["Messages"]
        changed = True
    else:
        for key, value in DEFAULT_CONFIG["Messages"].items():
            if key not in loaded_config["Messages"]:
                loaded_config["Messages"][key] = value
                changed = True

    # ==================== ADMIN GROUPS ====================

    if "AdminGroups" not in loaded_config:
        loaded_config["AdminGroups"] = DEFAULT_CONFIG["AdminGroups"]
        changed = True

    # ==================== SAVE ====================

    if changed:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(
                loaded_config,
                f,
                indent=4,
                ensure_ascii=False
            )

    return loaded_config


config = load_or_create_config()

bot_token = config["BotToken"]
server_id = config["ServerId"]
ip_adress = config["IpAdress"]
port = config["Port"]
command_sender_role = config["CommandSenderRole"]

channel_ids = config["ChannelIds"]
admin_groups = config["AdminGroups"]

# Единый футер
FOOTER_TEXT = config.get(
    "Footer",
    DEFAULT_FOOTER
)

# Сообщения
MESSAGES = config.get(
    "Messages",
    DEFAULT_CONFIG["Messages"]
)

# Интервалы WS-логов
WS_LOG_INTERVALS = config.get(
    "WSLogIntervals",
    DEFAULT_CONFIG["WSLogIntervals"]
)


def msg(key, **kwargs):
    """
    Получение сообщения из конфигурации.

    Пример:
        msg("RegistrationSuccess", steam_id=steam_id)
    """

    text = MESSAGES.get(key, key)

    try:
        return text.format(**kwargs)

    except (KeyError, ValueError):
        return text


# ==================== GLOBALS ====================

intents = disnake.Intents.default()
intents.members = True

bot = commands.InteractionBot(
    test_guilds=[server_id],
    intents=intents
)

player_count = None
max_player_count = None
last_message_time = time.time()

ALL_ADMIN_ROLE_IDS = set()

for role_list in admin_groups.values():
    ALL_ADMIN_ROLE_IDS.update(role_list)

# Активное WebSocket-соединение
current_websocket = None

# Задача WS-сервера (чтобы не запускать второй раз)
ws_server_task = None

# Ожидающие ответы команд
pending_responses = {}

# WS-сообщения этих типов не дублируются в канал WSLogs (слишком длинные)
WS_LOG_SILENT_TYPES = {"players_response", "admin_stats"}

# Буфер WS-логов с интервалом.
# {msg_type: {"message": str, "first_at": float}}
ws_log_buffer = {}


# ==================== UTILS ====================

def update_last_message_time():
    global last_message_time
    last_message_time = time.time()


def init_database():
    with sqlite3.connect("user_data.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                discord_id INTEGER PRIMARY KEY,
                steam_id TEXT NOT NULL
            )
        """)


init_database()


def normalize_steam_id(raw: str):
    """
    Приводит SteamID к виду '<17 цифр>@steam'.
    Принимает и '76561198012345678', и '76561198012345678@steam'.
    Возвращает None, если формат неверный.
    """

    value = (raw or "").strip().lower()

    if value.endswith("@steam"):
        value = value[:-len("@steam")]

    if not re.fullmatch(r"\d{17}", value):
        return None

    return f"{value}@steam"


# Русские названия ролей SCP:SL (ключ — название роли без пробелов/дефисов, в нижнем регистре).
# Если роли нет в словаре, показывается то, что прислал плагин.
ROLE_NAMES = {
    "scp173": "SCP-173",
    "scp049": "SCP-049",
    "scp0492": "SCP-049-2",
    "scp079": "SCP-079",
    "scp096": "SCP-096",
    "scp106": "SCP-106",
    "scp939": "SCP-939",
    "scp3114": "SCP-3114",
    "classd": "Класс-D",
    "scientist": "Учёный",
    "facilityguard": "Охранник",
    "ntfprivate": "Рядовой МОГ",
    "ntfsergeant": "Сержант МОГ",
    "ntfspecialist": "Специалист МОГ",
    "ntfcaptain": "Капитан МОГ",
    "chaosconscript": "Новобранец ПХ",
    "chaosrifleman": "Стрелок ПХ",
    "chaosrepressor": "Каратель ПХ",
    "chaosmarauder": "Мародёр ПХ",
    "tutorial": "Туториал",
    "spectator": "Наблюдатель",
    "overwatch": "Overwatch",
    "filmmaker": "Режиссёр",
    "none": "Нет роли",
}


def translate_role(role) -> str:
    role = str(role or "").strip()

    if not role:
        return "—"

    key = re.sub(r"[^a-z0-9]", "", role.lower())

    return ROLE_NAMES.get(key, role)


# ==================== NORMAL LOG MESSAGE ====================

async def send_log_message(channel_id: int, message: str):
    try:
        if not message:
            return

        channel = bot.get_channel(channel_id)

        if not channel:
            channel = await bot.fetch_channel(channel_id)

        if not channel:
            print(
                msg(
                    "ChannelNotFound",
                    channel_id=channel_id
                )
            )
            return

        if len(message) > 2000:
            parts = [
                message[i:i + 2000]
                for i in range(0, len(message), 2000)
            ]

            for idx, part in enumerate(parts, start=1):
                await channel.send(
                    f"**[Part {idx}/{len(parts)}]**\n{part}"
                )

            return

        await channel.send(message)

    except disnake.NotFound:
        print(
            msg(
                "ChannelDoesNotExist",
                channel_id=channel_id
            )
        )

    except disnake.Forbidden:
        print(
            msg(
                "ChannelNoPermission",
                channel_id=channel_id
            )
        )

    except Exception as e:
        print(
            msg(
                "SendLogError",
                error=e
            )
        )


# ==================== WS EMBED LOG ====================

async def send_ws_log(message: str):
    """
    Отправляет все WS-сообщения
    в отдельный Discord-канал в виде Embed.
    """

    try:
        channel_id = channel_ids.get(
            "WSLogs",
            0
        )

        if not channel_id:
            return

        if not message:
            return

        channel = bot.get_channel(channel_id)

        if not channel:
            channel = await bot.fetch_channel(
                channel_id
            )

        if not channel:
            print(
                msg(
                    "ChannelNotFound",
                    channel_id=channel_id
                )
            )
            return

        try:
            embed_color = int(
                MESSAGES.get(
                    "WSLogColor",
                    3447003
                )
            )

        except (ValueError, TypeError):
            embed_color = 3447003

        embed = disnake.Embed(
            title=MESSAGES.get(
                "WSLogTitle",
                "Archive SCP • WebSocket"
            ),
            description=message,
            color=embed_color,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await channel.send(
            embed=embed
        )

    except disnake.NotFound:
        print(
            msg(
                "ChannelDoesNotExist",
                channel_id=channel_ids.get(
                    "WSLogs",
                    0
                )
            )
        )

    except disnake.Forbidden:
        print(
            msg(
                "ChannelNoPermission",
                channel_id=channel_ids.get(
                    "WSLogs",
                    0
                )
            )
        )

    except Exception as e:
        print(
            msg(
                "SendLogError",
                error=e
            )
        )


# ==================== PLUGIN MESSAGES (CallAdmin / AdminStat) ====================

async def get_text_channel(channel_id: int):
    channel = bot.get_channel(channel_id)

    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    return channel


async def handle_call_admin(data: dict):
    """Вызов администратора от плагина (бывший вебхук CallAdmin)."""

    try:
        channel_id = channel_ids.get("CallAdmin", 0)

        if not channel_id:
            return

        channel = await get_text_channel(channel_id)

        admins = data.get("admins") or []

        admins_text = "\n".join(
            f"{a.get('name', '?')} ({a.get('steam_id', '?')})"
            for a in admins
            if isinstance(a, dict)
        ) or "—"

        embed = disnake.Embed(
            title=msg("CallAdminTitle"),
            description=msg("CallAdminDescription"),
            color=0xFFAA00,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name=msg("CallAdminPlayer"),
            value=(
                f"{data.get('player_name', 'Unknown')} "
                f"(`{data.get('player_id', 'Unknown')}`)"
            )[:1024],
            inline=False
        )

        embed.add_field(
            name=msg("CallAdminReason"),
            value=str(data.get("reason") or "Не указана")[:1024],
            inline=False
        )

        embed.add_field(
            name=msg("CallAdminAdminsOnline"),
            value=admins_text[:1024],
            inline=False
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await channel.send(
            embed=embed,
            allowed_mentions=disnake.AllowedMentions.none()
        )

    except Exception as e:
        print(
            msg(
                "SendLogError",
                error=e
            )
        )


async def handle_admin_stats(data: dict):
    """Статистика администраторов от плагина (бывший вебхук Novace/AdminStat)."""

    try:
        channel_id = channel_ids.get("AdminStats", 0)

        if not channel_id:
            return

        lines = [
            str(line)[:3500]
            for line in (data.get("lines") or [])
        ]

        if not lines:
            return

        channel = await get_text_channel(channel_id)

        title = str(
            data.get("title")
            or msg("AdminStatsTitle")
        )[:250]

        # Один embed на сообщение: у Discord лимит 6000 символов на сообщение
        chunks = []
        current = ""

        for line in lines:

            if current and len(current) + len(line) + 1 > 3800:
                chunks.append(current)
                current = ""

            current += line + "\n"

        if current:
            chunks.append(current)

        for index, chunk in enumerate(chunks, start=1):

            embed = disnake.Embed(
                title=title if index == 1 else None,
                description=chunk,
                color=0xFFFF00,
                timestamp=datetime.datetime.now()
            )

            embed.set_footer(
                text=f"{FOOTER_TEXT} | {index}/{len(chunks)}"
            )

            await channel.send(
                embed=embed,
                allowed_mentions=disnake.AllowedMentions.none()
            )

    except Exception as e:
        print(
            msg(
                "SendLogError",
                error=e
            )
        )


# ==================== WEBSOCKET SERVER ====================

async def ws_handler(websocket):
    global current_websocket
    global player_count
    global max_player_count

    # ==================== CONNECTION LOG ====================

    ws_message = msg(
        "WebSocketConnected",
        address=websocket.remote_address
    )

    print(
        f"{c.GREEN}"
        f"{ws_message}"
        f"{c.RESET}"
    )

    asyncio.create_task(
        send_ws_log(ws_message)
    )

    current_websocket = websocket

    try:
        async for message in websocket:

            update_last_message_time()

            # ==================== JSON ====================

            try:
                data = json.loads(message)

            except json.JSONDecodeError:

                ws_message = msg(
                    "WebSocketInvalidJson"
                )

                print(ws_message)

                asyncio.create_task(
                    send_ws_log(ws_message)
                )

                continue

            # ==================== WS MESSAGE LOG ====================

            msg_type = data.get("type")

            ws_message = f"[WS] {msg_type}: {data}"

            print(ws_message)

            try:
                interval = int(
                    WS_LOG_INTERVALS.get(msg_type, 0)
                )
            except (ValueError, TypeError):
                interval = 0

            if msg_type in WS_LOG_SILENT_TYPES:

                pass

            elif interval and interval > 0:

                # Буферизируем — отправит задача ws_log_dispatcher
                entry = ws_log_buffer.get(msg_type)

                if entry is None:
                    ws_log_buffer[msg_type] = {
                        "message": ws_message,
                        "first_at": time.time()
                    }
                else:
                    entry["message"] = ws_message

            else:

                asyncio.create_task(
                    send_ws_log(ws_message)
                )

            # ==================== MESSAGE HANDLER ====================

            match msg_type:

                # ==================== COMMAND RESPONSE ====================

                case "command_response":

                    cmd_id = data.get("id")

                    if cmd_id in pending_responses:
                        pending_responses[
                            cmd_id
                        ].set_result(
                            data.get(
                                "result",
                                ""
                            )
                        )

                # ==================== CALL ADMIN ====================

                case "call_admin":

                    asyncio.create_task(
                        handle_call_admin(data)
                    )

                # ==================== ADMIN STATS ====================

                case "admin_stats":

                    asyncio.create_task(
                        handle_admin_stats(data)
                    )

                # ==================== PLAYERS LIST ====================

                case "players_response":

                    req_id = data.get("id")

                    future = pending_responses.get(req_id)

                    if future is not None and not future.done():
                        future.set_result(
                            data.get(
                                "players",
                                []
                            )
                        )

                # ==================== PLAYER COUNT ====================

                case "player_count":

                    player_count = data.get(
                        "player_count"
                    )

                    max_player_count = data.get(
                        "max_player_count"
                    )

                    await websocket.send(
                        json.dumps(
                            {
                                "status": "success"
                            }
                        )
                    )

                # ==================== CHECK ROLES ====================

                case "check_roles":

                    steam_id = data.get(
                        "steam_id"
                    )

                    response = {
                        "type": "check_roles_response",
                        "steam_id": steam_id,
                        "status": "error",
                        "message": msg(
                            "CheckRolesUserNotFound"
                        )
                    }

                    with sqlite3.connect(
                        "user_data.db"
                    ) as conn:

                        cursor = conn.execute(
                            """
                            SELECT discord_id
                            FROM user_data
                            WHERE steam_id = ?
                            """,
                            (steam_id,)
                        )

                        result = cursor.fetchone()

                    if result:

                        discord_id = result[0]

                        guild = bot.get_guild(
                            server_id
                        )

                        member = (
                            guild.get_member(
                                discord_id
                            )
                            if guild
                            else None
                        )

                        if member:

                            user_roles = {
                                role.id
                                for role in member.roles
                            }

                            if (
                                1529443858579193874
                                in user_roles
                            ):

                                response = {
                                    "type": "check_roles_response",
                                    "steam_id": steam_id,
                                    "status": "success",
                                    "roles": []
                                }

                            else:

                                matching = [
                                    k
                                    for k, ids
                                    in admin_groups.items()
                                    if all(
                                        rid in user_roles
                                        for rid in ids
                                    )
                                ]

                                response = {
                                    "type": "check_roles_response",
                                    "steam_id": steam_id,
                                    "status": "success",
                                    "roles": matching
                                }

                        else:

                            response["message"] = msg(
                                "CheckRolesMemberNotFound"
                            )

                    print(
                        f"[WS] Response {response}"
                    )

                    asyncio.create_task(
                        send_ws_log(
                            f"[WS] Response {response}"
                        )
                    )

                    await websocket.send(
                        json.dumps(
                            response
                        )
                    )

                # ==================== LOG ====================

                case "log":

                    log_type = data.get(
                        "log_type"
                    )

                    log_msg = data.get(
                        "message"
                    )

                    if (
                        log_type in channel_ids
                        and log_msg
                    ):

                        asyncio.create_task(
                            send_log_message(
                                channel_ids[
                                    log_type
                                ],
                                log_msg
                            )
                        )

                        await websocket.send(
                            json.dumps(
                                {
                                    "status": "success"
                                }
                            )
                        )

    except websockets.exceptions.ConnectionClosed:

        ws_message = msg(
            "WebSocketDisconnected"
        )

        print(
            f"{c.RED}"
            f"{ws_message}"
            f"{c.RESET}"
        )

        asyncio.create_task(
            send_ws_log(ws_message)
        )

    finally:

        if current_websocket == websocket:
            current_websocket = None


async def start_ws_server():

    print(
        f"{c.CYAN}"
        f"Starting WebSocket server on "
        f"ws://{ip_adress}:{port}"
        f"{c.RESET}"
    )

    server = await websockets.serve(
        ws_handler,
        ip_adress,
        port
    )

    await server.wait_closed()


# ==================== BOT EVENTS & TASKS ====================

@bot.event
async def on_ready():

    print(
        f"{c.GREEN}"
        f"{msg('BotConnected', bot=bot.user, server_id=server_id)}"
        f"{c.RESET}"
    )

    print(
        f"{c.CYAN}"
        f"[WS] Initializing WebSocket server task..."
        f"{c.RESET}"
    )

    # on_ready может вызываться повторно при переподключении к Discord —
    # WS-сервер второй раз запускать нельзя (порт уже занят)
    global ws_server_task

    if ws_server_task is None or ws_server_task.done():
        ws_server_task = asyncio.create_task(
            start_ws_server()
        )

    if not update_status.is_running():
        update_status.start()

    if not ws_log_dispatcher.is_running():
        ws_log_dispatcher.start()


@bot.event
async def on_member_update(
    before: disnake.Member,
    after: disnake.Member
):

    if before.guild.id != server_id:
        return

    before_roles = {
        role.id
        for role in before.roles
    }

    after_roles = {
        role.id
        for role in after.roles
    }

    removed_roles = (
        before_roles - after_roles
    )

    if not removed_roles:
        return

    if not removed_roles.intersection(
        ALL_ADMIN_ROLE_IDS
    ):
        return

    with sqlite3.connect(
        "user_data.db"
    ) as conn:

        cursor = conn.execute(
            """
            SELECT steam_id
            FROM user_data
            WHERE discord_id = ?
            """,
            (after.id,)
        )

        result = cursor.fetchone()

    if result:

        steam_id = result[0]

        global current_websocket

        if current_websocket:

            payload = {
                "type": "remove_group",
                "steam_id": steam_id
            }

            try:

                await current_websocket.send(
                    json.dumps(payload)
                )

                ws_message = msg(
                    "WsRemoveGroup",
                    steam_id=steam_id
                )

                print(
                    f"{c.YELLOW}"
                    f"{ws_message}"
                    f"{c.RESET}"
                )

                asyncio.create_task(
                    send_ws_log(ws_message)
                )

            except Exception as e:

                ws_message = msg(
                    "WsRemoveGroupError",
                    error=e
                )

                print(
                    f"{c.RED}"
                    f"{ws_message}"
                    f"{c.RESET}"
                )

                asyncio.create_task(
                    send_ws_log(ws_message)
                )


# ==================== STATUS ====================

@tasks.loop(seconds=5)
async def update_status():

    global player_count
    global max_player_count

    try:

        elapsed = (
            time.time()
            - last_message_time
        )

        if (
            elapsed > 7
            or not player_count
            or not max_player_count
        ):

            activity = disnake.Game(
                msg(
                    "ServerRestarting"
                )
            )

            await bot.change_presence(
                status=disnake.Status.dnd,
                activity=activity
            )

        else:

            activity = disnake.Game(
                msg(
                    "PlayersStatus",
                    players=player_count,
                    max_players=max_player_count
                )
            )

            status = (
                disnake.Status.online
                if int(player_count) > 0
                else disnake.Status.idle
            )

            await bot.change_presence(
                status=status,
                activity=activity
            )

    except Exception as e:

        print(
            f"{c.RED}"
            f"{msg('UpdateStatusError', error=e)}"
            f"{c.RESET}"
        )


# ==================== WS LOG DISPATCHER ====================

@tasks.loop(seconds=1)
async def ws_log_dispatcher():

    now = time.time()

    for msg_type in list(ws_log_buffer.keys()):

        try:
            interval = int(
                WS_LOG_INTERVALS.get(msg_type, 0)
            )
        except (ValueError, TypeError):
            interval = 0

        if interval <= 0:
            # Интервал убрали из конфига — сбрасываем буфер мгновенно
            entry = ws_log_buffer.pop(msg_type)
            asyncio.create_task(
                send_ws_log(entry["message"])
            )
            continue

        entry = ws_log_buffer.get(msg_type)

        if not entry:
            continue

        if now - entry["first_at"] >= interval:

            message = entry["message"]
            del ws_log_buffer[msg_type]

            asyncio.create_task(
                send_ws_log(message)
            )


# ==================== COMMANDS ====================

@bot.slash_command(
    description="Зарегистрировать SteamID (без @steam)",
    guild_ids=[server_id]
)
async def register(
    inter: disnake.ApplicationCommandInteraction,
    steam_id: str = commands.Param(
        description="SteamID64, 17 цифр (приписка @steam не нужна)"
    )
):

    # Принимаем SteamID с @steam и без — приписку добавляет бот
    normalized = normalize_steam_id(steam_id)

    if normalized is None:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "RegistrationInvalidSteamId"
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        return

    steam_id = normalized

    discord_id = inter.author.id

    conn = sqlite3.connect(
        "user_data.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT steam_id
        FROM user_data
        WHERE discord_id = ?
        """,
        (discord_id,)
    )

    existing_data = cursor.fetchone()

    if existing_data:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "RegistrationAlreadyExists",
                steam_id=existing_data[0]
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        conn.close()

        return

    cursor.execute(
        """
        SELECT discord_id
        FROM user_data
        WHERE steam_id = ?
        """,
        (steam_id,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "RegistrationSteamAlreadyUsed"
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        conn.close()

        return

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_data
        (discord_id, steam_id)
        VALUES (?, ?)
        """,
        (
            discord_id,
            steam_id
        )
    )

    conn.commit()
    conn.close()

    embed = disnake.Embed(
        title="Successfully registered!",
        description=msg(
            "RegistrationSuccess",
            steam_id=steam_id
        ),
        color=0x00FF00,
        timestamp=datetime.datetime.now()
    )

    embed.add_field(
        name="SQL value",
        value=(
            f"{discord_id} "
            f"(<@{discord_id}>): "
            f"{steam_id}"
        )
    )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    await inter.response.send_message(
        embed=embed
    )


@bot.slash_command(
    description="Удалить себя из базы данных",
    guild_ids=[server_id]
)
async def unregister(
    inter: disnake.ApplicationCommandInteraction
):

    discord_id = inter.author.id

    conn = sqlite3.connect(
        "user_data.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT steam_id
        FROM user_data
        WHERE discord_id = ?
        """,
        (discord_id,)
    )

    existing_data = cursor.fetchone()

    if not existing_data:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "UnregisterNotRegistered"
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        conn.close()

        return

    cursor.execute(
        """
        DELETE FROM user_data
        WHERE discord_id = ?
        """,
        (discord_id,)
    )

    conn.commit()
    conn.close()

    embed = disnake.Embed(
        title="Successfully unregistered!",
        description=msg(
            "UnregisterSuccess"
        ),
        color=0x00FF00,
        timestamp=datetime.datetime.now()
    )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    await inter.response.send_message(
        embed=embed
    )


@bot.slash_command(
    name="deleteuser",
    description="Удалить пользователя из базы по SteamID",
    guild_ids=[server_id]
)
async def deleteuser(
    inter: disnake.ApplicationCommandInteraction,
    steam_id: str = commands.Param(
        description="SteamID64, 17 цифр (приписка @steam не нужна)"
    )
):

    modrole = inter.author.guild.get_role(
        command_sender_role
    )

    if modrole not in inter.author.roles:

        embed = disnake.Embed(
            title="Ошибка",
            description=msg(
                "DeleteNoPermission"
            ),
            color=disnake.Color.red()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed,
            ephemeral=True
        )

        return

    normalized = normalize_steam_id(steam_id)

    if normalized is None:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "DeleteUserInvalidSteamId"
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        return

    with sqlite3.connect(
        "user_data.db"
    ) as conn:

        cursor = conn.execute(
            """
            SELECT discord_id
            FROM user_data
            WHERE steam_id = ?
            """,
            (normalized,)
        )

        row = cursor.fetchone()

        if row:

            discord_id = row[0]

            conn.execute(
                """
                DELETE FROM user_data
                WHERE steam_id = ?
                """,
                (normalized,)
            )

            conn.commit()

    if row:

        embed = disnake.Embed(
            title="Success",
            description=msg(
                "DeleteSuccess"
            ),
            color=0x00FF00,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="SQL value",
            value=(
                f"{discord_id} "
                f"(<@{discord_id}>): "
                f"{normalized}"
            )
        )

    else:

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "DeleteNotFound",
                identifier=normalized
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    await inter.response.send_message(
        embed=embed
    )


# ==================== /LIST ====================

LIST_PAGE_SIZE = 15


async def request_player_list():
    """Запрашивает у плагина список игроков, которые сейчас на сервере."""

    global current_websocket

    if not current_websocket:

        raise Exception(
            msg(
                "ExecutePluginOffline"
            )
        )

    req_id = str(
        time.time_ns()
    )

    loop = asyncio.get_running_loop()

    future = loop.create_future()

    pending_responses[
        req_id
    ] = future

    try:

        await current_websocket.send(
            json.dumps(
                {
                    "type": "get_players",
                    "id": req_id
                }
            )
        )

        return await asyncio.wait_for(
            future,
            timeout=10.0
        )

    finally:

        pending_responses.pop(
            req_id,
            None
        )


def format_player_line(player: dict) -> str:

    name = str(
        player.get("name")
        or player.get("nickname")
        or "Unknown"
    )

    steam = str(
        player.get("steam_id")
        or player.get("user_id")
        or "—"
    )

    if steam != "—" and "@" not in steam:
        steam = f"{steam}@steam"

    role = translate_role(
        player.get("role")
    )

    return f"{name} | {steam} | {role}"


class PlayerListView(disnake.ui.View):

    def __init__(
        self,
        inter: disnake.ApplicationCommandInteraction,
        players: list
    ):

        super().__init__(timeout=180)

        self.inter = inter
        self.author_id = inter.author.id
        self.lines = [
            format_player_line(p)
            for p in players
            if isinstance(p, dict)
        ]
        self.page = 0
        self.total_pages = max(
            1,
            -(-len(self.lines) // LIST_PAGE_SIZE)
        )

        self._update_buttons()

    def build_embed(self) -> disnake.Embed:

        start = self.page * LIST_PAGE_SIZE

        chunk = self.lines[
            start:start + LIST_PAGE_SIZE
        ]

        title = msg("ListTitle")

        if max_player_count:
            title = (
                f"{title} "
                f"{len(self.lines)}/{max_player_count}"
            )
        else:
            title = f"{title} {len(self.lines)}"

        embed = disnake.Embed(
            title=title,
            description=(
                "\n".join(chunk)
                if chunk
                else msg("ListEmpty")
            ),
            color=disnake.Color.green(),
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=msg(
                "ExecutePage",
                current=self.page + 1,
                total=self.total_pages
            )
        )

        return embed

    def _update_buttons(self):

        self.prev_button.disabled = self.page <= 0

        self.next_button.disabled = (
            self.page >= self.total_pages - 1
        )

    async def interaction_check(
        self,
        interaction: disnake.MessageInteraction
    ) -> bool:

        if interaction.author.id != self.author_id:

            await interaction.response.send_message(
                msg("ListNotYours"),
                ephemeral=True
            )

            return False

        return True

    @disnake.ui.button(
        label="◀",
        style=disnake.ButtonStyle.secondary
    )
    async def prev_button(
        self,
        button: disnake.ui.Button,
        interaction: disnake.MessageInteraction
    ):

        self.page = max(0, self.page - 1)

        self._update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @disnake.ui.button(
        label="▶",
        style=disnake.ButtonStyle.secondary
    )
    async def next_button(
        self,
        button: disnake.ui.Button,
        interaction: disnake.MessageInteraction
    ):

        self.page = min(
            self.total_pages - 1,
            self.page + 1
        )

        self._update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    async def on_timeout(self):

        for child in self.children:
            child.disabled = True

        try:
            await self.inter.edit_original_message(
                view=self
            )
        except Exception:
            pass


@bot.slash_command(
    name="list",
    description="Показать, кто сейчас на сервере",
    guild_ids=[server_id]
)
async def list_players(
    inter: disnake.ApplicationCommandInteraction
):

    await inter.response.defer()

    try:

        players = await request_player_list()

    except Exception as e:

        if isinstance(e, asyncio.TimeoutError):
            error_text = (
                "плагин не ответил за 10 секунд "
                "(проверь, что он поддерживает запрос get_players)"
            )
        else:
            error_text = str(e)[:3000] or type(e).__name__

        embed = disnake.Embed(
            title="Error",
            description=msg(
                "ListError",
                error=error_text
            ),
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.edit_original_message(
            embed=embed
        )

        return

    view = PlayerListView(
        inter,
        players or []
    )

    await inter.edit_original_message(
        embed=view.build_embed(),
        view=view
    )


@bot.slash_command(
    description="Показать пользователей из базы данных",
    guild_ids=[server_id]
)
async def show(
    inter: disnake.ApplicationCommandInteraction,
    string: str
):

    modrole = inter.author.guild.get_role(
        command_sender_role
    )

    if modrole not in inter.author.roles:

        embed = disnake.Embed(
            title="Ошибка",
            description=msg(
                "ShowNoPermission"
            ),
            color=disnake.Color.red()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.response.send_message(
            embed=embed
        )

        return

    conn = sqlite3.connect(
        "user_data.db"
    )

    cursor = conn.cursor()

    if string.lower() == "all":

        cursor.execute(
            """
            SELECT discord_id, steam_id
            FROM user_data
            """
        )

        users = cursor.fetchall()

        if users:

            description = "\n".join(
                [
                    msg(
                        "ShowUser",
                        discord_id=discord_id,
                        steam_id=steam_id
                    )
                    for discord_id, steam_id
                    in users
                ]
            )

        else:

            description = msg(
                "ShowEmptyDatabase"
            )

        embed = disnake.Embed(
            title=msg(
                "ShowAllTitle"
            ),
            description=description,
            color=0x00FF00,
            timestamp=datetime.datetime.now()
        )

    else:

        cursor.execute(
            """
            SELECT discord_id, steam_id
            FROM user_data
            WHERE discord_id = ?
            """,
            (string,)
        )

        user_data = cursor.fetchone()

        if not user_data:

            cursor.execute(
                """
                SELECT discord_id, steam_id
                FROM user_data
                WHERE steam_id = ?
                """,
                (string,)
            )

            user_data = cursor.fetchone()

        if user_data:

            discord_id, steam_id = user_data

            description = msg(
                "ShowUser",
                discord_id=discord_id,
                steam_id=steam_id
            )

        else:

            description = msg(
                "ShowNotFound",
                identifier=string
            )

        embed = disnake.Embed(
            title=msg(
                "ShowResultTitle"
            ),
            description=description,
            color=(
                0x00FF00
                if user_data
                else 0xFF0000
            ),
            timestamp=datetime.datetime.now()
        )

    conn.close()

    embed.set_footer(
        text=FOOTER_TEXT
    )

    await inter.response.send_message(
        embed=embed
    )


@bot.slash_command(
    description="Отправить команду плагину",
    guild_ids=[server_id]
)
async def execute(
    inter: disnake.ApplicationCommandInteraction,
    command: str
):

    user_role_ids = {
        role.id
        for role in inter.author.roles
    }

    matching_groups = [
        group_name
        for group_name, role_list
        in admin_groups.items()
        if any(
            role_id in user_role_ids
            for role_id in role_list
        )
    ]

    group = ''
    user_id = ''

    if matching_groups:

        conn = sqlite3.connect(
            "user_data.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT steam_id
            FROM user_data
            WHERE discord_id = ?
            """,
            (inter.author.id,)
        )

        result = cursor.fetchone()

        conn.close()

        if result is None:

            await inter.response.send_message(
                msg(
                    "ExecuteNotRegistered"
                ),
                ephemeral=True
            )

            return

        group = matching_groups[0]
        user_id = result[0]

    elif command_sender_role in user_role_ids:

        group = 'all'
        user_id = inter.author.id

    else:

        await inter.response.send_message(
            msg(
                "ExecuteNoPermission"
            ),
            ephemeral=True
        )

        return

    await inter.response.defer()

    try:

        response = await send_command_to_plugin(
            command,
            user_id,
            inter.author.name,
            group
        )

        print(group)

        chunk_size = 4000

        chunks = [
            response[i:i + chunk_size]
            for i in range(
                0,
                len(response),
                chunk_size
            )
        ]

        embeds = []

        for index, chunk in enumerate(chunks):

            embed = disnake.Embed(
                title=command,
                description=chunk,
                color=disnake.Color.green()
            )

            embed.set_footer(
                text=msg(
                    "ExecutePage",
                    current=index + 1,
                    total=len(chunks)
                )
            )

            embeds.append(embed)

        if len(embeds) <= 10:

            await inter.edit_original_message(
                embeds=embeds
            )

        else:

            await inter.edit_original_message(
                embeds=embeds[:10]
            )

            for i in range(
                10,
                len(embeds),
                10
            ):

                await inter.channel.send(
                    embeds=embeds[i:i + 10]
                )

    except Exception as e:

        error_text = str(e)[:3990]

        embed = disnake.Embed(
            title=command,
            description=msg(
                "ExecuteError",
                error=error_text
            ),
            color=disnake.Color.red()
        )

        embed.set_footer(
            text=FOOTER_TEXT
        )

        await inter.edit_original_message(
            embed=embed
        )


# ==================== SEND COMMAND ====================

async def send_command_to_plugin(
    command: str,
    user_id: str,
    name: str,
    group: str
):

    global current_websocket

    if not current_websocket:

        raise Exception(
            msg(
                "ExecutePluginOffline"
            )
        )

    cmd_id = str(
        time.time_ns()
    )

    payload = {
        "type": "execute_command",
        "id": cmd_id,
        "user_id": user_id,
        "nick_name": name,
        "command": command,
        "group": group
    }

    loop = asyncio.get_running_loop()

    future = loop.create_future()

    pending_responses[
        cmd_id
    ] = future

    try:

        await current_websocket.send(
            json.dumps(payload)
        )

        return await asyncio.wait_for(
            future,
            timeout=10.0
        )

    finally:

        pending_responses.pop(
            cmd_id,
            None
        )


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    bot.run(bot_token)