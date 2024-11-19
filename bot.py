import discord
import os
import mimetypes
import asyncio
from discord.ext import commands

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

async def delete_messages(messages, delay):
    """
    Helper function to delete messages after a specified delay
    """
    await asyncio.sleep(delay)
    try:
        for message in messages:
            await message.delete()
    except discord.errors.NotFound:
        # Message already deleted
        pass
    except discord.errors.Forbidden:
        print("Bot lacks permission to delete messages")

@bot.command(name='downloadfile')
async def download_file(ctx, filename):
    """
    Advanced file search and download command with auto-delete
    """
    # Store messages to be potentially deleted
    messages_to_delete = [ctx.message]
    
    try:
        # Confirm command usage
        status_msg = await ctx.send(f"🔍 Searching for file: {filename}")
        messages_to_delete.append(status_msg)
        
        # Tracks found files
        found_files = []
        
        # Iterate through all text channels in the server
        for channel in ctx.guild.text_channels:
            try:
                # Scan recent messages (last 200 to increase chances)
                async for message in channel.history(limit=200):
                    # Check message attachments
                    for attachment in message.attachments:
                        if attachment.filename.lower() == filename.lower():
                            # Collect file details
                            found_files.append({
                                'channel': channel,
                                'message': message,
                                'attachment': attachment
                            })
            except Exception as e:
                print(f"Error searching in {channel.name}: {e}")
        
        # Process found files
        if found_files:
            # Edit status message
            await status_msg.edit(content=f"✅ Found {len(found_files)} instance(s) of {filename}")
            
            # Send details and download links for each found file
            for idx, file_info in enumerate(found_files, 1):
                channel = file_info['channel']
                attachment = file_info['attachment']
                message = file_info['message']
                
                # Create embed with file details and download instructions
                embed = discord.Embed(
                    title=f"📁 File Found: {filename} (Instance {idx})",
                    color=discord.Color.green()
                )
                
                # Add file metadata
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Uploaded By", value=message.author.mention, inline=True)
                embed.add_field(name="Upload Date", value=message.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                
                # File size and type
                embed.add_field(name="File Size", value=f"{attachment.size:,} bytes", inline=True)
                embed.add_field(name="File Type", value=attachment.content_type or "Unknown", inline=True)
                
                # Send embed with download link
                download_msg = await ctx.send(embed=embed)
                download_link_msg = await ctx.send(f"📥 Direct Download Link: {attachment.url}")
                
                # Add these messages to deletion list
                messages_to_delete.extend([download_msg, download_link_msg])
            
            # Schedule deletion of all messages after 30 seconds
            bot.loop.create_task(delete_messages(messages_to_delete, 30))
        
        else:
            # No files found
            await status_msg.edit(content=f"❌ No files named '{filename}' found in this server.")
            
            # Schedule deletion of messages after 5 seconds
            bot.loop.create_task(delete_messages(messages_to_delete, 5))
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = await ctx.send(f"An unexpected error occurred: {str(e)}")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))

@bot.command(name='findfile')
async def find_file(ctx, filename):
    """
    Alias for download command to maintain backward compatibility
    """
    await download_file(ctx, filename)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')

# Error handling for command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        # Store messages to delete
        messages_to_delete = [ctx.message]
        
        # Send error message
        error_msg = await ctx.send("Please provide a filename. Usage: !downloadfile <filename>")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))
    else:
        # Store messages to delete
        messages_to_delete = [ctx.message]
        
        # Send error message
        error_msg = await ctx.send(f"An error occurred: {error}")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))

import discord
import os
import mimetypes
import asyncio
from discord.ext import commands

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

async def delete_messages(messages, delay):
    """
    Helper function to delete messages after a specified delay
    """
    await asyncio.sleep(delay)
    try:
        for message in messages:
            await message.delete()
    except discord.errors.NotFound:
        # Message already deleted
        pass
    except discord.errors.Forbidden:
        print("Bot lacks permission to delete messages")

@bot.command(name='downloadfile')
async def download_file(ctx, filename):
    """
    Advanced file search and download command with auto-delete
    """
    # Store messages to be potentially deleted
    messages_to_delete = [ctx.message]
    
    try:
        # Confirm command usage
        status_msg = await ctx.send(f"🔍 Searching for file: {filename}")
        messages_to_delete.append(status_msg)
        
        # Tracks found files
        found_files = []
        
        # Iterate through all text channels in the server
        for channel in ctx.guild.text_channels:
            try:
                # Scan recent messages (last 200 to increase chances)
                async for message in channel.history(limit=200):
                    # Check message attachments
                    for attachment in message.attachments:
                        if attachment.filename.lower() == filename.lower():
                            # Collect file details
                            found_files.append({
                                'channel': channel,
                                'message': message,
                                'attachment': attachment
                            })
            except Exception as e:
                print(f"Error searching in {channel.name}: {e}")
        
        # Process found files
        if found_files:
            # Edit status message
            await status_msg.edit(content=f"✅ Found {len(found_files)} instance(s) of {filename}")
            
            # Send details and download links for each found file
            for idx, file_info in enumerate(found_files, 1):
                channel = file_info['channel']
                attachment = file_info['attachment']
                message = file_info['message']
                
                # Create embed with file details and download instructions
                embed = discord.Embed(
                    title=f"📁 File Found: {filename} (Instance {idx})",
                    color=discord.Color.green()
                )
                
                # Add file metadata
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Uploaded By", value=message.author.mention, inline=True)
                embed.add_field(name="Upload Date", value=message.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                
                # File size and type
                embed.add_field(name="File Size", value=f"{attachment.size:,} bytes", inline=True)
                embed.add_field(name="File Type", value=attachment.content_type or "Unknown", inline=True)
                
                # Send embed with download link
                download_msg = await ctx.send(embed=embed)
                download_link_msg = await ctx.send(f"📥 Direct Download Link: {attachment.url}")
                
                # Add these messages to deletion list
                messages_to_delete.extend([download_msg, download_link_msg])
            
            # Schedule deletion of all messages after 30 seconds
            bot.loop.create_task(delete_messages(messages_to_delete, 30))
        
        else:
            # No files found
            await status_msg.edit(content=f"❌ No files named '{filename}' found in this server.")
            
            # Schedule deletion of messages after 5 seconds
            bot.loop.create_task(delete_messages(messages_to_delete, 5))
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = await ctx.send(f"An unexpected error occurred: {str(e)}")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))

@bot.command(name='findfile')
async def find_file(ctx, filename):
    """
    Alias for download command to maintain backward compatibility
    """
    await download_file(ctx, filename)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')

# Error handling for command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        # Store messages to delete
        messages_to_delete = [ctx.message]
        
        # Send error message
        error_msg = await ctx.send("Please provide a filename. Usage: !downloadfile <filename>")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))
    else:
        # Store messages to delete
        messages_to_delete = [ctx.message]
        
        # Send error message
        error_msg = await ctx.send(f"An error occurred: {error}")
        messages_to_delete.append(error_msg)
        
        # Schedule deletion of messages after 5 seconds
        bot.loop.create_task(delete_messages(messages_to_delete, 5))

# Use environment variables for security
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("Error: DISCORD_BOT_TOKEN environment variable not set.")
    exit(1)

bot.run(TOKEN)
