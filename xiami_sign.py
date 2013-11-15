#!/usr/bin/python3
#coding=utf-8 
import datetime
import re

from urllib.request import urlopen,install_opener,build_opener,Request,HTTPHandler,HTTPCookieProcessor
from http.cookiejar import CookieJar
from urllib.parse import urlencode

import smtplib
from email.mime.text import MIMEText
from email.utils     import formatdate
from email.header import Header 

#email notificaion 
smtpHost = 'smtp.xx.com'
sslPort  = 'xx'
fromMail = 'no-reply@xx.com'
username = 'no-reply@xx.com'
password = '*******'
 
#在此填写账户名（可多账户）
user_info=[
	{"email":"xx@xx.com","password":"xx"},
]

#xiami uris
site_urls={
	"index":r"http://www.xiami.com/web",
	"login":r"http://www.xiami.com/web/login",
	"signin":r"http://www.xiami.com/task/signin",
}

login_form={
	'LoginButton':'登陆',
	'remember': 1,
}

#flags
site_flags={
	"logged-in":r"我的虾米",
	"login-failed":"email或者密码错误",
	"identify-required":"请输入验证码",
	"not-signed-in":"还没有加入虾米网",
	"signed-in":"我的留言",
}

headers = {'Referer':'http://www.xiami.com/web/login', 'User-Agent':'Mozilla/5.0',}
uid_re="/web/friends/id/([0-9]*)\""

#=========================
def login(n):
	cookie_support= HTTPCookieProcessor(CookieJar())
	opener = build_opener(cookie_support, HTTPHandler)
	install_opener(opener)
	lf=login_form
	lf.update(user_info[n])
	
	login_url = 'http://www.xiami.com/web/login
'	login_data = urlencode(lf).encode("utf-8")
	login_headers = {'Referer':'http://www.xiami.com/web/login', 'User-Agent':'Opera/9.60',}
	login_request = Request(login_url, login_data, login_headers)
	content = urlopen(login_request).read().decode("utf-8")
	
	login_flag = None
	if content.find(site_flags["login-failed"])!=-1:
		print("%s %s:邮箱或密码错误.\r\n"%(datetime.datetime.now(),user_info[n]["email"]))
		sendmail(user_info[n]["email"], "账号 %s 登陆失败。\n账号或密码错误,请手动到虾米签到" %(user_info[n]["email"]))
	if content.find(site_flags["identify-required"])!=-1:
		print("%s %s:需要输入验证码.\r\n"%(datetime.datetime.now(),user_info[n]["email"]))
		sendmail(user_info[n]["email"], "账号 %s 登陆失败。\n需要输入验证码,请手动到虾米签到" %(user_info[n]["email"]))
	if content.find(site_flags["logged-in"])!=-1:
		print("%s %s:登陆成功."%(datetime.datetime.now(),user_info[n]["email"]))
		login_flag = 'success'
	if login_flag==None:
		return	
		
	profile_url="http://www.xiami.com/web/profile"
	profile_request = Request(profile_url,headers=login_headers)
	content = urlopen(profile_request).read().decode("utf-8")
	install_opener(opener)
	
	UID=re.findall(uid_re,content)[0]
	checkin_url="http://www.xiami.com/web/checkin/id/"+UID
	checkin_headers = {'Referer':'http://www.xiami.com/web/', 'User-Agent':'Opera/9.99',}
	checkin_request = Request(checkin_url, None, checkin_headers)
	checkin_response = urlopen(checkin_request).read().decode("utf-8")
	checkin_pattern = re.compile(r'<a class="check_in" href="(.*?)">')
	checkin_result = checkin_pattern.search(checkin_response)

	if not checkin_result:
		pattern = re.compile(r'<div class="idh">已连续签到(\d+)天</div>')
		result = pattern.search(checkin_response)
		if result:
			print("亲，账号%s今天已经签到过了,当前已经签到 %s 天" %(user_info[n]["email"], result.group(1)))
			sendmail(user_info[n]["email"], "亲,账号%s今天已经签到过了,当前已经签到了%s天" %(user_info[n]["email"], result.group(1)))
			return None;
		else :
			print("账号%s签到失败" %(user_info[n]["email"]))
			sendmail(user_info[n]["email"], "账号%s签到失败,请手动到虾米签到" %(user_info[n]["email"]))
			return None
	checkin_url = 'http://www.xiami.com' + checkin_result.group(1)
	checkin_headers = {'Referer':'http://www.xiami.com/web', 'User-Agent':'BH_Toolchain0.5',}
	checkin_request = Request(checkin_url, None, checkin_headers)
	checkin_response = urlopen(checkin_request).read().decode("utf-8")
	pattern = re.compile(r'<div class="idh">已连续签到(\d+)天</div>')
	result = pattern.search(checkin_response)
	if result:
		print("账号 %s 签到成功,当前已经签到 %s 天" %(user_info[n]["email"], result.group(1)))
		sendmail(user_info[n]["email"], "亲，你的账号%s签到成功,当前已经签到%s天" %(user_info[n]["email"], result.group(1)))
		return None
	else :
		print("账号 %s 签到失败" %(user_info[n]["email"]))
		sendmail(user_info[n]["email"], "账号%s签到失败,请手动到虾米签到" %(user_info[n]["email"]))
		return None

def sendmail(email, message):
	#邮件标题和内容
	subject  = u'[虾米签到]签到结果'
	body     = u'签到结果：\n' + message
	 
	#初始化邮件
	encoding = 'utf-8'
	mail = MIMEText(body.encode(encoding),'plain',encoding)
	mail['Subject'] = Header(subject,encoding)
	mail['From'] = fromMail
	mail['To'] = email
	mail['Date'] = formatdate()
	 
	try:
		smtp = smtplib.SMTP_SSL(smtpHost,sslPort)
		smtp.ehlo()
		smtp.login(username,password)
		smtp.sendmail(fromMail,email,mail.as_string())
		smtp.close()
		print('send mail seccessfully')
	except Exception:
		print ('Error: unable to send email')

#=========================
if __name__=="__main__":
	#print(script_info)
	for i in range(len(user_info)):
		login(i)