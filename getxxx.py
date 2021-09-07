#!/usr/bin/python3
import hashlib, base64, json, requests, sys # pip3 install requests
from sanic import Sanic # pip3 install sanic
from sanic.response import html
from lxml import etree # pip3 install lxml

## ------------ utils -------------

def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest().lower()

def urls2apis(urls):
    return [(url, url) for url in urls]

## ------------ 98tang ------------

def tang_decode(data, codebook1, codebook2, key):
    result = ''
    i = 0
    for d in data:
        k = ord(key[i])
        index = codebook1.index(d) - k
        while index < 0:
            index += len(codebook2)
        result += codebook2[index]
        i += 1
        if i == len(key):
            i = 0
    return str(base64.b64decode(result), "utf8")

def tang_decryptApi(data):
    codebook = 'GHI9+JKLxyz012MNOPYbcRSTUVW8/ABCw3DEZaFXefghijklm7=nopqrsdQtuv456'
    offset = codebook.index(data[-1])
    codebook1 = codebook[offset:] + codebook[:offset]
    key = md5('201906xsevMNBG01' + data[-1])
    return tang_decode(data[:-1], codebook1, codebook, key)

def tang_main():
    urls = ['https://r.cnpmjs.org/6vd-pub-baoyu', 'https://r.cnpmjs.org/6vd-pub-shen']
    for url in urls:
        try:
            resp = requests.get(url)
            ciphertext = resp.json()['description']
            apis = tang_decryptApi(ciphertext )
            apiObj = json.loads(apis)
            return urls2apis(apiObj['bbs_site'])
        except:
            pass
    return []

## --------------- zztt -----------------

def zztt_main():
    url = 'https://zzzttt.online'
    headers = {'user-agent': 'zzztttWb;Mozilla/5.0 (Android5.1.1) AppleWebKit/537. 36 (KHTML, like Gecko) Chrome/41. 0.2225.0 Safari/537. 36'}
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf8'
    root = etree.HTML(resp.text)
    alist = root.xpath('//div[@class="list"]/a')
    result = []
    for a in alist:
        u = a.xpath('./@href')[0]
        t = a.xpath('.//div[@class="btnTitle"]/text()')[0]
        result.append((u, t))
    return result

## --------------- APP ------------------

app = Sanic('GET-XXX')

def render_apis(apis):
    result = ''
    for api in apis:
        result += ('<h2><a href="{0}">{1}</a></h2>\n'.format(api[0], api[1]))
    return result

@app.route('/')
async def get_xxx(request):
    apis = [('98tang', '98堂'), ('zztt', '黑料不打烊')]
    return html(render_apis(apis))

@app.route('/98tang')
async def get_98tang(request):
    return html(render_apis(tang_main()))

@app.route('/zztt')
async def get_zztt(request):
    return html(render_apis(zztt_main()))

def main():
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080
    app.run(host='0.0.0.0', port=port, access_log=False)

if __name__ == '__main__':
    main()

