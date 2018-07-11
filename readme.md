# IPProxy
## 简介
自动从免费网站获取可用IP并提供ip自动选择的代理ip项目

### 使用说明
#####初始化IPProxy

``` python
import IPProxy
ipproxy = IPProxy() 
# 默认首先从save.txt读取ip列表
# 若IP总数不足15(数量可自定)
# 则自动从www.xicidaili.com获取ip列表
```
#####从ip池中获取ip

``` Python
import IPProxy
ipproxy = IPProxy()
rootUrl = 'http://www.baidu.com'
proxies = ipproxy.getAvailableIP(rootUrl)
# rootUrl为网站的根目录
# 如爬取网址http://www.xicidaili.com/nn/1时
# rootUrl为http://www.xicidaili.com
# getAvailableIP()会对IP池中的代理ip进行对应地址的连接测试，并返回一个可用的ip地址
# 如果在爬虫中使用了header等参数，可以填入getAvailableIP()的参数中
# 使用方法等同于requests.get()
# getAvailableIP()不支持params参数
```

#####访问失败
``` Python
import IPProxy
ipproxy = IPProxy()
rootUrl = 'http://www.baidu.com'
proxies = ipproxy.getAvailableIP(rootUrl)
try:
	requests.get(url,proxies=proxies)
except requests.exceptions.ProxyError:
# 或者一切由代理引发的错误
	ipproxy.delBadProxy(proxies)
# delBadProxy()可以将无法连接目标地址或被目标地址屏蔽的ip代理从代理池中移除
```
#####更多api信息
[more api](api.md)
