from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, StreamingHttpResponse
from django.template import loader
from .models import Dataset,Domain
from django.urls import reverse
from datetime import datetime, timedelta
import operator
from . import Keyword_Generation as kg
import json
from django.contrib import messages
import json
import csv
import os
from django.core.cache import cache
from django.utils import timezone
import pytz
import re
import random
import pandas as pd
from dateutil import parser
import pycountry

data = None
#keyword_set = {}
keyword__domain = {}
#IDS = {} #store matching level between searching word and all dataset
domain =""
cart_list = []

def is_valid_country_name(country_name):
	try:
		pycountry.countries.lookup(country_name)
		return True
	except LookupError:
		return False

def get_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
	else:
		ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
	return ip

def isNumeric(n):
	float_regex = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
	if float_regex.match(n):
		return True
	else:
		return False

def isDate(n):
	date_regex = re.compile(r'^\d{2}/\d{2}/\d{2}$')
	if date_regex.match(n):
		return True
	else:
		return False

def get_cache(ip,name):
	if cache.get(str(ip)+"_"+name) == None:
		return None
	else :
		return cache.get(str(ip)+"_"+name)

"""
# sentence is the string that need to turn to regular expression
# return: regular expression according to the sentence 

"""

def turn_reg(sentence):
	split_list = list(sentence)
	last_type = ""
	regex_pattern = r''
	for i in range(len(split_list)):
		if split_list[i].isdigit():
			if last_type != "digit":
				regex_pattern += r'\d*'

			last_type = "digit"
		elif split_list[i].isalpha() and split_list[i].islower():

			if last_type != "lower":
				regex_pattern += r'[a-z]*'
			last_type = "lower"

		elif split_list[i].isalpha() and split_list[i].isupper():

			if last_type != "upper":
				regex_pattern += r'[A-Z]*'
			last_type = "upper"
		else:
			regex_pattern += re.escape(split_list[i])

			last_type = "special"


	return regex_pattern

"""
# check how much cell in the column has the same format
# data : queryset of dataset model  
# col: the column name of dataset
# return: the number of cell which has the same format

max number of cell which has the same format / total number of cell in the column
"""
def consistent_num(data,col):
	"""
	col_detail contain [mean(index=0),min(index=1),max(index=2),distict(index=3), 
						std(index=4),type(index=5),missing_num(index=6)]
	"""
	col_detail = (data.column_summary)[col] 
	if col_detail[5] == "str":
		df = pd.read_csv(data.host_link,encoding = 'ISO-8859-1')
		column = df[col].tolist()
		match_dict = {}
		for cell in column:
			regex_pattern = turn_reg(cell)
			if regex_pattern in match_dict:
				match_dict[regex_pattern] +=1
			else:
				match_dict[regex_pattern] = 1
		return (max(match_dict.items(), key=lambda x:x[1]))[1]
	else:
		return data.total_records



def search(kw,data):
	keyword_set = {}
	for d in data:
		sentence = ''
		for col_name in list(d.column_summary.keys()):
			sentence = sentence + col_name +" "
		keywords = kg.extact(sentence)
		for k in keywords: # get every keyword from the the database
			if k in keyword_set:# if the keyword exist
				if d.id in keyword_set[k]:
					#if the keyword exist and id already recorded, the frequency increase
					keyword_set[k][d.id]+=1
				else:
					#if the keyword exist and id isn't recorded, record it 
					keyword_set[k][d.id] = 1
			else:
				keyword_set[k] = {d.id:1}


	# processed input query and displays candidate datasets
	IDS = {}
	#  keyword_set = keyword__domain[domain]
	search_word_set = kg.extact(kw)
	for w in search_word_set:
		if w in keyword_set:
			for item in keyword_set[w].items():
				if item[0] in IDS:
					IDS[item[0]]+= item[1]
				else:
					IDS[item[0]] = item[1]
		else:
			syn_list = kg.synonyms(w)
			for syn in syn_list:
				if syn in keyword_set:
					for item in keyword_set[syn].items():
						if item[0] in IDS:
							IDS[item[0]]+= item[1]
						else:
							IDS[item[0]] = item[1]
		
	#sort the dataset by the mathching level
	IDS = dict(sorted(IDS.items(), key=lambda x:x[1], reverse=True))
	data = Dataset.objects.filter(id__in=list(IDS.keys()))
	return data


