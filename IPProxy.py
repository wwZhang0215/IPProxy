# -*- coding: utf-8 -*-
import os
import time

import requests
import threading
from bs4 import BeautifulSoup

# from IP import IP


class IPProxy:
    def __init__(self, maxip=15, online=True):
        self._autoRefreshThread = threading.Thread(target=self._autoRefresh)

        self.lock = threading.Lock()
        self.IPPool = []
        self.failedPool = []
        self.checkedUrl = []
        self.maxip = maxip
        # init from saved file
        self.addFromFile()
        if online:
            self.getOnlineIP()
        # self._autoRefreshThread.start()

    # 手动增加IP代理地址
    def addToPool(self, address, port, httpType='http'):
        ip = self.IP()
        ip.setProxy(httpType, address, port)
        if ip in self.IPPool:
            return
        if self._checkConnection(ip):
            # self.lock.acquire()  # lock
            self.IPPool.append(ip)
            # self.lock.release()  # unlock
            print 'add proxy (' + str(len(self.IPPool)) + '/' + str(self.maxip) + ')'
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
    # ip格式 http/https空格*.*.*.*空格端口号
    def addFromFile(self, filename='save.txt'):
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
            ip = self.IP()
            ip.setProxy(ipSet[0], ipSet[1], ipSet[2])
            if self._checkConnection(ip) is True:
                self.IPPool.append(ip)
                print 'add proxy (' + str(len(self.IPPool)) + '/' + str(self.maxip) + ')'
            if len(self.IPPool) >= self.maxip:
                break
        ipFile.close()
        self.lock.release()

    def _checkConnection(self, IP, url='http://www.baidu.com', **kwargs):
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

    def checkConnection(self, url, **kwargs):
        # lock
        self.lock.acquire()
        for ip in self.IPPool:
            try:
                if self._checkConnection(ip, url, **kwargs) is not True:
                    ip.banList.append(url)
            except:
                ip.banList.append(url)
                continue
        self.lock.release()

    # rootUrl:网页根地址,如http://www.baidu.com
    def _getAllAvailableIP(self, rootUrl, minAvailable=0, **kwargs):
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
            self.getOnlineIP()
            availableIPs = self._getAllAvailableIP(rootUrl)

        return availableIPs

    r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

    def getAllAvailableIP(self, rootUrl, minAvailable=0, **kwargs):
        allIPs = self._getAllAvailableIP(rootUrl, minAvailable, **kwargs)
        availableIPs = []
        for ip in allIPs:
            availableIPs.append(ip.getProxyDict())
        return availableIPs

    # 获取单个
    def getAvailableIP(self, rootUrl, **kwargs):
        ips = self._getAllAvailableIP(rootUrl, **kwargs)
        if ips == 'no proxy ip available':
            return {}
        ips.sort()
        ips[0].lastUsedTime = time.time()
        return ips[0].getProxyDict()



    def getOnlineIP(self):
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
                    protocol = tds[5].text.strip()
                    if protocol == 'HTTP':
                        self.addToPool(ip, port)
                    elif protocol == 'HTTPS':
                        self.addToPool(ip, port, 'https')
                    if len(self.IPPool) >= self.maxip:
                        break
            except:
                continue
        self.lock.release()

    def _autoRefresh(self):
        while 1:
            # 每分钟刷新
            time.sleep(60)
            print 'refresh'
            if len(self.IPPool) < self.maxip/2:
                self.getOnlineIP()

    def __del__(self):
        # write pool to file
        saveFile = open('save.txt', 'w')
        for ip in self.IPPool:
            saveFile.write(ip.getString() + '\n')
        saveFile.close()


    class IP:
        def __init__(self):
            self._httpType = 'http'  # http/https
            self._ip = '127.0.0.1'
            self._port = '80'
            self.banList = []
            self.lastUsedTime = 0

        def setProxy(self, httpType, ip, port):
            self.setType(httpType)
            self.setPort(port)
            self.setIP(ip)

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

        def __cmp__(self, other):
            if self.getString() == other.getString():
                return 0
            if self.lastUsedTime < other.lastUsedTime:
                return -1
            else:
                return 1


if __name__ == '__main__':
    test = IPProxy()
    # test.addFromFile('ip.txt')
    # testip = IP()
    # testip.setProxy('https', '0.0.0.0', '80')
    # test.IPPool.append(testip)
    # testip = IP()
    # testip2 = IP()
    # lists = [testip]
    # a = testip2 in lists
    # print a
    # test.getOnlineIP()
    # print test.getAllAvailableIP('http://www.bilibili.com')
    # print test.getAvailableIP('http://www.bilibili.com', headers={})
    test.__del__()
    # print test.getAllAvailableIP('http://www.bilibili.com', 9)

    # print test.gettAvailableIP('http://www.baidu.com')
