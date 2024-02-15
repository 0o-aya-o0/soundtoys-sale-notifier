import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from configparser import ConfigParser
import schedule
from time import sleep

# ConfigParserのインスタンスを作成
config = ConfigParser()

# config.iniファイルを読み込む
config.read('config.ini')

print("スクリプト実行開始")

# チェックするプラグインのURLとセール価格セレクタの辞書
plugins = {
    'Radiator(Soundtoys)': {'url': 'https://www.soundtoys.com/product/radiator/', 'selector': '.hero .sale-price'},
    'Devil-Lov Deluxe(soundtoys)': {'url': 'https://www.soundtoys.com/product/devil-loc-deluxe/', 'selector': '.hero .sale-price'},
    'Decapitator(soundtoys)': {'url': 'https://www.soundtoys.com/product/decapitator/', 'selector': '.hero .sale-price'},
    'Radiator(soundtoys)': {'url': 'https://www.soundtoys.com/product/radiator/', 'selector': '.hero .sale-price'},
    'Crystallizer(soundtoys)': {'url': 'https://www.soundtoys.com/product/crystallizer/', 'selector': '.hero .sale-price'},
    'MicroShift(soundtoys)': {'url': 'https://www.soundtoys.com/product/microshift/', 'selector': '.hero .sale-price'},
    'PhaseMistress(soundtoys)': {'url': 'https://www.soundtoys.com/product/phasemistress/', 'selector': '.hero .sale-price'},
    'Tremolator(soundtoys)': {'url': 'https://www.soundtoys.com/product/tremolator/', 'selector': '.hero .sale-price'}
}

def check_sale_prices(plugins):
    sale_info = {}
    for name, info in plugins.items():
        response = requests.get(info['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        
        full_price_element = soup.select_one('.full-price')
        sale_price_element = soup.select_one(info['selector'])
        if full_price_element and sale_price_element:
            full_price_text = full_price_element.text.strip().replace('$', '')
            sale_price_text = sale_price_element.text.strip().replace('On Sale ', '').replace('$', '')
            print(f"Full price: {full_price_text}, Sale price: {sale_price_text}")  # デバッグ出力
            try:
                full_price = float(full_price_text)
                sale_price = float(sale_price_text)
                if sale_price < full_price:
                    sale_info[name] = {
                        'sale_price': f'${sale_price}',
                        'normal_price': f'${full_price}',
                        'url': info['url']
                    }
                    print(f"Sale found for {name}")  # デバッグ出力
            except ValueError:
                print(f"Error converting prices for {name}")  # エラー出力
                continue

    return sale_info

def send_email(sale_info):
    # ConfigParserのインスタンスを作成
    config = ConfigParser()
    # config.iniファイルを読み込む
    config.read('config.ini')

    # SMTPセクションからサーバー設定を取得
    smtp_server = config.get('SMTP', 'server')
    smtp_port = config.getint('SMTP', 'port')  # ポートは整数として読み込む

    sender = config.get('EMAIL', 'sender')
    receiver = config.get('EMAIL', 'receiver')
    password = config.get('EMAIL', 'password')
    subject = 'プラグインのセール情報'
    body = 'セール中のプラグインの価格は以下の通りです：\n\n'

    for name, info in sale_info.items():
        body += (f'{name}: セール価格 {info["sale_price"]} (通常価格 {info["normal_price"]})\n'
                 f'詳細はこちら: {info["url"]}\n\n')

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # SMTPサーバーの設定とメールの送信
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        print('メールを送信しました。')
    except Exception as e:
        print(f"メール送信に失敗しました: {e}")


def scheduled_task():
    print("スクリプト実行開始")
    sale_info = check_sale_prices(plugins)
    print(sale_info)  # デバッグ出力
    if sale_info:
        send_email(sale_info)
    else:
        print('セール中のプラグインはありません。')

# スケジュール登録
schedule.every().day.at("10:30").do(scheduled_task)  #  条件を追加: 毎日10:30

# イベント実行
while True:
    schedule.run_pending()
    sleep(1)