def index(request):
	#global data,domain,keyword__domain
	context ={}
	ip = get_ip(request)
	data = cache.get(str(ip)+"_data")
	domain = cache.get(str(ip)+"_domain")
	domain_data = cache.get(str(ip)+"_domain_data")
	if request.method == 'POST':
		domain_sel = request.POST.get('domain','')
		sort = request.POST.get('sort','')
		search1 = request.POST.get('search1','')
		search2 = request.POST.get('search2','')

		if domain_sel != '':#for get all domain name 
			domain_id = Domain.objects.filter(name=domain_sel).values()
			data = Dataset.objects.filter(domain_id = domain_id[0]['id'])
			domain_data = data
			domain = domain_sel
			cache.set(str(ip)+"_data", data)
			cache.set(str(ip)+"_domain_data",data)
			cache.set(str(ip)+"_domain", domain)

		elif sort != '' and data != None:# sort the data 
			if sort == 'price_l_h' :
				data = sorted(data, key=operator.attrgetter('price'))
			elif sort == 'price_h_l':
				data = sorted(data, key=operator.attrgetter('price'),reverse=True)
			else:
				data = sorted(data, key=operator.attrgetter('pub_by'))
				#do not do sort by username(because l do not add user name)
			cache.set(str(ip)+"_data", data)
		elif search1 != ''and data != None:
			#seach algorithms 
			#if domain not in keyword__domain: 
			keyword_set = {}
			for d in domain_data:
				sentence = ''
				#do not add seller name in sentence, because not store user name
				sentence = sentence + d.title+" "+d.description+" "+ d.pub_by+" "
				keywords = kg.extact(sentence)
				for k in keywords: # get every keyword from the the database
					if k in keyword_set:# if the keyword exist
						if d.id in keyword_set[k]:
							#if the keyword exist and id already recorded, the frequency increase
							keyword_set[k][d.id]+=1
						else:
							#if the keyword exist and id isn't recorded, record it 
							keyword_set[k][d.id] = 1
					else:
						keyword_set[k] = {d.id:1}
					#IDS[d.id] = 0
				#keyword__domain[domain] = keyword_set
				#print(keyword_set)


			# processed input query and displays candidate datasets
			IDS = {}
			#keyword_set = keyword__domain[domain]
			search_word_set = kg.extact(search1)
			for w in search_word_set:
				if w in keyword_set:
					for item in keyword_set[w].items():
						if item[0] in IDS:
							IDS[item[0]]+= item[1]
						else:
							IDS[item[0]] = item[1]
				else:
					# find synonyms to make sure the word in the table
					syn_list = kg.synonyms(w)
					for syn in syn_list:
						if syn in keyword_set:
							for item in keyword_set[syn].items():
								if item[0] in IDS:
									IDS[item[0]]+= item[1]
								else:
									IDS[item[0]] = item[1]
			
			#sort the dataset by the mathching level
			IDS = dict(sorted(IDS.items(), key=lambda x:x[1], reverse=True))
			data = Dataset.objects.filter(id__in=list(IDS.keys()))
			if search2 != '' :
				data = search(search2,data)
			cache.set(str(ip)+"_data", data)

		elif search2 != '' and search1 == ''and data != None:
			data =search(search2,domain_data)
			cache.set(str(ip)+"_data", data)

		#print(type(data))
		"""if data != None:
									if f_s != '':
										data = data.filter(file_size__gt = f_s)
									if n_r != '':
										data = data.filter(total_records__gt = n_r)
									if n_c != '':
										data = data.filter(total_columns__gt = n_c)
									context["metadata"]=data"""




	names = Domain.objects.values_list('name')
	domains = []
	for name in names:
		domains.append(name[0])
	template = loader.get_template('first.html')

	"""
	# add the drop down values
	"""
	context["domains"]=domains

	if domain == None or domain == '':
		context["chosen_domain"] ="Select domain..."
	else:
		context["chosen_domain"] = domain


	if data != None:
		context["metadata"]=data

	template = loader.get_template('first.html')
	return HttpResponse(template.render(context, request))


