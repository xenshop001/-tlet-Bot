import discord
from discord import app_commands
import os


BOT_TOKEN = ""
GUILD_ID = 1389619560365166753

PLAYER_ROLE_ID = 1391553353120612382
DEV_ROLE_ID = 1391553312205181088
SUGGESTION_CHANNEL_ID = 1400574508217405441

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def has_role(role_id):
    def predicate(interaction: discord.Interaction):
        return any(role.id == role_id for role in interaction.user.roles)
    return app_commands.check(predicate)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'A bot bejelentkezve: {client.user}')

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Nincs jogosultságod ehhez a parancshoz.",
                ephemeral=True
            )
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"Egy váratlan hiba történt: {error}",
                ephemeral=True
            )
        print(f"Hiba: {error}")

@tree.command(name="otlet", description="Küldj be egy ötletet a szerverre.", guild=discord.Object(id=GUILD_ID))
@has_role(PLAYER_ROLE_ID)
async def otlet(interaction: discord.Interaction, otlet: str):
    if interaction.channel.id != SUGGESTION_CHANNEL_ID:
        await interaction.response.send_message(
            f"Ezt a parancsot csak a <#{SUGGESTION_CHANNEL_ID}> csatornában használhatod.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="Új ötlet érkezett!",
        description=otlet,
        color=discord.Color.blue()
    )
    embed.set_author(name=f"Beküldő: {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
    embed.set_footer(text=f"ID: {interaction.user.id}")

    suggestion_channel = client.get_channel(SUGGESTION_CHANNEL_ID)
    if suggestion_channel:
        sent_embed = await suggestion_channel.send(embed=embed)
        await sent_embed.add_reaction("✅")
        await sent_embed.add_reaction("❌")
    
    await interaction.followup.send(
        f"Köszönjük az ötleted, <@{interaction.user.id}>! Sikeresen továbbítottam a fejlesztő felé.",
        ephemeral=True
    )

@tree.command(name="jovahagy", description="Jóváhagy egy beküldött ötletet.", guild=discord.Object(id=GUILD_ID))
@has_role(DEV_ROLE_ID)
async def jovahagy(interaction: discord.Interaction, uzenet_id: str):
    try:
        message = await interaction.channel.fetch_message(int(uzenet_id))
        embed = message.embeds[0]
        original_sender_id = embed.footer.text.replace("ID: ", "")
        original_sender = await client.fetch_user(int(original_sender_id))

        response_embed = discord.Embed(
            title="✅ Ötletedet jóváhagytuk!",
            description=f"A fejlesztők elfogadták a következő ötletedet:\n\n> {embed.description}",
            color=discord.Color.green()
        )
        await original_sender.send(embed=response_embed)

        embed.color = discord.Color.green()
        embed.title = "✅ Ötlet elfogadva!"
        await message.edit(embed=embed)

        await interaction.response.send_message("Az ötlet sikeresen jóváhagyva és a felhasználó értesítve.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("Hiba: Az üzenet nem található. Kérlek, add meg a megfelelő üzenet ID-t.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Hiba történt: {e}", ephemeral=True)

@tree.command(name="elutasit", description="Elutasít egy beküldött ötletet.", guild=discord.Object(id=GUILD_ID))
@has_role(DEV_ROLE_ID)
async def elutasit(interaction: discord.Interaction, uzenet_id: str):
    try:
        message = await interaction.channel.fetch_message(int(uzenet_id))
        embed = message.embeds[0]
        original_sender_id = embed.footer.text.replace("ID: ", "")
        original_sender = await client.fetch_user(int(original_sender_id))
        
        response_embed = discord.Embed(
            title="❌ Ötletedet elutasítottuk.",
            description=f"Sajnos a fejlesztők nem fogadták el a következő ötletedet:\n\n> {embed.description}",
            color=discord.Color.red()
        )
        await original_sender.send(embed=response_embed)
        
        embed.color = discord.Color.red()
        embed.title = "❌ Ötlet elutasítva"
        await message.edit(embed=embed)

        await interaction.response.send_message("Az ötlet sikeresen elutasítva és a felhasználó értesítve.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("Hiba: Az üzenet nem található. Kérlek, add meg a megfelelő üzenet ID-t.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Hiba történt: {e}", ephemeral=True)

client.run(BOT_TOKEN)