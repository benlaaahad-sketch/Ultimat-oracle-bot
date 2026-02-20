import requests

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"
# اینو با دامنه خودت عوض کن
RAILWAY_URL = "https://ultimat-oracle-bot.up.railway.app"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
data = {"url": f"{RAILWAY_URL}/webhook"}

response = requests.post(url, json=data)
print(response.json())