def detail(request,ID):
	context ={}
	data = Dataset.objects.filter(id = ID)
	context["column"] = {}
	for d in data:
		column_summary = d.column_summary
		context["file_size"] = d.file_size / 1024
		sample = (d.sample)[(list(d.sample))[0]]

	# add sample value to the column variable
	for col,infor in column_summary.items():
		context["column"][col] = [sample[col],infor[6],infor[3]]
	context["metadata"]=data
	
	template = loader.get_template('dataList.html')
	return HttpResponse(template.render(context,request))

def download(request,ID):
	data = Dataset.objects.filter(id = ID)
	for d in data:
		sample = d.sample
	path = "/home/csimage/git/DataMarket/dataMarket/users/sample/"+d.title+"_"+str(d.id)+"_sample.csv"
	print(path)
	print(type(sample))
	json_list = list(sample.values())

	with open(path, 'w', encoding='UTF8') as f:
		header = list(json_list[0].keys())
		writer = csv.writer(f)
		writer.writerow(header)
		for d in json_list:
			writer.writerow(list(d.values()))
	try:
		response = StreamingHttpResponse(open(path, 'rb'))
		response['content_type'] = "application/octet-stream"
		response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
		return response
	except Exception as e:
		print(e)
		raise Http404

def add_cart(request,ID):
	#global cart_list
	ip = get_ip(request)
	cart_list = cache.get(ip)
	if cart_list is None:
		cart_list = {}

	selected_options = request.POST.getlist('checkbox',[])

	if selected_options == []:
		messages.warning(request, "the column choice can't be empty")
		return redirect(request.META.get('HTTP_REFERER', '/detail/{ID}/'))

	cart_list[ID]= selected_options

	print(cart_list)

	cache.set(ip,cart_list ,3600)

	return redirect("http://127.0.0.1:8000/users")

def shop_cart(request):
	ip = get_ip(request)
	cart_list = cache.get(ip)
	if cart_list == None:
		cart_list = {}

	cache_cart = cache.get(str(ip)+"_cart")
	if cache_cart == None:
		cache_cart = {}

	cart_shop = {}
	if request.method == 'POST':
		for key,value in cart_list.items():
			col_chosen = request.POST.getlist('checkbox_'+key,'')
			if col_chosen != None:
				if key in cache_cart:
					cache_cart[key].extend(set(col_chosen)-set(cache_cart[key]))
				else:
					cache_cart[key] = col_chosen
				#cart_shop[data] = ', '.join(cache_cart[key])

	for key,value in cache_cart.items():
		data = Dataset.objects.get(id = key)
		cart_shop[data] = ', '.join(cache_cart[key])
	
	context = {}
	context["cart"] = cart_shop
	cache.set(str(ip)+"_cart",cache_cart)
	template = loader.get_template('shop_cart.html')

	return HttpResponse(template.render(context,request))


