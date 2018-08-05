# Document

> \_\_init\_\_(self, maxip=15, online=True, autoRefresh=True, country='中国', minPoints=30, maxLatency=3)

* 初始化ipproxy
	* :param maxip:ip池中最大代理ip数量，默认值15
    * :param online:是否从网络获取免费ip代理，默认True
    * :param autoRefresh:是否启用自动刷新线程
    * :param country:当需要使用国外代理时修改此参数， 可用国家和地区：*美国 巴西 印尼 俄罗斯 法国 印度 香港 泰国 孟加拉*
    * :param minPoints:国外代理评分最低限制，国内代理使用时可无视
    * :param maxLatency:国外代理允许最长延迟，国内代理使用时可无视
    
&nbsp;

> addToPool(self, address, port, httpType='http', foreign='c')

* 手动添加ip到ip池中
	* :param address: ip地址
    * :param port: 端口号
    * :param httpType: http/https, 默认http
    * :param foreign: c/f 默认c 用于标示该ip属于境内或者境外
    
&nbsp;

> delBadProxy(self, proxies)


* 用于删除出现错误的代理
	* :param proxies: 代理 eg.{'http':'127.0.0.1:80'}
    
&nbsp;

> addFromFile(self, filename='save.txt')

* 从文件添加ip代理
	* :param filename: 读取的文件名
    * 文件格式：
    	* 每行一个ip
        * 格式：http/https ip port
        * eg.
        * http 127.0.0.1 80
     
&nbsp;

> checkConnection(self, url, \*\*kwargs)

* 检查ip池中所有ip对url的连接状况
	* :param url: 目标地址
    * :param \*\*kwargs: request所需参数，如 header、ua等，用法同request.get()中的\*\*kwargs

&nbsp;

> getAllAvailableIP(self, rootUrl, minAvailable=0, \*\*kwargs)

* 获取ip池中所有可以连接rootUrl的代理
	* :param rootUrl: 爬虫目标地址的根地址
    * :param minAvailable: 最少代理数量，若可用ip少于此值则会重新从网站获取ip
    * :param \*\*kwargs: request所需参数，如 header、ua等，用法同request.get()中的\*\*kwargs，建议与最终爬取链接所使用的kwargs相同以保证代理的可用性
    * :return \[{proxy}, {proxy}]
    * :returnType List
    
&nbsp;

> getAvailableIP(self, rootUrl, \*\*kwargs)

* 从ip池中获取一个代理
	* :param rootUrl: 爬虫目标地址的根地址
    * :param \*\*kwargs: request所需参数，如 header、ua等，用法同request.get()中的\*\*kwargs，建议与最终爬取链接所使用的kwargs相同以保证代理的可用性
    * :return {proxy}
    * :returnType Dict
    
&nbsp;

> getForeignIP(self, country='中国', minPoints=50, maxLatency=5)

* 从代理网站中自动获取可用国外代理
    * 参数列表同__init__

&nbsp;

> getChineseIP(self):

* 从代理网站中自动获取可用国内代理

&nbsp;

> \_\_del\_\_(self)

* 析构函数
* 在程序退出时，自动将ip池中的所有代理保存至save.txt，便于下次使用