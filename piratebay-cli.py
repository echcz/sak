#!/usr/bin/python3
import requests # pip3 install requests
import sys
from lxml import etree # pip3 install lxml
import re

class Item:
    category = ''
    detName = ''
    detDesc = ''
    link = ''

    def __init__(self, category, detName, detDesc, link):
        self.category = category
        self.detName = detName
        self.detDesc = detDesc
        self.link = link

def parseHtmlForItems(html):
    items = []
    trs = html.xpath('//table[@id="searchResult"]/tr')
    for tr in trs:
        cInfo = tr.xpath('./td[@class="vertTh"]/center/a/text()')
        cStr = _paresCategoryInfo(cInfo)
        if cStr != None:
            detName = tr.xpath('.//a[@class="detLink"]/text()')[0].strip()
            detDescTailNode = tr.xpath('.//font[@class="detDesc"]/a/text()')
            detDescTail = ""
            if len(detDescTailNode) > 0:
                detDescTail = detDescTailNode[0]
            detDesc = (tr.xpath('.//font[@class="detDesc"]/text()')[0] + detDescTail).strip()
            link = tr.xpath('.//a[@title="Download this torrent using magnet"]/@href')[0].strip()
            items.append(Item(cStr, detName, detDesc, link))
    return items

def _paresCategoryInfo(categoryInfo):
    if len(categoryInfo) != 2:
        return None
    return "{0}({1})".format(categoryInfo[0].strip(), categoryInfo[1].strip())

def showItems(items):
    for i, item in enumerate(items):
        print(i, item.category, item.detName, item.detDesc, sep=" | ")

def showItem(items, i):
    if (i < 0) | (i >= len(items)):
        print("无指定条目!")
        return
    item = items[i]
    print(i, item.category, item.detName, item.detDesc, sep=" | ", end=" :\n")
    print(item.link)

class Searcher:
    searchName = ''
    pageNum = 1
    orderBy = 99
    category = "0"
    categoryStr = "All"
    categoryNode = None
    begin = 0
    end = 0
    totle = 0
    count = 0
    items = []

    def search(self):
        if (self.searchName == "") | (self.searchName.isspace()):
            return
        # 搜索
        url = "https://thepiratebay10.org/search/{0}/{1}/{2}/{3}".format(self.searchName, self.pageNum, self.orderBy, self.category)
        resp = requests.get(url)
        if resp.status_code != 200:
            print("网络请求出错, 请检查网络或访问的地址!!")
            sys.exit(1)
        resp.encoding = "utf-8"
        html = etree.HTML(resp.text)
        # 设置page信息
        countInfo = html.xpath('//body/h2[1]/text()')[0].strip()
        self._parseCountInfo(countInfo)
        # 设置categoryNode
        categoryNodes = html.xpath('//select[@id="category"]')
        if len(categoryNodes) > 0:
            self.categoryNode = categoryNodes[0]
        else:
            self.categoryNode = None
        # 设置items
        self.items = parseHtmlForItems(html)

    def _parseCountInfo(self, countInfo):
        matchObj = re.match(r"Displaying hits from (\d+) to (\d+) \(approx (\d+) found\)", countInfo, re.I)
        if matchObj != None:
            self.begin = int(matchObj.group(1))
            self.end = int(matchObj.group(2))
            self.totle = int(matchObj.group(3))
            self.count = (self.totle + 29) // 30
        else:
            self.begin = 0
            self.end = 0
            self.totle = 0
            self.count = 0


    def setupCategory(self):
        buf = {"0": "All"}
        gBuf = {}
        print("0 : All")
        if self.categoryNode != None:
            optgroups = self.categoryNode.xpath('./optgroup')
            for optgroup in optgroups:
                gCode = optgroup.xpath('./option[1]/@value')[0][:1] + "00"
                gDesc = optgroup.xpath('./@label')[0]
                print("[ {0} : {1} ]:".format(gCode, gDesc))
                gBuf[gCode] = gDesc
                opts = optgroup.xpath('./option')
                for opt in opts:
                    code = opt.xpath('./@value')[0]
                    desc = opt.xpath('./text()')[0].strip()
                    buf[code] = desc
                    print("{0} : {1}".format(code, desc))
        print("当前类型: {0}({1})".format(self.category, self.categoryStr))
        while True:
            inputStr = input("请输出类别编码(可以使用','分隔以同时输入多个组编码; 输入'q'将取消设置): ").strip()
            if "q" == inputStr:
                return
            elif inputStr in buf:
                self.category = inputStr
                self.categoryStr = buf[inputStr]
                return
            else:
                gCodes = inputStr.split(",")
                cs = self._getCategoryStrByGCodes(gBuf, gCodes)
                if cs != None:
                    self.category = inputStr
                    self.categoryStr = cs
                    return
                else:
                    print("输入有误!")

    def _getCategoryStrByGCodes(self, gBuf, gCodes):
        gDescs = []
        for gc in gCodes:
            if gc in gBuf:
                gDescs.append(gBuf[gc])
            else:
                return None
        return ",".join(gDescs)


    def showMeta(self):
        print("类别: {0}, 搜索: {1}, 页码: {2}, 总条数: {3}, 总页数: {4}, 显示条码: [{5},{6})".format(
            self.categoryStr, self.searchName, self.pageNum, self.totle, self.count, self.begin, self.end))

    def searchAndShow(self):
        self.search()
        showItems(self.items)
        self.showMeta()

    def setPageNum(self, pageNum):
        if pageNum < 1:
            pageNum = 1
        elif pageNum > self.count:
            if self.count == 0:
                pageNum = 1
            else:
                pageNum = self.count
        self.pageNum = pageNum

