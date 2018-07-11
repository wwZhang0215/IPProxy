# -*- coding: utf-8 -*-
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

# if __name__ == '__main__':
#     ip = IP()
#     ip.setIP('0.0.0.0')
#     ip.setPort('1080')
#     ip.setType('https')
#     print ip.getProxyDict()
