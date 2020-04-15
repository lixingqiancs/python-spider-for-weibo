'''
Function:
	简单的评论数据可视化
Author:
	Charles
微信公众号:
	Charles的皮卡丘
'''
import os
import re
import jieba
import pickle
from wordcloud import WordCloud


'''词云'''
def drawWordCloud(words, title, savepath='./results'):
	if not os.path.exists(savepath):
		os.mkdir(savepath)
	wc = WordCloud(font_path='simkai.ttf', background_color='white', max_words=2000, width=1920, height=1080, margin=5)
	wc.generate_from_frequencies(words)
	wc.to_file(os.path.join(savepath, title+'.png'))


'''统计词频'''
def statistics(texts, stopwords):
	words_dict = {}
	for text in texts:
		temp = jieba.cut(text)
		for t in temp:
			if t in stopwords or t == 'unknow':
				continue
			if t in words_dict.keys():
				words_dict[t] += 1
			else:
				words_dict[t] = 1
	return words_dict


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="weibo comments analysis")
	parser.add_argument('-i', dest='input', help='input file')
	parser.add_argument('-o', dest='output', help='output file')
	args = parser.parse_args()
	input_file = args.input
	out_file = args.output

	with open(input_file, 'rb') as f:
		data = pickle.load(f)
	texts = []
	for key, value in data.items():
		for each in value['data']['data']:
			text = each.get('text')
			text = re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+', '', text)
			if text:
				texts.append(text)
	stopwords = open('./stopwords.txt', 'r', encoding='utf-8').read().split('\n')[:-1]
	words_dict = statistics(texts, stopwords)
	drawWordCloud(words_dict, out_file, savepath='./results')