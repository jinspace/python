__author__ = 'JC'
# -*- coding:utf-8 -*- 

import urllib
import urllib.request
import re

class Tool:
	#去除7位长空格
	removeImg = re.compile(' {7}|')
	#删除超链接标签
	removeAddr = re.compile('<a.*?>|</a>')
	#把换行的标签换为\n
	replaceLine = re.compile('<tr>|<div>|</div>|</p>')
	#将表格制表<td>替换为\t
	replaceTD= re.compile('<td>')
	#把段落开头换为\n加空两格
	replacePara = re.compile('<p.*?>')
	#将换行符或双换行符替换为\n
	replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
	removeExtraTag = re.compile('<.*?>')
	def replace(self,text):
	
		text = re.sub(self.removeImg,"",text)		
		text = re.sub(self.removeAddr,"",text)		
		text = re.sub(self.replaceLine,"\n",text)
		text = re.sub(self.replaceTD,"\t",text)
		text = re.sub(self.replacePara,"\n    ",text)
		text = re.sub(self.replaceBR,"\n",text)
		text = re.sub(self.removeExtraTag,"",text)			
		#strip()将前后多余内容删除
		return text.strip()

class BDTB:
	#初始化，传入基地址及只看楼主参数
	def __init__(self,baseUrl,seeLZ,floorTag):
		#base链接地址
		self.baseUrl = baseUrl
		#是否只看楼主
		self.seeLZ = '?see_lz='+str(seeLZ)
		#HTML标签剔除工具类对象
		self.tool = Tool()
		#全局file变量，文件写入操作对象
		self.file = None
		#楼层标号，初始为1
		self.floor = 1
		#默认的标题，如果没有成功获取到标题的话则会用这个标题
		self.defaultTitle = u"百度贴吧"
		#是否写入楼分隔符的标记
		self.floorTag = floorTag

		self.flag = 0

	def getPage(self,pageNum):
		try:
			#构建URL
			url = self.baseUrl + self.seeLZ + '&pn=' + str(pageNum)
			request = urllib.request.Request(url)
			response = urllib.request.urlopen(request)
			#返回UTF-8格式编码内容
			content = response.read().decode('utf-8')
			return content
		#无法连接，报错
		except urllib.request.URLError as e:
			if hasattr(e,"reason"):
				print ("连接百度贴吧失败,错误原因", e.reason)
				return None
	#获取帖子标题
	def getTitle(self,page):
		#得到标题的正则表达式
		pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
		result = re.search(pattern,page)
		if result:
			#如果存在，则返回标题
			return result.group(1)
		else:
			return None

	#获取帖子一共有多少页
	def getPageNum(self,page):
		pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>',re.S)
		result = re.search(pattern,page)
		if result:
			return result.group(1).strip()
		else:
			return None

	#获取每一层楼的内容,传入页面内容		
	def getContent(self,page):
		pattern = re.compile('<div id="post_content_.*?>(.*?)</div>',re.S)
		results = re.findall(pattern,page) #得到的是list对象
		contents = []
		for result in results:
			content = "\n"+self.tool.replace(result)+"\n"
			#contents = contents + content
			contents.append(content)
		return contents

	def setFileTitle(self,title):
		#如果标题不是为None，即成功获取到标题
		if title is not None:
			self.file = open(title + ".txt","w+")
		else:
			self.file = open(self.defaultTitle + ".txt","w+")

	def writeData(self,contents):
		#向文件写入每一楼的信息
		for item in contents[::-1]:
			if self.floorTag == 1:
				#楼之间的分隔符
				floorLine = "\n" + str(self.floor) + "-----------------------------------------------------------------------------------------\n"
				self.file.write(floorLine)
			self.file.write(item)
			self.floor += 1

	def start(self):
		pageIndex = self.getPage(1)
		title = self.getTitle(pageIndex)
		pageNum = self.getPageNum(pageIndex)
		self.setFileTitle(title)
		contents = self.getContent(pageIndex)
		print("\n标题是：",title, "\n共",pageNum,"页")
		#print(contents)
		
		if pageNum == None:
			print("URL已失效，请重试")
			return
			
		try:
			print("该帖子共有" + str(pageNum) + "页")
			#倒序页面写入，因为帖子是倒序排列
			for i in range(int(pageNum),0,-1):
				print("正在写入第" + str(i) + "页数据")
				page = self.getPage(i)
				contents = self.getContent(page)
				self.writeData(contents)
		#出现写入异常
		except IOError as e:
			print("写入异常，原因" + e.message)
		finally:
			self.file.close()
			print("写入任务完成")
		

print("请输入帖子代号")
baseURL = 'http://tieba.baidu.com/p/3138733512'
#baseURL = 'http://tieba.baidu.com/p/3138733512' + str(input('http://tieba.baidu.com/p/3138733512'))
bdtb = BDTB(baseURL,1,1)
bdtb.start()