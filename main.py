import discord
import asyncio
import json
import os

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # from .env
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))  # from .env
DATA_FILE = "exploit_data.json"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

default_detection_settings = {
    "krnl": "med",
}

default_exploits_data = {
    "external": [
        {"name": "Matcha", "status": "undetected", "notes": "Clean and safe"},
        {"name": "Nezur", "status": "undetected", "notes": "Lightweight, secure"},
    ],
    "internal": [],
    "mobile": [],
    "macos": [],
}

detection_settings = {}
exploits_data = {}


def has_permission(message):
    if not message.guild:
        return False
    if message.author.guild_permissions.administrator:
        return True
    admin_role_name = "Admin"
    if any(role.name == admin_role_name for role in message.author.roles):
        return True
    return False


def save_data():
    global detection_settings, exploits_data
    data = {
        "detection_settings": detection_settings,
        "exploits_data": exploits_data,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_data():
    global detection_settings, exploits_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            detection_settings = data.get("detection_settings", {})
            exploits_data = data.get("exploits_data", {})
    else:
        detection_settings = default_detection_settings.copy()
        exploits_data = {k: v.copy() for k, v in default_exploits_data.items()}


def build_embeds():
    krnl_detection = detection_settings.get("krnl", "med").capitalize()
    detection_str = f"**KRNL**: Detection level set to **{krnl_detection}**"

    embed1 = discord.Embed(
        title="📋 Roblox Exploit Status - Windows DLL/API",
        description="Internal DLL/API Executors",
        color=discord.Color.red()
    )
    embed1.add_field(
        name="Executors",
        value=(
            "**Visual**: UP | Detected — No key system.\n"
            "**Wave**: UP | Very High Detection — Flagged, not recommended.\n"
            "**Solara**: UP | Detected — Maintained, frequently flagged.\n"
            "**Volcano**: UP | Medium Detection — Electron rebrand.\n"
            "**Zenith**: UP | Detected — Strong decompiler.\n"
            "**AWP (Sniper)**: DOWN — False undetected claims.\n"
            "**Ocean**: UP | Detected — Basic GUI.\n"
            "**Seliware**: UP | High Detection — Simple.\n"
            "**SirHurt**: UP | Detected — Legacy.\n"
            "**Fentanyl**: UP | Unknown — Meme name, avoid.\n"
            "**Potassium**: UP | High Detection — Similar to Wave.\n"
            "**Celery**: UP | Medium — Lightweight.\n"
            "**Swift**: UP | Medium Detection.\n"
            "**Cryptic-PC**: UP | Detected.\n"
            "**Ronix (PC)**: UP | Medium Detection.\n\n"
            + detection_str
        ),
        inline=False
    )

    external_exploits_list = exploits_data.get("external", [])
    external_value = "\n".join(
        f"**{e['name']}**: {e['status'].capitalize()} — {e['notes']}"
        for e in external_exploits_list
    ) or "No external exploits listed."

    embed2 = discord.Embed(
        title="🛡️ Roblox Exploit Status - External Executors",
        description="Driver-based (real external) exploits",
        color=discord.Color.blue()
    )
    embed2.add_field(name="Executors", value=external_value, inline=False)

    embed3 = discord.Embed(
        title="📱 Roblox Exploit Status - Android & iOS",
        description="Mobile Executors",
        color=discord.Color.green()
    )
    embed3.add_field(
        name="Android Executors",
        value=(
            "**Delta Android**: UP | Undetected — Best Android executor.\n"
            "**Ronix Android**: UP | Undetected — Reliable Delta alternative.\n"
            "**Arceus X**: UP | Very High Detection — Skidded, flagged.\n"
            "**Illusion Android**: UP | Detected — Paste, avoid.\n"
            "**Subzero Android**: DOWN — Claims bypass, still bans.\n"
            "**Frostware Android**: UP | Unknown — By nop."
        ),
        inline=False
    )
    embed3.add_field(
        name="iOS Executors",
        value=(
            "**Delta iOS**: UP | Detected — Breaks tools, best option.\n"
            "**Cryptic iOS**: Unknown — Crashes often.\n"
            "**Codex iOS**: UP | Detected — Limited compatibility.\n"
            "**Hydrogen iOS**: In Development — No data."
        ),
        inline=False
    )

    embed4 = discord.Embed(
        title="🖥️ Roblox Exploit Status - macOS + Notes",
        description="macOS Executors and Safety Notes",
        color=discord.Color.orange()
    )
    embed4.add_field(
        name="macOS Executors",
        value=(
            "**Hydrogen (Mac)**: UP | Undetected — Best free option.\n"
            "**Macsploit**: UP | High Detection — Basic, paid."
        ),
        inline=False
    )
    embed4.add_field(
        name="✅ Notes & Recommendations",
        value=(
            "- Use **Delta Android** or **Ronix Android** for mobile.\n"
            "- For driver-based execution, prefer **Matcha**, **Nezur**, or **Severe**.\n"
            "- Avoid executors like **Wave**, **Evon**, **Arceus X** — flagged/skidded.\n"
            "- Never trust executors that claim to be ‘undetectable’ with no proof.\n"
            "- Use at your own risk. Roblox bans can be hardware-level or account-linked."
        ),
        inline=False
    )

    return [embed1, embed2, embed3, embed4]


async def update_embeds(channel):
    try:
        async for msg in channel.history(limit=50):
            if msg.author == client.user:
                await msg.delete()
    except Exception as e:
        print(f"Failed to delete old embeds: {e}")

    embeds = build_embeds()
    await channel.send(embeds=embeds[:2])
    await channel.send(embeds=embeds[2:])


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    load_data()
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print("❌ Could not find the target channel.")
        return

    await update_embeds(channel)
    print("✅ Embeds loaded and sent.")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("!"):
        return

    cmd_parts = content.split(maxsplit=1)
    command = cmd_parts[0].lower()
    args_str = cmd_parts[1] if len(cmd_parts) > 1 else ""

    # Permission check for admin commands
    admin_commands = ["!setdetection", "!addexploit", "!edit", "!removeexploit"]
    if command in admin_commands:
        if not has_permission(message):
            await message.channel.send("❌ You do not have permission to use this command.")
            return

    # !setdetection <module> <low|med|high>
    if command == "!setdetection":
        parts = args_str.split()
        if len(parts) != 2:
            await message.channel.send("Usage: `!setdetection <module> <low|med|high>`")
            return
        module, level = parts
        module = module.lower()
        level = level.lower()
        valid_modules = ["krnl"]
        valid_levels = ["low", "med", "high"]
        if module not in valid_modules:
            await message.channel.send(f"Unknown detection module: `{module}`")
            return
        if level not in valid_levels:
            await message.channel.send(f"Invalid detection level: `{level}`. Choose low, med, or high.")
            return
        detection_settings[module] = level
        save_data()
        await message.channel.send(f"Detection level for `{module}` set to `{level}`.")
        channel = message.guild.get_channel(TARGET_CHANNEL_ID)
        if channel:
            await update_embeds(channel)
        return

    # !addexploit <category> <name> <status> <notes>
    if command == "!addexploit":
        parts = args_str.split(maxsplit=3)
        if len(parts) < 4:
            await message.channel.send("Usage: `!addexploit <category> <name> <status
