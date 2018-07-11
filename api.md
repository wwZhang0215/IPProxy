# Document

> \_\_init\_\_(self, maxip=15, online=True)

* 初始化ipproxy
	* :param maxip:ip池中最大代理ip数量，默认值15
    * :param online:是否从网络获取免费ip代理，默认True
    
&nbsp;

> addToPool(self, address, port, httpType='http')

* 手动添加ip到ip池中
	* :param address: ip地址
    * :param port: 端口号
    * :param httpType: http/https, 默认http
    
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

> getOnlineIP(self)

* 从代理网站中自动获取可用代理

&nbsp;

> \_\_del\_\_(self)

* 析构函数
* 在程序退出时，自动将ip池中的所有代理保存至save.txt，便于下次使用