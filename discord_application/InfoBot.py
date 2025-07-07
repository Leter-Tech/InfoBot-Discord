import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
import asyncio

DISCORD_TOKEN = "REMOVED"
GEMINI_API_KEY = "REMOVED"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="...", intents=intents)
tree = bot.tree

async def generate_ai_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

@bot.event
async def on_message(message):
    if not bot.user or message.author.bot:
        return

    mentioned = any(user.id == bot.user.id for user in message.mentions)
    is_reply = (
        message.reference is not None and 
        message.reference.resolved and 
        getattr(message.reference.resolved, "author", None) == bot.user
    )

    if mentioned or is_reply:
        context_text = ""
        if message.reference and message.reference.message_id:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                context_text = f"Previous message: \"{replied_message.content}\"\n"
            except Exception:
                pass

        user_name = message.author.display_name
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        prompt = (
            f"{context_text}"
            f"You are InfoBot, an AI chatbot and assistant in a Discord server."
            f"{user_name} sent the message: \"{content}\".\n"
            f"Reply in a helpful, concise, and friendly way, directly addressing {user_name} by name. This assistant can support a wide range of server types: in Community & Chat Servers, it sparks friendly conversations, offers games and trivia, answers FAQs, and suggests engaging topics; in Education & Study Groups, it helps with homework, simplifies concepts, assists with essays, and prepares quizzes; for Developer & Tech Servers, it provides code snippets, explains bugs, offers library/tool info, and helps with Git or shell commands; in Writing & Creative Spaces, it generates story ideas, builds characters, proofreads text, and creates lyrics or scripts; for Gaming Communities, it offers strategy tips, game lore, name generators, and bot support; in Mental Health & Wellness Servers, it shares affirmations, stress relief methods, motivation, and mindfulness practices; for Productivity & Workspaces, it breaks down tasks, summarizes meetings, assists with decisions, and supports goal planning; in Business & Professional Groups, it drafts emails, gives proposal feedback, improves resumes, and creates marketing copy; for Language & Translation Servers, it translates phrases, explains grammar, adds cultural context, and helps build vocabulary; and in Moderation & Server Management, it clarifies rules, explains bot commands, creates welcome messages, and suggests conflict resolution approaches."
            f"Your job is to understand the user's intent and take action immediately. Do not ask questions, delay, or acknowledge. Just respond with the actual output the user is asking for. If they want trivia, give a trivia question. If they want a song, write the first verse. If they want help, give it. If they want a story, start telling it. If they want a summary, summarize it. If they need code, generate it. If they say 'sure' or 'go ahead', proceed without hesitation."
            f"Keep your responses concise and within 2000 characters"
        )

        await message.channel.typing()
        ai_reply = await generate_ai_response(prompt)
        await message.reply(ai_reply)

    await bot.process_commands(message)

@tree.command(name="ask", description="Ask InfoBot for help with anything.")
@app_commands.describe(query="What do you want help with?")
async def help_command(interaction: discord.Interaction, query: str = "A user has requested help."):
    await interaction.response.defer()

    prompt = (
        "You are InfoBot, an AI chatbot and assistant. " +
        "Here's the user's question or help request: " + query + "\n\n" +
        "Respond in a helpful, concise, and friendly way. Keep replies below 2000 characters. " +
        "This assistant can support a wide range of server types: in Community & Chat Servers, it sparks friendly conversations, offers games and trivia, answers FAQs, and suggests engaging topics; in Education & Study Groups, it helps with homework, simplifies concepts, assists with essays, and prepares quizzes; for Developer & Tech Servers, it provides code snippets, explains bugs, offers library/tool info, and helps with Git or shell commands; in Writing & Creative Spaces, it generates story ideas, builds characters, proofreads text, and creates lyrics or scripts; for Gaming Communities, it offers strategy tips, game lore, name generators, and bot support; in Mental Health & Wellness Servers, it shares affirmations, stress relief methods, motivation, and mindfulness practices; for Productivity & Workspaces, it breaks down tasks, summarizes meetings, assists with decisions, and supports goal planning; in Business & Professional Groups, it drafts emails, gives proposal feedback, improves resumes, and creates marketing copy; for Language & Translation Servers, it translates phrases, explains grammar, adds cultural context, and helps build vocabulary; and in Moderation & Server Management, it clarifies rules, explains bot commands, creates welcome messages, and suggests conflict resolution approaches."
        "Your job is to understand the user's intent and take action immediately. Do not ask questions, delay, or acknowledge. Just respond with the actual output the user is asking for. If they want trivia, give a trivia question. If they want a song, write the first verse. If they want help, give it. If they want a story, start telling it. If they want a summary, summarize it. If they need code, generate it. If they say 'sure' or 'go ahead', proceed without hesitation."
    )

    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)

@tree.command(name="summarize", description="Summarize any block of text.")
@app_commands.describe(text="The text you'd like to summarize")
async def summarize_command(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    
    prompt = (
        f"You are InfoBot, a helpful AI assistant. Summarize the following text in a clear and concise way:\n\n"
        f"{text}\n\n"
        f"Keep it under 2000 characters and use simple, friendly language suitable for a Discord user."
    )

    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)

