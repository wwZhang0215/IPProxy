# -*- coding: utf-8 -*-
import time

import requests
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# from IP import IP


class IPProxy:
    def __init__(self, maxip=15, online=True, autoRefresh=True, country='中国', minPoints=30, maxLatency=3):
        self.lock = threading.Lock()
        self.IPPool = []
        self.failedPool = []
        self.checkedUrl = []
        self.maxip = maxip
        # init from saved file

        if online and country == '中国':
            self.addFromFile()
            self.getChineseIP()
        elif online and country != '中国':
            self.addFromFile(foreign=True)
            self.getForeignIP(country=country, minPoints=minPoints, maxLatency=maxLatency)
        self.__save2File()
        if autoRefresh:
            self.__autoRefreshThread = threading.Thread(target=self.__autoRefresh, args=((country == '中国'), country, minPoints, maxLatency))
            self.__autoRefreshThread.setDaemon(True)
            self.__autoRefreshThread.start()

    # 手动增加IP代理地址
    def addToPool(self, address, port, httpType='http', foreign='c', location='unknown'):
        ip = self.IP()
        ip.setProxy(httpType, address, port, foreign, location)
        if ip in self.IPPool:
            return
        if self.__checkConnection(ip):
            # self.lock.acquire()  # lock
            self.IPPool.append(ip)
            # self.lock.release()  # unlock
            print 'add proxy ' + ip.getString() + ' (' + str(len(self.IPPool)) + '/' + str(self.maxip) + ')'
        else:
            return 'proxy ip not usable'

    # 当检测到无法访问时调用这个函数
    # {a:b}
    def delBadProxy(self, proxies):
        for proxy in proxies:
            string = proxies[proxy]
            spilt = string.split(':')
            ip = self.IP()
            ip.setProxy(proxy, spilt[0], spilt[1])
            # under lock
            self.lock.acquire()
            self.IPPool.remove(ip)
            self.failedPool.append(ip._ip)
            self.lock.release()

    # 从文件中读取ip地址
    # 每行一个ip
    # ip格式 http/https空格*.*.*.*空格端口号空格c/f
    def addFromFile(self, filename='save.txt', foreign=False):
        # if os.path.exists(filename):
        #     ipFile = open(filename, 'r')
        # else:
        #     os.mknod(filename)
        ipFile = open(filename, 'a+')

        # under lock
        self.lock.acquire()
        for line in ipFile.readlines():
            if line == '\n':
                break
            ipSet = line.split('\n')[0].split(' ')
            if (ipSet[3] == 'f' and foreign == False) or (ipSet[3] == 'c' and foreign == True):
                continue
            ip = self.IP()
            ip.setProxy(ipSet[0], ipSet[1], ipSet[2], ipSet[3])
            if self.__checkConnection(ip) is True:
                self.IPPool.append(ip)
                print 'add proxy ' + ip.getString() + ' (' + str(len(self.IPPool)) + '/' + str(self.maxip) + ')'
            if len(self.IPPool) >= self.maxip:
                break
        ipFile.close()
        self.lock.release()

    def __checkConnection(self, IP, url='http://www.baidu.com', **kwargs):
        try:
            # try1 = IP.getProxyDict()
            response = requests.get(url, proxies=IP.getProxyDict(), timeout=5, **kwargs)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.ProxyError,
                requests.exceptions.ConnectionError), e:
            # print 'failed'
            return False
        else:
            if response.status_code == 200:
                return True
            elif response.status_code == 302 or response.status_code == 403:
                IP.banList.append(url)
                return "banned"
            return response.status_code

    def checkConnection(self, url='http://www.baidu.com', **kwargs):
        # lock
        self.lock.acquire()
        for ip in self.IPPool:
            try:
                if self.__checkConnection(ip, url, **kwargs) is not True:
                    ip.banList.append(url)
            except:
                ip.banList.append(url)
                continue
        self.lock.release()

    # rootUrl:网页根地址,如http://www.baidu.com
    def __getAllAvailableIP(self, rootUrl='http://www.baidu.com', minAvailable=0, **kwargs):
        availableIPs = []
        if rootUrl not in self.checkedUrl:
            print 'checking ip available for ' + rootUrl
            self.checkConnection(rootUrl, **kwargs)
            self.checkedUrl.append(rootUrl)

        for ip in self.IPPool:
            if rootUrl in ip.banList:
                continue
            else:
                availableIPs.append(ip)
        if len(availableIPs) <= minAvailable:
            print'no proxy ip available'
            print'getting online ips'
            # return 'no proxy ip available'
            self.lock.acquire()
            self.checkedUrl.remove(rootUrl)
            for ip in self.IPPool:
                if rootUrl in ip.banList:
                    self.IPPool.remove(ip)
                    self.failedPool.append(ip._ip)
            self.lock.release()
            self.getChineseIP()
            availableIPs = self.__getAllAvailableIP(rootUrl)

        return availableIPs

    r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

    def getAllAvailableIP(self, rootUrl='http://www.baidu.com', minAvailable=0, **kwargs):
        allIPs = self.__getAllAvailableIP(rootUrl, minAvailable, **kwargs)
        availableIPs = []
        for ip in allIPs:
            availableIPs.append(ip.getProxyDict())
        return availableIPs

    # 获取单个
    def getAvailableIP(self, rootUrl='http://www.baidu.com', **kwargs):
        ips = self.__getAllAvailableIP(rootUrl, **kwargs)
        if ips == 'no proxy ip available':
            return {}
        ips.sort()
        ips[0].lastUsedTime = time.time()
        return ips[0].getProxyDict()

    # 美国：us 巴西：br 印尼：id 俄罗斯：ru 法国：fr 印度：in 香港：hk 泰国：th 孟加拉：bd
    def getForeignIP(self, country='中国', minPoints=50, maxLatency=5):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=chrome_options)
        countryDict = {'中国': 'cn',
                       '美国': 'us',
                       '巴西': 'br',
                       '印尼': 'id',
                       '俄罗斯': 'ru',
                       '法国': 'fr',
                       '印度': 'in',
                       '香港': 'hk',
                       '泰国': 'th',
                       '孟加拉': 'bd',
                       }
        if not countryDict.has_key(country):
            print '无法找到该国家代理,自动寻找中国代理'
            country = 'cn'
        else:
            country = countryDict[country]
        self.lock.acquire()
        # header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        # payload = {'page': '1'}
        url = 'https://proxy.coderbusy.com/classical/country/'+country+'.aspx?page=1'
        while True:
            try:
                if len(self.IPPool) >= self.maxip:
                    break
                driver.get(url)
                # soupIP = BeautifulSoup(response, 'html.parser')
                trList = driver.find_elements_by_tag_name('tr')
                for tr in trList[1:]:
                    tdList = tr.find_elements_by_tag_name('td')
                    ip = tdList[0].text.strip()
                    if ip in self.failedPool:
                        # print 'skip'
                        continue
                    points = tdList[1].text
                    port = tdList[2].text
                    protocol = tdList[5].text.strip()
                    delay = tdList[10].text[:-1]
                    if float(points) < minPoints or float(delay) > maxLatency:
                        continue
                    if protocol == 'HTTP':
                        self.addToPool(ip, port, foreign='f')
                    elif protocol == 'HTTPS':
                        self.addToPool(ip, port, httpType='https', foreign='f')
                    if len(self.IPPool) >= self.maxip:
                        break
                pages = driver.find_elements_by_class_name('page-item')
                nextPage = pages[len(pages) - 3].find_element_by_tag_name('a').get_attribute('href')
                lastPage = pages[len(pages) - 2].find_element_by_tag_name('a').get_attribute('href')

                if nextPage == lastPage:
                    break
                else:
                    url = nextPage
            except Exception, e:
                print e.message
                continue
        self.lock.release()

    def getChineseIP(self):
        self.lock.acquire()
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        for page in range(1, 5):
            try:
                if len(self.IPPool) >= self.maxip:
                    break
                response = requests.get('http://www.xicidaili.com/nn/' + str(page), headers=header).text
                soupIP = BeautifulSoup(response, "html.parser")
                trs = soupIP.find_all('tr')
                for tr in trs[1:]:
                    tds = tr.find_all('td')
                    ip = tds[1].text.strip()
                    if ip in self.failedPool:
                        # print 'skip'
                        continue
                    port = tds[2].text.strip()
                    location = tds[3].text.strip()
                    protocol = tds[5].text.strip()
                    if protocol == 'HTTP':
                        self.addToPool(ip, port, location=location)
                    elif protocol == 'HTTPS':
                        self.addToPool(ip, port, httpType='https', location=location)
                    if len(self.IPPool) >= self.maxip:
                        break
            except:
                continue
        self.lock.release()

    def __autoRefresh(self, china, country='中国', minPoints=30, maxLatency=3):
        while 1:
            # 每分钟刷新
            time.sleep(60)
            print 'refresh'
            if len(self.IPPool) < self.maxip / 2:
                if china:
                    self.getChineseIP()
                else:
                    self.getForeignIP(country, minPoints, maxLatency)
            self.__save2File()

    def __save2File(self):
        # write pool to file
        saveFile = open('save.txt', 'w')
        for ip in self.IPPool:
            saveFile.write(ip.printString() + '\n')
        saveFile.close()

    def __del__(self):
        self.__save2File()

    class IP:
        def __init__(self):
            self._httpType = 'http'  # http/https
            self._ip = '127.0.0.1'
            self._port = '80'
            self.banList = []
            self.lastUsedTime = 0
            self.foreign = 'c'
            self.location = 'unknown'

        def setProxy(self, httpType, ip, port, foreign='c', location='unknown'):
            self.setType(httpType)
            self.setPort(port)
            self.setIP(ip)
            self.foreign = foreign
            self.location = location

        def setType(self, httpType):
            self._httpType = httpType

        def setIP(self, ip):
            self._ip = ip

        def setPort(self, port):
            self._port = port

        def getProxyDict(self):
            return {self._httpType: self._ip + ':' + self._port}

        def getString(self):
            return self._httpType + ' ' + self._ip + ' ' + self._port

        def printString(self):
            return self._httpType + ' ' + self._ip + ' ' + self._port + ' ' + self.foreign

        def __cmp__(self, other):
            if self.getString() == other.getString():
                return 0
            if self.lastUsedTime < other.lastUsedTime:
                return -1
            else:
                return 1


if __name__ == '__main__':
    # test = IPProxy(maxip=5, country='美国', maxLatency=10, minPoints=5)
    # test.addFromFile('ip.txt')
    # testip = IP()
    # testip.setProxy('https', '0.0.0.0', '80')
    # test.IPPool.append(testip)
    # testip = IP()
    # testip2 = IP()
    # lists = [testip]
    # a = testip2 in lists
    # print a
    test = IPProxy()
    requests.get('https://www.bilibili.com', proxies=test.IPPool[0].getProxyDict(), verify=False)
    print test.getAllAvailableIP('https://www.bilibili.com')
    # print test.getAvailableIP('http://www.bilibili.com', headers={})
    # print test.getAllAvailableIP('http://www.bilibili.com', 9)

    # print test.gettAvailableIP('http://www.baidu.com')
    # foreign = IPProxy(maxip=5, autoRefesh=False, online=False)
    # foreign.getForeignIP(maxLatency=1000, minPoints=0)
