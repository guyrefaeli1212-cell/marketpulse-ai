import os
import io
import discord
from discord.ext import commands
import yfinance as yf
import matplotlib.pyplot as plt
from keep_alive import keep_alive

# הגדרת Intents לבוט
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# תיקים וירטואליים למשתמשים
user_wallets = {}

def get_wallet(user_id):
    if user_id not in user_wallets:
        user_wallets[user_id] = {"cash": 10000.0, "stocks": {}}
    return user_wallets[user_id]

# פונקציה לבדיקת מחיר מניה בזמן אמת מ-Yahoo Finance
def get_stock_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except Exception:
        return None

@bot.event
async def on_ready():
    print(f"הבוט התחבר בהצלחה בתור {bot.user}")

# פקודת קנייה: !buy AAPL 5
@bot.command(name="buy", help="קנה כל מניה בעולם, למשל: !buy AAPL 5")
async def buy(ctx, symbol: str, amount: int):
    symbol = symbol.upper()
    
    if amount <= 0:
        await ctx.send("הכמות חייבת להיות גדולה מ-0.")
        return

    await ctx.send(f"⏳ בודק מחיר עבור `{symbol}`...")
    price_per_share = get_stock_price(symbol)
    
    if price_per_share is None:
        await ctx.send(f"המניה `{symbol}` לא נמצאה או שסימל הטיקר לא חוקי.")
        return

    total_cost = price_per_share * amount
    wallet = get_wallet(ctx.author.id)

    if wallet["cash"] < total_cost:
        await ctx.send(f"אין לך מספיק כסף! יש לך ${wallet['cash']:,.2f} וצריך ${total_cost:,.2f}.")
        return

    wallet["cash"] -= total_cost
    wallet["stocks"][symbol] = wallet["stocks"].get(symbol, 0) + amount

    embed = discord.Embed(title="📈 אישור רכישת מניה", color=discord.Color.green())
    embed.add_field(name="משתמש", value=ctx.author.mention, inline=False)
    embed.add_field(name="מניה", value=symbol, inline=True)
    embed.add_field(name="כמות", value=str(amount), inline=True)
    embed.add_field(name="מחיר ליחידה", value=f"${price_per_share:,.2f}", inline=True)
    embed.add_field(name="עלות כוללת", value=f"${total_cost:,.2f}", inline=False)
    embed.add_field(name="יתרת מזומן חדשה", value=f"${wallet['cash']:,.2f}", inline=False)
    await ctx.send(embed=embed)

# פקודת מכירה: !sell AAPL 5
@bot.command(name="sell", help="מכור מניה, למשל: !sell AAPL 5")
async def sell(ctx, symbol: str, amount: int):
    symbol = symbol.upper()
    
    if amount <= 0:
        await ctx.send("הכמות חייבת להיות גדולה מ-0.")
        return

    wallet = get_wallet(ctx.author.id)
    current_owned = wallet["stocks"].get(symbol, 0)

    if current_owned < amount:
        await ctx.send(f"אין לך מספיק מניות למכירה! יש ברשותך {current_owned} מניות של `{symbol}`.")
        return

    price_per_share = get_stock_price(symbol)
    if price_per_share is None:
        price_per_share = 0

    total_earned = price_per_share * amount
    wallet["cash"] += total_earned
    wallet["stocks"][symbol] -= amount
    if wallet["stocks"][symbol] == 0:
        del wallet["stocks"][symbol]

    embed = discord.Embed(title="📉 אישור מכירת מניה", color=discord.Color.red())
    embed.add_field(name="משתמש", value=ctx.author.mention, inline=False)
    embed.add_field(name="מניה", value=symbol, inline=True)
    embed.add_field(name="כמות נמכרת", value=str(amount), inline=True)
    embed.add_field(name="סך הכל הרווחת", value=f"${total_earned:,.2f}", inline=False)
    embed.add_field(name="יתרת מזומן חדשה", value=f"${wallet['cash']:,.2f}", inline=False)
    await ctx.send(embed=embed)