class TopCategory:
    title = ""
    url = ""
    ended = False

    def __init__(self, title, url, ended = False):
        self.title = title
        self.url = url
        self.ended = ended

class Toper:
    categories = []
    index = 0
    items = []

    def __init__(self):
        url = "https://thepiratebay10.org/top"
        resp = requests.get(url)
        if resp.status_code != 200:
            print("网络请求出错, 请检查网络或访问的地址!!")
            sys.exit(1)
        resp.encoding = "utf-8"
        html = etree.HTML(resp.text)
        nodes = html.xpath('//table[@id="categoriesTable"]/tr/td/dl/*')
        for node in nodes:
            if node.tag == "dt":
                title = node.xpath('./a[1]/text()')[0].strip()
                url = node.xpath('./a[1]/@href')[0]
                self.categories.append(TopCategory("[ {0} ] ".format(title), "https://thepiratebay10.org"+url))
                title2 = "[ {0}({1}) ]".format(title, node.xpath('./a[2]/text()')[0].strip())
                url2 = node.xpath('./a[2]/@href')[0]
                self.categories.append(TopCategory(title2, "https://thepiratebay10.org"+url2, True))
            elif node.tag == "dd":
                subNodes = node.xpath('.//a')
                for subNode in subNodes:
                    title = subNode.xpath('./text()')[0].strip()
                    url = subNode.xpath('./@href')[0]
                    self.categories.append(TopCategory(title, "https://thepiratebay10.org"+url))
                self.categories[-1].ended = True

    def showCategories(self):
        for i, v in enumerate(self.categories):
            print(i , v.title, sep=":", end="  ")
            if v.ended:
                print()

    def setCategoryIndex(self, index):
        if (index < 0) | (index >= len(self.categories)):
            return False
        else:
            self.index = index
            return True

    def getTop(self):
        url = self.categories[self.index].url
        resp = requests.get(url)
        resp.encoding = "utf-8"
        html = etree.HTML(resp.text)
        # 设置items
        self.items = parseHtmlForItems(html)

    def getAndShow(self):
        self.getTop()
        showItems(self.items)


def runSearcher(searcher):
    inputStr = input("请输入搜索关键词(输出空白字符将退出): ").strip()
    if inputStr == "":
        return
    searcher.searchName = inputStr
    searcher.searchAndShow()
    while True:
        ops = input("i <item> 查看指定条目详情; g <page> 跳转到指定页码; p 上一页; n 下一页; s <keyword> 搜索指定关键词; r 刷新; c 设置查询类型; q 退出;\n")
        op = ops[:1]
        arg = ops[1:].strip()
        if op == "i":
            showItem(searcher.items, (int(arg)))
        elif op == "g":
            searcher.setPageNum(int(arg))
            searcher.searchAndShow()
        elif op == "p":
            searcher.setPageNum(searcher.pageNum - 1)
            searcher.searchAndShow()
        elif op == "n":
            searcher.setPageNum(searcher.pageNum + 1)
            searcher.searchAndShow()
        elif op == "s":
            if arg == "":
                print("输入有误(不允许为空)!")
            else:
                searcher.searchName = arg
                searcher.pageNum = 1
                searcher.searchAndShow()
        elif op == "r":
            searcher.searchAndShow()
        elif op == "c":
            searcher.setupCategory()
        elif op == "q":
            return

def runToper(toper):
    toper.showCategories()
    while True:
        inputStr = input("请输入类别编号[0, {0})(输入'q'将退出): ".format(len(toper.categories))).strip()
        if inputStr == "q":
            return
        index = int(inputStr)
        flag = toper.setCategoryIndex(index)
        if flag:
            toper.getAndShow()
            break
        else:
            print("输入有误!")
    while True:
        ops = input("i <item> 查看指定条目详情; g <no> 查询指定类别编号的热门条目; r 刷新; c 查看类别目录; q 退出;\n")
        op = ops[:1]
        arg = ops[1:].strip()
        if op == "i":
            showItem(toper.items, int(arg))
        elif op == "g":
            flag = toper.setCategoryIndex(int(arg))
            if flag:
                toper.getAndShow()
            else:
                print("输入有误!")
        elif op == "r":
            toper.getAndShow()
        elif op == "c":
            toper.showCategories()
        elif op == "q":
            return

if __name__ == "__main__":
    searcher = None
    toper = None
    while True:
        m = input("请输入模式('s'(搜索), 't'(热门))(输入'q'将退出): ").strip()
        if m == "q":
            break
        elif m == "s":
            if searcher == None:
                searcher = Searcher()
            runSearcher(searcher)
        elif m == "t":
            if toper == None:
                toper = Toper()
            runToper(toper)