@tree.command(name="translate", description="Translate a message into another language.")
@app_commands.describe(text="The text you want translated", language="The language to translate it into")
async def translate_command(interaction: discord.Interaction, text: str, language: str):
    await interaction.response.defer()
    prompt = (
        f"You are InfoBot, a helpful AI translator. Translate the following text into {language}:\n\n"
        f"{text}\n\n"
        f"Be accurate, keep the tone natural, and make sure the output stays under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="define", description="Define a word or phrase.")
@app_commands.describe(term="The word or phrase you want defined")
async def define_command(interaction: discord.Interaction, term: str):
    await interaction.response.defer()
    prompt = (
        f"Define the term '{term}' in simple, easy-to-understand language suitable for a Discord user. "
        f"Keep the output under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="explain", description="Explain a concept or topic.")
@app_commands.describe(topic="What do you want explained?")
async def explain_command(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()
    prompt = (
        f"Explain the following concept in simple terms: {topic}. Use examples if helpful. "
        f"Keep the explanation under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="suggest", description="Ask InfoBot for creative suggestions.")
@app_commands.describe(request="What do you want suggestions for?")
async def suggest_command(interaction: discord.Interaction, request: str):
    await interaction.response.defer()
    prompt = (
        f"Give suggestions for: {request}. Respond with a list of creative and helpful ideas. "
        f"Keep your answer under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="write", description="Generate a short piece of text (caption, tweet, intro, etc.)")
@app_commands.describe(instruction="What do you want InfoBot to write?")
async def write_command(interaction: discord.Interaction, instruction: str):
    await interaction.response.defer()
    prompt = (
        f"Write based on this instruction: {instruction}. Keep it concise, Discord-friendly, and under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="correct", description="Fix grammar or improve a sentence.")
@app_commands.describe(text="The text you'd like corrected or improved")
async def correct_command(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    prompt = (
        f"Improve the grammar and clarity of this text: \"{text}\". Maintain its tone and meaning. "
        f"Ensure your reply stays under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="sentiment_analysis", description="Analyze the tone or intent of a message.")
@app_commands.describe(text="The message you'd like analyzed")
async def analyze_command(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    prompt = (
        f"Analyze the tone, intent, and emotion of this message: \"{text}\". "
        f"Is it serious, sarcastic, aggressive, kind, etc.? Keep your analysis under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)


@tree.command(name="quote", description="Get a motivational or themed quote.")
@app_commands.describe(theme="Optional theme for the quote (e.g. courage, success, love)")
async def quote_command(interaction: discord.Interaction, theme: str = "inspiration"):
    await interaction.response.defer()
    prompt = (
        f"Give a motivational quote based on the theme '{theme}'. Include the author's name if known. "
        f"Ensure your reply is under 2000 characters."
    )
    ai_reply = await generate_ai_response(prompt)
    await interaction.followup.send(ai_reply)

@tree.command(name="commands", description="View the full list of InfoBot commands.")
async def commands_command(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="📜 InfoBot Commands",
        description="Here's a full list of available commands and what they do.",
        color=0xFF5757
    )

    embed.add_field(
        name="🔗 View Command List",
        value="[Click here to view all commands](https://infobot-discord.web.app/)",
        inline=False
    )

    embed.set_footer(text="Ask anything, anytime.")
    await interaction.followup.send(embed=embed)

@tree.command(name="about_infobot", description="Know all the features of InfoBot.")
async def about_infobot_command(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="🤖 InfoBot",
        description="Know all about InfoBot!",
        color=0xFF5757
    )

    embed.add_field(
        name="🔗 About InfoBot",
        value="[Click here to view details about InfoBot](https://infobot-discord.web.app/)",
        inline=False
    )

    embed.set_footer(text="Ask anything, anytime.")
    await interaction.followup.send(embed=embed)

@tree.command(name="summarize_chat", description="Summarize the recent conversation in this channel.")
@app_commands.describe(count="Number of recent messages to summarize (max 20)")
async def summarize_chat_command(interaction: discord.Interaction, count: int):
    await interaction.response.defer()

    if count < 1 or count > 20:
        await interaction.followup.send("Please choose a number between 1 and 20.")
        return

    messages = []
    async for msg in interaction.channel.history(limit=50):
        if not msg.author.bot:
            messages.append(msg)
        if len(messages) >= count:
            break

    if not messages:
        await interaction.followup.send("No valid messages found to summarize.")
        return

    messages.reverse()
    formatted = "\n".join(f"{msg.author.display_name}: {msg.content}" for msg in messages)

    prompt = (
        "You are InfoBot, an AI assistant in a Discord server.\n"
        "Summarize the following recent conversation between users in a clear and concise way.\n"
        "Include who said what (briefly), focus on the main points, and keep the summary casual but informative.\n"
        "Limit the output to strictly under 2000 characters.\n\n"
        f"Messages:\n{formatted}"
    )

    ai_reply = await generate_ai_response(prompt)

    if len(ai_reply) > 1990:
        ai_reply = ai_reply[:1990] + "…"

    await interaction.followup.send(ai_reply)

@bot.event
async def on_ready():
    print(f"InfoBot is online as {bot.user}!")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Command sync failed: {e}")

bot.run(DISCORD_TOKEN)