import json
import re
import requests
from telethon import TelegramClient,events

f = open('config.json')
datas = json.load(f)
phone_number = datas["phone number"]
api_id = datas["api id"]
api_hash = datas["api hash"]
chat_id = datas["chat id"]
## here is the bad chars in signal
bad_chars = ["*","`","•","$","🔴","🔥","🎯","⛔️","🏳️"]
client = TelegramClient(phone_number, api_id, api_hash)


# Bot hesabınızı kullanarak gizli kanala bağlanın
async def connect_to_channel(channel_username):
    channel = await client.get_entity(channel_username)
    return channel

# Kanala bağlandıktan sonra mesajları alın
@client.on(events.NewMessage(chat_id))
async def my_event_handler(event):
    order = {
        'symbol': "",
        'side': "",
        'entry_price': 0,
        'leverage': 0,
        'targets': [],
        'stop_loss': 0
    }
    for i in bad_chars:
        event.text = event.text.replace(i,'')
    """
        That's my channel signal, you can re-design splitting code with your signal or you can
        edit your signal like that;
        🆕 $LPT/USDT | 🔴 SHORT 
        🏳️ Entry Price: 6.1892
        🔥 Leverage: 20X
        🎯 Targets:
        • 5.98864
        • 5.63797
        • 5.14487
        ⛔️ Stop Loss: 6.4835
    """
    orderTexts = event.text.splitlines()
    orderTexts.remove('')
    splitted_symbol = orderTexts[0].split("| ",1)[0]
    splitted_side = orderTexts[0].split("| ",1)[1]
    splitted_entry_price = orderTexts[1].split("Entry Price: ",1)[1] # text-splitting ile entry price değerini alıyoruz
    splitted_leverage = orderTexts[2].split("Leverage: ",1)[1]
    splitted_stop_loss = orderTexts[len(orderTexts)-1].split("Stop Loss: ",1)[1]
    order['symbol'] = splitted_symbol
    order['side'] = splitted_side
    order["entry_price"] = splitted_entry_price
    order["leverage"] = splitted_leverage.replace("X",'')
    for i in range(len(orderTexts) - 5):
        order["targets"] += [orderTexts[i+4]]
    order["stop_loss"] = orderTexts[len(orderTexts) - 1]
    print(order)
    send_request(order["symbol"],order["side"],order["entry_price"],order["leverage"],order["targets"],order["stop_loss"])


def send_request(symbol,side,entryPrice,leverage,targets,stopLoss):
    # Binance Futures API URL'si
    url = "https://fapi.binance.com/v1/futures/order"
    # Pozisyon parametreleri
    symbol = symbol
    side = side
    type = "LIMIT"
    price = entryPrice
    quantity = 10
    leverage = leverage

    # Pozisyon oluşturma
    headers = {
        "X-MBX-API-KEY": datas["api_key"],
        "X-MBX-API-SECRET": datas["secret_key"],
    }

    data = {
        "symbol": symbol,
        "side": side,
        "type": type,
        "price": entryPrice,
        "quantity": quantity,
        "leverage": leverage,
    }

    response = requests.post(url, headers=headers, data=data)
    # Pozisyon yanıtını kontrol etme
    if response.status_code == 200:
        print("Pozisyon oluşturuldu!")
        position = response.json()
        print(position)
    else:
        print("Pozisyon oluşturulamadı!")
    data = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "price": price,
        "quantity": quantity,
        "leverage": leverage,
        "stop-loss-price": stopLoss,
        "take-profit-prices": targets,
    }

    response = requests.post(url, headers=headers, data=data)
    # Hedefler yanıtını kontrol etme

    if response.status_code == 200:
        print("Hedefler ayarlandı!")
    else:
        print("Hedefler ayarlanamadı!")

with client:
    # Gizli kanala bağlanın
    print(f"Connect to  {chat_id}..")
    channel = client.loop.run_until_complete(connect_to_channel(chat_id))

    # Kanalda yeni mesajlar olup olmadığını dinleyin
    client.run_until_disconnected()