# ---------------------------------------------
# ------------------ Data Quality Formua ------------------
# ---------------------------------------------
def formula(request):
	context ={}
	context["choices"]= [0,10,20,30,40,50,60,70,80,90,100]
	#context["col"] = col
	#get random example of the column
	"""data = Dataset.objects.get(id = ID)
	sample = data.sample
	sample_list = list(data.sample)
	row = (data.sample)[sample_list[random.randint(0,len(sample_list)-1)]]
	context["sample"] = row[col]
	template = loader.get_template('formula.html')
	context["data"] = data.title"""
	if request.method == 'POST':
		complet_rate = request.POST.get('c_c','')
		complet_rate = float(complet_rate) if len(complet_rate) != 0 else 0

		complet_weight =  request.POST.get('c_c_w','')
		complet_weight = int(complet_weight) if len(complet_weight) != 0 else 0

		uniqueness_rate = request.POST.get('u','')
		uniqueness_rate = float(uniqueness_rate) if len(uniqueness_rate) != 0 else 0

		uniqueness_weight = request.POST.get('u_w','')
		uniqueness_weight = int(uniqueness_weight) if len(uniqueness_weight) != 0 else 0

		consistency_rate = request.POST.get('c_con','')
		consistency_rate = float(consistency_rate) if len(consistency_rate) != 0 else 0

		consistency_weight = request.POST.get('c_con_w','')
		consistency_weight = int(consistency_weight) if len(consistency_weight) != 0 else 0

		if complet_weight+uniqueness_weight+consistency_weight != 100 :
			messages.warning(request, "The sum of weight must be equal to 100. Please write again ")
			return redirect(request.META.get('HTTP_REFERER', '..'))

		"""
		# store the formula parameter to the cache
		# eg. ip_quality:{"Completeness":[complet_rate,complet_weight]}
		"""
		ip = get_ip(request)
		ip_quality = ip+"_quality"
		quality_list = cache.get(ip_quality)
		if quality_list is None:
			quality_list = {}
		quality_list["Completeness"] = [complet_rate,complet_weight]
		quality_list["Uniqueness"] = [uniqueness_rate,uniqueness_weight]
		quality_list["Consistency"] = [consistency_rate,consistency_weight]
		cache.set(ip_quality,quality_list ,3600)
		print(quality_list)
		return redirect(data_quality)


	template = loader.get_template('formula.html')
	return HttpResponse(template.render(context,request))


def data_quality(request):
	#print("in")
	context={}
	ip = get_ip(request)
	cart_list = cache.get(ip)
	if cart_list is None:
		cart_list = {}
	cart={}


	"""
	# data is the dataset model object and value is the column that customer choosen
	"""

	for key,value in cart_list.items():
		data = Dataset.objects.get(id = key)
		cart[data] = value
	context["cart"] =cart


	"""
	# From cache, to get data quality 
	"""
	ip_quality = ip+"_quality"
	quality_list = cache.get(ip_quality)
	if quality_list == None:
		return redirect("formula")


	"""
	# From cache, to get column quality formula
	"""
	column_form = cache.get(ip+"_column_Quality")


	quality_dic = {}
	for key,value in cart_list.items():
		data = Dataset.objects.get(id = key)
		summary = data.column_summary
		quality_dic[int(key)] = {}

		for col in value:
			"""
			# calculate the completness
			"""
			completness = ((data.total_records -summary[col][6])/data.total_records)*100
			#print("completness:"+str(completness))

			if completness >= quality_list["Completeness"][0]:
				complet_point = 1
			else:
				complet_point = 0
			"""
			# calculate the Uniqueness
			"""
			uniqueness = (data.unique_num/data.total_records)*100
			#print("uniqueness:"+str(uniqueness))

			if uniqueness >= quality_list["Uniqueness"][0]:
				unique_point = 1
			else:
				unique_point = 0
			"""
			# calculate the Consistency
			# max number of cell which has the same format / total number of cell in the column
			"""

			consistency = (summary[col][7]/data.total_records)*100
			if consistency >= quality_list["Consistency"][0]:
				consist_point = 1
			else:
				consist_point = 0

			"""
			# Check whether define the column quality, if yes, add column accuarcy in the quality formula
			"""
			if column_form is not None and key in column_form and col in column_form[key]:
				col_list = column_form[key][col]
				accuracy = (col_list['Accuracy'][2]/data.total_records)*100
				print("accuracy:"+ str(accuracy))
				if accuracy >= col_list['Accuracy'][0]:
					acc_point = 1
				else:
					acc_point = 0

				quality_dic[int(key)][col]= complet_point*col_list["Completeness"][0]+ \
				unique_point*col_list["Uniqueness"][0]+consist_point* col_list["Consistency"][0]+\
				acc_point*col_list["Accuracy"][1]
				continue


			quality_dic[int(key)][col]= complet_point*quality_list["Completeness"][1]+ \
			unique_point*quality_list["Uniqueness"][1]+consist_point* quality_list["Consistency"][1]
			#print(quality_dic[int(key)][col])

	context["quality"] =quality_dic #{ID:{col:data_quality}}

	quality_sum={}
	for ID,col_quality in quality_dic.items():
		quality_sum[ID] = 0
		for col, c_quality in col_quality.items():
			quality_sum[ID]+= c_quality*(1/len(col_quality))
		quality_sum[ID] = round(quality_sum[ID])

	context["quality_sum"] = quality_sum

	template = loader.get_template('data_quality.html')
	return HttpResponse(template.render(context,request))

