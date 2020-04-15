'''
Function:
	微博评论爬虫
Author:
	Charles
微信公众号:
	Charles的皮卡丘
'''
import re
import time
import copy
import pickle
import requests
import argparse
import pandas as pd 

tags = re.compile('</?\w+[^>]*>')
comments, ids,genders = [], [], []


'''微博爬虫类'''
class weibo():
	def __init__(self, **kwargs):
		self.login_headers = {
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
								'Accept': '*/*',
								'Accept-Encoding': 'gzip, deflate, br',
								'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
								'Connection': 'keep-alive',
								'Origin': 'https://passport.weibo.cn',
								'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt='
							}
		self.login_url = 'https://passport.weibo.cn/sso/login'
		self.home_url = 'https://weibo.com/'
		self.headers = {
						'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
						}
		self.session = requests.Session()
		self.time_interval = 5
	'''获取评论数据'''
	def getComments(self, url, url_type='pc', max_page='all', out_filename='results', savename=None, is_print=True, **kwargs):
		# 判断max_page参数是否正确
		if not isinstance(max_page, int):
			if max_page != 'all':
				raise ValueError('[max_page] error, weibo.getComments -> [max_page] should be <number(int) larger than 0> or <all>')
		else:
			if max_page < 1:
				raise ValueError('[max_page] error, weibo.getComments -> [max_page] should be <number(int) larger than 0> or <all>')
		# 判断链接类型
		if url_type == 'phone':
			mid = url.split('/')[-1]
		elif url_type == 'pc':
			mid = self.__getMid(url)
		else:
			raise ValueError('[url_type] error, weibo.getComments -> [url_type] should be <pc> or <phone>')
		# 数据爬取
		headers = copy.deepcopy(self.headers)
		headers['Accept'] = 'application/json, text/plain, */*'
		headers['MWeibo-Pwa'] = '1'
		headers['Referer'] = 'https://m.weibo.cn/detail/%s' % mid
		headers['X-Requested-With'] = 'XMLHttpRequest'
		url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(mid, mid)
		num_page = 0
		comments_data = {}
		while True:
			num_page += 1
			print('[INFO]: Start to get the comment data of page%d...' % num_page)
			if num_page > 1:
				url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type={}'.format(mid, mid, max_id, max_id_type)
			res = self.session.get(url, headers=headers)
			comments_data[num_page] = res.json()
			try:
				comment_data = comments_data[num_page]['data']['data']
				for data in comment_data:
					comment = tags.sub('', data['text']) # 去掉html标签            
					weibo_id = data['id']
					gender = data['user']['gender']
					comments.append(comment)
					ids.append(weibo_id)
					genders.append(gender)
			except KeyError:
				pass

			if is_print:
				print(type(res.json()))
			try:
				max_id = res.json()['data']['max_id']
				max_id_type = res.json()['data']['max_id_type']
			except:
				break
			if isinstance(max_page, int):
				if num_page < max_page:
					time.sleep(self.time_interval)
				else:
					break
			else:
				if int(float(max_id)) != 0:
					time.sleep(self.time_interval)
				else:
					break
		if savename is None:
			savename = './pkl/comments_%s.pkl' % str(int(time.time()))

		df = pd.DataFrame({'ID': ids, '评论': comments, '性别':genders})
		df = df.drop_duplicates()
		df.to_csv(f'./csv/{out_filename}.csv', index=False, encoding='utf-8')
		with open(savename, 'wb') as f:
			pickle.dump(comments_data, f)
		return True
	'''模拟登陆'''
	def login(self, username, password):
		data = {
				'username': username,
				'password': password,
				'savestate': '1',
				'r': 'https://weibo.cn/',
				'ec': '0',
				'pagerefer': 'https://weibo.cn/pub/',
				'entry': 'mweibo',
				'wentry': '',
				'loginfrom': '',
				'client_id': '',
				'code': '',
				'qq': '',
				'mainpageflag': '1',
				'hff': '',
				'hfp': ''
				}
		res = self.session.post(self.login_url, headers=self.login_headers, data=data)
		if res.json()['retcode'] == 20000000:
			self.session.headers.update(self.login_headers)
			print('[INFO]: Account -> %s, login successfully...' % username)
			return True
		else:
			raise RuntimeError('[INFO]: Account -> %s, fail to login, username or password error...' % username)
	'''获取PC端某条微博的mid'''
	def __getMid(self, pc_url):
		headers = copy.deepcopy(self.headers)
		headers['Cookie'] = 'SUB=_2AkMrLtDRf8NxqwJRmfgQzWzkZI11ygzEieKdciEKJRMxHRl-yj83qhAHtRB6AK7-PqkF1Dj9vq59_dD6uw4ZKE_AJB3c;'
		res = requests.get(pc_url, headers=headers)
		mid = re.findall(r'mblog&act=(\d+)\\', res.text)[0]
		return mid


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="weibo comments spider")
	parser.add_argument('-u', dest='username', help='weibo username')
	parser.add_argument('-p', dest='password', help='weibo password')
	parser.add_argument('-m', dest='max_page', help='max number of comment pages to crawl(number<int> larger than 0 or all)', default=10)
	parser.add_argument('-l', dest='link', help='weibo comment link', default='https://weibo.com/1223178222/Hhdq4AV6k?filter=hot&root_comment_id=0&type=comment#_rnd1550995912971')
	parser.add_argument('-t', dest='url_type', help='weibo comment link type(pc or phone)', default='pc')
	parser.add_argument('-o', dest='csv_out', help='csv format file out name', default='results')
	args = parser.parse_args()
	wb = weibo()
	username = args.username
	password = args.password
	try:
		max_page = int(float(args.max_page))
	except:
		pass
	url = args.link
	url_type = args.url_type
	if not username or not password or not max_page or not url or not url_type:
		raise ValueError('argument error')
	wb.login(username, password)
	out_filename = args.csv_out
	wb.getComments(url, url_type, max_page, out_filename)