import sendgrid
import requests
import urllib.parse
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.cloud import datastore

from bs4 import BeautifulSoup
import base64
import json

"""
デプロイコマンド：gcloud functions deploy task_cybozu_topmessage --runtime python37 --trigger-topic=cybozu_users --allow-unauthenticated --region asia-northeast1
"""

domain = "https://gw.xxxxxxxxxx.jp/members/"
session = None
cookie = None
csrf_ticket = None

def task_cybozu_topmessage(event, context):
    cybozu_id       = ''
    cybozu_password = ''
    gsuite_account  = ''

    # パラメータ取得
    if 'data' in event:
        name       = base64.b64decode(event['data']).decode('utf-8')
        json_dict  = json.loads(name)
        properties = json_dict['properties']

        cybozu_id       = properties['cybozu_id']['stringValue']
        cybozu_password = properties['cybozu_password']['stringValue']
        gsuite_account  = properties['gsuite_account']['stringValue']
    else:
        print('pubsub message data not found....')
        return 'pubsub message data not found....'

    # ログイン
    if(login(cybozu_id,cybozu_password) == False): 

        # メール送信
        sendMailPassWordChenge(gsuite_account)

        # データ削除
        deleteCybozuAccount(gsuite_account)
        return 'login error.'

    # TOPページの取得
    res = httpRequestTop()
    if(res == None):
        sendMailPassWordChenge(gsuite_account)
        deleteCybozuAccount(gsuite_account)
        return 'login error.'

    # 個人用フォルダお知らせ領域解析処理
    for message in requestNewNoticeMessages(res):

        # 新しいメッセージの情報取得
        requestNewNoticeMessage(message)

        # メール送信
        sendMail(message, gsuite_account)

    # ログアウト
    logout()

    return 'success'

def login(cybozu_id,cybozu_password):
    global session
    global cookie
    global csrf_ticket
    print('start login... :' + str(cybozu_id))

    # ログインページのURLからオブジェクトを生成
    url = domain + "ag.exe?page=AGIndex"
    session  = requests.session()
    response = session.get(url)
    cookie   = response.cookies

    # ログイン情報
    info = {
        "csrf_ticket" : "",
        "_System"     : "login",
        "_Login"      : "1",
        "LoginMethod" : "1",
        "_Account"    : cybozu_id,
        "Password"    : cybozu_password
    }

    # URLをたたきHTMLを表示
    response = session.post(url, data=info, cookies=cookie)

    # csrf_ticketの取得
    soup = BeautifulSoup(response.content, 'html.parser')

    soupret = soup.find('input', attrs={'name':'csrf_ticket', 'type':'hidden'})
    if (soupret == None):
        print('csrf_ticket is not read')
        print(response)
        return False
    csrf_ticket = soupret['value']
    print('login complate... csrf_ticket:' + csrf_ticket)
    return True

def logout():
    global session
    global cookie
    global csrf_ticket

    url = domain + "ag.exe"

    info = {
        "csrf_ticket" : csrf_ticket,
        "_System"     : "Login",
        "_Logout"     : "ログアウト"
    }

    response = session.post(url, data=info, cookies=cookie)
    if (response == None):
        print('logout failre...')
        return False
    return True


def httpRequestTop():
    global session
    global cookie
    print('start http request top page...')

    url = domain + "ag.exe"
    response = session.get(url, cookies=cookie)

    soup = BeautifulSoup(response.content, 'html.parser')
    text_title = soup.find('title').text

    if text_title != "トップページ - サイボウズ Office":
        print('top page is not read')
        return None

    return response

def requestNewNoticeMessages(response):
    print('start requestNewNoticeMessages...')
    messages = []

    soup = BeautifulSoup(response.content, 'html.parser')
    for inp in soup.find_all('input', attrs={'name':'MessageID'}):
        print(inp)
        print(inp.next_sibling)

        id    = inp.get('value')
        title = inp.next_sibling.text
        url   = inp.next_sibling.get('href')
        html = '<a href=''{}''>スレッドリンク</a><br>'.format(domain + url) 

        messages.append(cybozuMessage(id, title, url, html))

    return messages

def requestNewNoticeMessage(message):
    global session
    global cookie
    print('requestNewNoticeMessage...' + message.title)

    url = domain + message.url
    response = session.get(url, cookies=cookie)

    if response.text == "":
        print('message page is not read')
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # メッセージ本文
    messageText = soup.find('div', id='messageText')
    message.html = message.html + '<hr>' + str(messageText)

    # 既存メッセージの処理
    for div in soup.find_all('div', class_='vr_follow'):

        if('updateContents' in div['class']):
            div['style']='background-color:rgb(252, 244, 225)'

        for img in div.find_all('img'):
            img.extract()

        div.find('div', class_='vr_followUserImageColumn').extract()
        div.find('div', class_='followMenu')              .extract()
        if(div.find('div', class_='simpleReplyUserList') != None):
            div.find('div', class_='simpleReplyUserList').extract()

        message.html = message.html + '<hr>' + str(div)

    # メッセージ内のURLを相対パスから絶対パスに変更
    message.html = message.html.replace(domain + 'ag.exe','ag.exe')
    message.html = message.html.replace('ag.exe', domain + 'ag.exe')
    return

def sendMail(cmessage,gsuite_account):
    print('start sendMail...')

    message = Mail(
        from_email='daichi.asada@sendmail.com',
        to_emails=gsuite_account,
        subject='【自動通知】' + cmessage.title,
        html_content=cmessage.html
    )

    try:
        sg = SendGridAPIClient('xxxxxxxxxxxxxxxx')
        response = sg.send(message)

        if response.status_code != '200':
            print(response.status_code)
            print(response.body)
            print(response.headers)
    except Exception as e:
        print(e)
    return

def sendMailPassWordChenge(gsuite_account):
    print('start sendMail...')

    html_content  = '<a href=\"https://gw.tfounion.jp/members/ag.exe?page=AGIndex\">サイボウズ</a>'
    html_content += '<a href=\"https://account-cybozu-regist-dot-tfounion-cfcb3.appspot.com\">配信ツール</a>'

    message = Mail(
        from_email='daichi.asada@sendmail.com',
        to_emails=gsuite_account,
        subject='【自動通知】サイボウズのパスワードを変更してください',
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient('xxxxxxxxxxxxxxx')
        response = sg.send(message)

        if response.status_code != '200':
            print(response.status_code)
            print(response.body)
            print(response.headers)
    except Exception as e:
        print(e)
    return

def deleteCybozuAccount(gsuite_account):
    print('start deleteCybozuAccount...')
    client = datastore.Client()
    client.delete(client.key('cybozu_account', gsuite_account))
    return

class cybozuMessage:

    def __init__(self, id, title, url, html=''):
        self.id    = id,
        self.title = title
        self.url   = url
        self.html  = html