def column_quality(request,ID,col):
	data = Dataset.objects.get(id = ID)
	context ={}
	context['data'] = data
	context['column'] = col
	sample = data.sample
	sample_list = list(data.sample)
	row = (data.sample)[sample_list[random.randint(0,len(sample_list)-1)]]
	context["sample"] = row[col]
	context["types"] = ["Date","Age","Other","Country"]
	context["choices"]= [0,10,20,30,40,50,60,70,80,90,100]

	ip = get_ip(request)
	ip_quality = ip+"_quality"
	quality_list = cache.get(ip_quality)
	if quality_list == None:
		return redirect("formula")
	context['complet'] = quality_list["Completeness"][0]
	context['uniqueness'] = quality_list["Uniqueness"][0]
	context['consist'] = quality_list["Consistency"][0]
	template = loader.get_template('column_quality.html')
	return HttpResponse(template.render(context,request))

def column_add(request,ID,col):
	ip = get_ip(request)
	ip_quality = ip+"_quality"
	quality_list = cache.get(ip_quality)
	if quality_list == None:
		return redirect("formula")

	complet_weight =  request.POST.get('c_c_w','')
	complet_weight = int(complet_weight) if len(complet_weight) != 0 else 0

	uniqueness_weight = request.POST.get('u_w','')
	uniqueness_weight = int(uniqueness_weight) if len(uniqueness_weight) != 0 else 0

	consistency_weight = request.POST.get('c_con_w','')
	consistency_weight = int(consistency_weight) if len(consistency_weight) != 0 else 0

	accuracy_rate = request.POST.get('c_a','')
	accuracy_rate = float(accuracy_rate) if len(accuracy_rate) != 0 else 0

	accuracy_weight = request.POST.get('c_a_w','')
	accuracy_weight = float(accuracy_weight) if len(accuracy_weight) != 0 else 0


	if complet_weight+uniqueness_weight+consistency_weight+accuracy_weight != 100 :
		messages.warning(request, "The sum of weight must be equal to 100. Please write again ")
		return redirect(request.META.get('HTTP_REFERER', '..'))

	column_type = request.POST.get('column_type','')
	data = Dataset.objects.get(id = ID)
	df = pd.read_csv(data.host_link,encoding = 'ISO-8859-1')
	column = df[col].tolist()
	num_accuracy = 0
	if column_type == 'Date':
		for c in column:
			try:
				date = parser.parse(c)
				if date <  datetime.now():
					num_accuracy +=1
			except Exception as e:
				#print(e)
				continue
	elif column_type == 'Age':
		for c in column:
			if not isinstance(c,str):
				c = str(c)
			numbers_list = re.findall(r'\d+', c)
			if len(numbers_list) == 0:
				continue
			elif len(numbers_list) == 1 and 0<= float(numbers_list[0]) < 120:
				num_accuracy +=1
			elif len(numbers_list) == 2 and 0<= float(numbers_list[0]) < 120 and \
				0 <= float(numbers_list[1]) < 120 and float(numbers_list[1]) > float(numbers_list[0]):
				num_accuracy +=1
	elif column_type == 'Country':
		for c in column:
			if is_valid_country_name(c):
				num_accuracy +=1




	if num_accuracy > 0:
		#Check whether cache store the column quality formula
		column_acc = cache.get(ip+"_column_Quality")
		if column_acc == None:
			column_acc = {}

		if ID in column_acc:
			column_acc[ID][col]={"Accuracy":[accuracy_rate,accuracy_weight,num_accuracy],
								"Completeness":[complet_weight],
								"Uniqueness":[uniqueness_weight],
								"Consistency":[consistency_weight]}
		else:
			column_acc[ID]={col:{"Accuracy":[accuracy_rate,accuracy_weight,num_accuracy],
								"Completeness":[complet_weight],
								"Uniqueness":[uniqueness_weight],
								"Consistency":[consistency_weight]}}

		cache.set(ip+"_column_Quality",column_acc)

	return redirect(data_quality)  

