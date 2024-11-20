import discord
from discord.ext import commands
from discord import ui
import os
import mimetypes
import asyncio
from collections import defaultdict
import cachetools
import typing
from datetime import datetime, timedelta

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Cache for storing file locations (filename -> list of file info)
# TTL of 1 hour, max size of 1000 entries
file_cache = cachetools.TTLCache(maxsize=1000, ttl=3600)

# Cache for storing channel permissions (channel_id -> can_read)
# TTL of 5 minutes, max size of 100 entries
permission_cache = cachetools.TTLCache(maxsize=100, ttl=300)

class DownloadButton(discord.ui.View):
    def __init__(self, url: str, filename: str):
        super().__init__(timeout=600)  # 10 minute timeout
        self.add_item(discord.ui.Button(
            label=f"Download {filename}",
            style=discord.ButtonStyle.primary,
            url=url
        ))

class FileSearcher:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.found_files = []
        
    async def can_read_channel(self, channel: discord.TextChannel) -> bool:
        """Check if bot can read channel with caching"""
        channel_id = channel.id
        if channel_id in permission_cache:
            return permission_cache[channel_id]
        
        permissions = channel.permissions_for(self.guild.me)
        can_read = permissions.read_messages and permissions.read_message_history
        permission_cache[channel_id] = can_read
        return can_read

    async def search_channel(self, channel: discord.TextChannel, filename: str, limit: int = 200) -> None:
        """Search a single channel for files"""
        if not await self.can_read_channel(channel):
            return

        try:
            async for message in channel.history(limit=limit):
                for attachment in message.attachments:
                    if attachment.filename.lower() == filename.lower():
                        self.found_files.append({
                            'channel': channel,
                            'message': message,
                            'attachment': attachment
                        })
        except discord.errors.Forbidden:
            pass
        except Exception as e:
            print(f"Error searching in {channel.name}: {e}")

    async def search_all_channels(self, filename: str) -> list:
        """Search all channels concurrently"""
        # Check cache first
        cache_key = f"{self.guild.id}:{filename.lower()}"
        if cache_key in file_cache:
            return file_cache[cache_key]

        # Create tasks for each channel
        tasks = [
            self.search_channel(channel, filename)
            for channel in self.guild.text_channels
        ]
        
        # Run all searches concurrently
        await asyncio.gather(*tasks)
        
        # Cache results
        if self.found_files:
            file_cache[cache_key] = self.found_files
            
        return self.found_files

async def delete_messages(messages: list[discord.Message], delay: int):
    """Delete messages after delay"""
    if not messages:
        return
        
    await asyncio.sleep(delay)
    
    # Batch delete if possible
    if len(messages) <= 100 and all(m.channel.id == messages[0].channel.id for m in messages):
        try:
            await messages[0].channel.delete_messages(messages)
            return
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass
    
    # Fall back to individual deletion
    for message in messages:
        try:
            await message.delete()
        except (discord.errors.NotFound, discord.errors.Forbidden):
            pass

@bot.command(name='downloadfile', aliases=['findfile'])
async def download_file(ctx: commands.Context, filename: str, *args):
    """Advanced file search and download command"""
    messages_to_delete = [ctx.message]
    use_button = bool(args and args[0].lower() == "download")
    deletion_time = 10 if use_button else 30
    
    try:
        # Send initial status
        status_msg = await ctx.send("🔍 Searching...")
        messages_to_delete.append(status_msg)
        
        # Initialize and run search
        searcher = FileSearcher(ctx.guild)
        found_files = await searcher.search_all_channels(filename)
        
        if not found_files:
            await status_msg.edit(content=f"❌ No files named '{filename}' found.")
            await delete_messages(messages_to_delete, 5)
            return

        # Update status with file count
        await status_msg.edit(content=f"✅ Found {len(found_files)} instance(s) of {filename}")
        
        # Process results
        for idx, file_info in enumerate(found_files, 1):
            if use_button:
                button_view = DownloadButton(file_info['attachment'].url, filename)
                file_msg = await ctx.send(
                    f"📁 **{filename}** (Found in {file_info['channel'].mention})",
                    view=button_view
                )
                messages_to_delete.append(file_msg)
            else:
                embed = discord.Embed(
                    title=f"📁 File Found: {filename} (Instance {idx})",
                    color=discord.Color.green()
                ).add_field(
                    name="Channel", value=file_info['channel'].mention, inline=True
                ).add_field(
                    name="Uploaded By", value=file_info['message'].author.mention, inline=True
                ).add_field(
                    name="Upload Date", 
                    value=file_info['message'].created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    inline=True
                ).add_field(
                    name="File Size",
                    value=f"{file_info['attachment'].size:,} bytes",
                    inline=True
                ).add_field(
                    name="File Type",
                    value=file_info['attachment'].content_type or "Unknown",
                    inline=True
                )
                
                download_msg = await ctx.send(embed=embed)
                download_link_msg = await ctx.send(
                    f"📥 Direct Download Link: {file_info['attachment'].url}"
                )
                messages_to_delete.extend([download_msg, download_link_msg])
        
        # Schedule cleanup
        bot.loop.create_task(delete_messages(messages_to_delete, deletion_time))
        
    except Exception as e:
        error_msg = await ctx.send(f"An error occurred: {str(e)}")
        messages_to_delete.append(error_msg)
        await delete_messages(messages_to_delete, 5)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name} (ID: {bot.user.id})')
    
@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    messages_to_delete = [ctx.message]
    
    if isinstance(error, commands.MissingRequiredArgument):
        error_msg = await ctx.send("Usage: !downloadfile <filename> [download]")
    else:
        error_msg = await ctx.send(f"Error: {error}")
    
    messages_to_delete.append(error_msg)
    await delete_messages(messages_to_delete, 5)

def main():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    bot.run(token)

if __name__ == "__main__":
    main()
