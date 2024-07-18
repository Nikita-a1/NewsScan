import requests

def send_msg(bot_token, channel_id):
    message = f"[{'https://quote.ru'}]({'https://quote.ru'}) *{'e'}*\n{'r'}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {'chat_id': channel_id, 'text': message, 'parse_mode': 'Markdown',
              'disable_web_page_preview': True}
    requests.post(url, data=params)

send_msg('7359065426:AAH7DTsO5vgmwvSU1d110CEiPHi64nI1lUo', '-1002168464302')