# פקודת בדיקת תיק השקעות: !portfolio
@bot.command(name="portfolio", help="בדוק את היתרה ותיק המניות שלך")
async def portfolio(ctx):
    wallet = get_wallet(ctx.author.id)
    
    embed = discord.Embed(
        title=f"💼 תיק ההשקעות של {ctx.author.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="מזומן בארנק", value=f"${wallet['cash']:,.2f}", inline=False)
    
    stocks_text = ""
    if wallet["stocks"]:
        for sym, qty in wallet["stocks"].items():
            current_price = get_stock_price(sym) or 0
            val = qty * current_price
            stocks_text += f"**{sym}**: {qty} מניות (שווי נוכחי: ${val:,.2f})\n"
    else:
        stocks_text = "אין לך מניות בתיק כרגע."
        
    embed.add_field(name="מניות בבעלותך", value=stocks_text, inline=False)
    await ctx.send(embed=embed)

# פקודת יועץ פיננסי חכם: !advisor
@bot.command(name="advisor", help="קבל ייעוץ פיננסי והמלצות על סמך תיק ההשקעות שלך")
async def advisor(ctx):
    wallet = get_wallet(ctx.author.id)
    cash = wallet["cash"]
    stocks = wallet["stocks"]
    
    total_stock_value = 0
    for sym, qty in stocks.items():
        price = get_stock_price(sym) or 0
        total_stock_value += qty * price
        
    total_net_worth = cash + total_stock_value
    
    advice_lines = []
    if total_net_worth > 10000:
        profit = total_net_worth - 10000
        advice_lines.append(f"🟢 כל הכבוד! אתה ברווח כולל של **${profit:,.2f}** מהסכום ההתחלתי שלך.")
    elif total_net_worth < 10000:
        loss = 10000 - total_net_worth
        advice_lines.append(f"🔴 שים לב, התיק שלך בהפסד של **${loss:,.2f}** נכון לעכשיו.")
    else:
        advice_lines.append("⚪ התיק שלך בדיוק על האפס ביחס לסכום ההתחלתי.")
        
    if len(stocks) == 0:
        advice_lines.append("💡 **המלצה:** אין לך בכלל מניות כרגע! כדאי לנצל את המזומן ולהשקיע בכמה חברות מובילות.")
    elif len(stocks) == 1:
        advice_lines.append("⚠️ **אזהרה:** כל ביצי ההסל שלך בסל אחד (יש לך רק מניה מסוג אחד). כדאי לפזר את הסיכונים.")
    else:
        advice_lines.append(f"✅ מצוין! התיק שלך מפוזר על פני {len(stocks)} חברות שונות.")
        
    cash_percentage = (cash / total_net_worth) * 100 if total_net_worth > 0 else 100
    if cash_percentage > 70:
        advice_lines.append(f"💵 יש לך אחוז גבוה מאוד של מזומן בארנק ({cash_percentage:.1f}%).")
    elif cash_percentage < 10:
        advice_lines.append(f"⚠️ אתה כמעט בלי מזומן נזיל ({cash_percentage:.1f}%).")

    embed = discord.Embed(
        title="🤖 היועץ הפיננסי האישי",
        description="\n\n".join(advice_lines),
        color=discord.Color.gold()
    )
    embed.add_field(name="שווי נקי כולל", value=f"${total_net_worth:,.2f}", inline=False)
    await ctx.send(embed=embed)

# פקודת גרף מניה: !chart AAPL
@bot.command(name="chart", help="הצג גרף מחירים חודשי למניה, למשל: !chart AAPL")
async def chart(ctx, symbol: str):
    symbol = symbol.upper()
    await ctx.send(f"⏳ מייצר גרף עבור `{symbol}`...")

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            await ctx.send(f"לא נמצאו נתונים עבור המניה `{symbol}`.")
            return

        plt.figure(figsize=(8, 4))
        plt.plot(hist.index, hist['Close'], color='#2ecc71', linewidth=2, marker='o', markersize=3)
        plt.title(f"Stock Price Chart: {symbol} (Last 30 Days)", fontsize=14, color='white')
        plt.xlabel("Date", fontsize=10, color='white')
        plt.ylabel("Price ($)", fontsize=10, color='white')
        plt.gca().set_facecolor('#2f3136')
        plt.gcf().patch.set_facecolor('#36393f')
        plt.tick_params(colors='white', labelsize=8)
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor=plt.gcf().get_facecolor(), edgecolor='none')
        buffer.seek(0)
        plt.close()

        file = discord.File(buffer, filename=f"{symbol}_chart.png")
        embed = discord.Embed(title=f"📊 גרף מניה: {symbol}", color=discord.Color.dark_green())
        embed.set_image(url=f"attachment://{symbol}_chart.png")
        await ctx.send(file=file, embed=embed)

    except Exception as e:
        await ctx.send(f"אירעה שגיאה בייצור הגרף עבור `{symbol}`.")

# פקודת מדריך: !setup (למנהלים בלבד)
@bot.command(name="setup", help="שולח הודעת הסבר ומדריך על פקודות הבוט לערוץ")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📊 מדריך מערכת המסחר בשרת",
        description="ברוכים הבאים לסימולטור המניות! לכל משתמש יש **$10,000** להתחלה. הנה רשימת הפקודות שתוכלו להשתמש בהן בצ'אט:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="📈 קניית מניה (!buy)", value="קנה כל מניה בעולם לפי הסימול.\n**דוגמה:** `!buy AAPL 5`", inline=False)
    embed.add_field(name="📉 מכירת מניה (!sell)", value="מכור מניות חזרה למזומן.\n**דוגמה:** `!sell AAPL 5`", inline=False)
    embed.add_field(name="📊 גרף מניה (!chart)", value="הצג גרף מחירים חודשי של מניה.\n**דוגמה:** `!chart AAPL`", inline=False)
    embed.add_field(name="💼 בדיקת תיק (!portfolio)", value="הצג יתרת מזומן ומניות בבעלותך.\n**דוגמה:** `!portfolio`", inline=False)
    embed.add_field(name="🤖 ייעוץ פיננסי (!advisor)", value="קבל טיפים והמלצות מהיועץ הווירטואלי.\n**דוגמה:** `!advisor`", inline=False)
    embed.set_footer(text="בהצלחה במסחר! 🚀")
    await ctx.send(embed=embed)

# הפעלת שרת ה-Flask לשמירת הבוט פעיל
keep_alive()

bot.run(os.environ['DISCORD_TOKEN'])
