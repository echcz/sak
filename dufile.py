from time import time
import requests
from PIL import Image
from io import BytesIO
from lxml import etree
# import logging
# import http.client

# logging.getLogger().setLevel(logging.DEBUG)
# http.client.HTTPConnection.debuglevel = 1

def parse(data: str):
    if data.endswith('err'):
        print('无法获取下载路径，请检查是否超过服务请求限制')
        return
    dom = etree.HTML(data)
    down_urls = dom.xpath('//a[@id="downs"]/@href')
    if not down_urls:
        print('获取不到下载路径，请检查是否超过服务请求限制')
        return
    for down_url in down_urls:
        print(down_url)

def format_proxy(proxy: str):
    i = proxy.find('://')
    head = ''
    tail = proxy
    if i > -1:
        head = proxy[0:i]
        tail = proxy[i+3:]
    if not head:
        head = 'socks5'
    if tail.startswith(':'):
        tail = '127.0.0.1' + tail
    if tail.endswith(':'):
        tail = tail + '7890'
    proxy = head + '://' + tail
    return proxy

def main():
    file_id = ''
    proxy = input('请输入代理地址(格式为 <协议=socks5://><IP=127.0.0.1>:<端口=7890>)(直接按回车将不使用代理): ')
    proxy = proxy.strip()
    if proxy:
        proxy = format_proxy(proxy)
        print("将使用代理: " + proxy)
    else:
        print("将不使用代理")

    while True: # LOOP1
        file_id = input('请输入文件ID(直接按回车退出程序): ')
        file_id = file_id.strip()
        if not file_id:
            return
        print("将获取以下文件的下载路径: " + file_id)
        with requests.session() as s:
            # 设置代理
            if proxy:
                proxies = {'http': proxy, 'https': proxy}
                s.proxies = proxies
            # 请求 file，用于设置 Cookie
            url = f'https://dufile.com/file/{file_id}.html'
            resp = s.get(url, timeout=10)
            if resp.status_code != 200:
                print(f'请求 file 出错: {resp.status_code}')
                continue
            # 请求 down，用于引导验证码
            url = f'https://dufile.com/down/{file_id}.html'
            resp = s.get(url, headers={'Referer': url}, timeout=10)
            if resp.status_code != 200:
                print(f'请求 down 出错: {resp.status_code}')
                continue
            f1 = False # 用于重新开始 LOOP1
            f2 = True # 用于跳出 LOOP2
            while f2:  # LOOP2
                # 请求 get_code，用于显示验证码
                url = 'https://dufile.com/down_code.php'
                resp = s.get(url, timeout=10)
                if resp.status_code != 200:
                    print(f'请求 get_code 出错: {resp.status_code}')
                    f1 = True
                    break
                image = Image.open(BytesIO(resp.content))
                image.show()
                # 请求 post_code，用于提交验证码
                while True:
                    code = input("请输入验证码(输入 - 重新获取验证码；直接按回车退出程序): ")
                    code = code.strip()
                    if not code:
                        return
                    if code == '-':
                        break
                    url = 'https://dufile.com/down_code.php'
                    resp = s.post(url, data=f'action=yz&id={file_id}&code={code}', headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
                    if resp.status_code != 200:
                        print(f'请求 post_code 出错: {resp.status_code}')
                        continue
                    if resp.text != '1':
                        print('请求 post_code 失败，请检查验证码是否输入正确')
                        continue
                    f2 = False
                    break
            if f1:
                continue
            # 请求 dd，用于获取下载地址
            url = f'https://dufile.com/dd.php?file_key={file_id}&p=0'
            resp = s.get(url, timeout=10)
            if resp.status_code != 200:
                print(f'请求 dd 出错: {resp.status_code}')
                continue
            # 解析下载地址
            parse(resp.text)

main()
