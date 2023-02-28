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

data = None
#keyword_set = {}
keyword__domain = {}
#IDS = {} #store matching level between searching word and all dataset
domain =""
cart_list = []

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

def search(kw):
	global data
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


def index(request):
	global data,domain,keyword__domain
	context ={}
	if request.method == 'POST':
		domain = request.POST.get('domain','')
		sort = request.POST.get('sort','')
		search1 = request.POST.get('search1','')
		search2 = request.POST.get('search2','')
		"""f_s = request.POST.get('f_s','')
								n_r = request.POST.get('n_r','')
								n_c = request.POST.get('n_c','')"""
		if domain != '':#for get all domain name 
			domain_id = Domain.objects.filter(name=domain).values()
			data = Dataset.objects.filter(domain_id = domain_id[0]['id'])
			context["metadata"]=data
		elif sort != '' and data != None:# sort the data 
			if sort == 'price_l_h' :
				data = sorted(data, key=operator.attrgetter('price'))
			elif sort == 'price_h_l':
				data = sorted(data, key=operator.attrgetter('price'),reverse=True)
			else:
				data = sorted(data, key=operator.attrgetter('pub_by'))
				#do not do sort by username(because l do not add user name)
			context["metadata"]=data
		elif search1 != ''and data != None:
			#seach algorithms 
			#if domain not in keyword__domain: 
			keyword_set = {}
			for d in data:
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
				search(search2)
			context["metadata"]=data

		elif search2 != '' and search1 == ''and data != None:
			search(search2)
			context["metadata"]=data

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
	context["domains"]=domains
	template = loader.get_template('first.html')
	#cache.set('guest', '1',3600)
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
	global cart_list
	context ={}
	data_list =[]
	template = loader.get_template('shop_cart.html')
	return HttpResponse(template.render(context,request))

def formula(request,ID,col):
	context ={}
	context["choices"]= [0,10,20,30,40,50,60,70,80,90,100]
	context["col"] = col
	#get random example of the column
	data = Dataset.objects.get(id = ID)
	sample = data.sample
	sample_list = list(data.sample)
	row = (data.sample)[sample_list[random.randint(0,len(sample_list)-1)]]
	context["sample"] = row[col]
	template = loader.get_template('formula.html')
	context["data"] = data.title
	return HttpResponse(template.render(context,request))

def formula_add(request,ID,col):
	complet_rate = request.POST.get('c_c','')
	complet_rate = float(complet_rate) if len(complet_rate) != 0 else 0

	complet_weight =  request.POST.get('c_c_w','')
	complet_weight = int(complet_weight) if len(complet_weight) != 0 else 0

	"""expire_time = request.POST.get('e_t','')
				if len(expire_time) == 0 :
					messages.warning(request, "the expire_time should not be empty")
					return redirect(request.META.get('HTTP_REFERER', '..'))
				e_t = datetime.strptime(expire_time, '%Y-%m-%d')
				t_zone = pytz.utc
				expire_time = t_zone.localize(e_t)"""

	volatility_y = request.POST.get('v_y','')
	volatility_y = int(volatility_y) if len(volatility_y) != 0 else 0
	volatility_m = request.POST.get('v_m','')
	volatility_m = int(volatility_m) if len(volatility_m) != 0 else 0
	volatility_d = request.POST.get('v_d','')
	volatility_d = int(volatility_d) if len(volatility_d) != 0 else 0
	volatility_h = request.POST.get('v_','')
	volatility_h = int(volatility_h) if len(volatility_h) != 0 else 0
	expiry_time = timedelta(days=volatility_d+ 30*volatility_m+ 365*volatility_y+ volatility_h/24)
	sample_format = request.POST.get('c_d_f','')

	fresh_rate = request.POST.get('f_p','')
	fresh_rate = float(fresh_rate) if len(fresh_rate) != 0 else 0

	fresh_weight = request.POST.get('f_w','')
	fresh_weight = int(fresh_weight) if len(fresh_weight) != 0 else 0

	accuracy_condition = request.POST.get('a_condition','')
	accuracy_input = request.POST.get('a_text','')
	accuracy_rate =request.POST.get('a_p','')
	accuracy_rate = float(accuracy_rate) if len(accuracy_rate) != 0 else 0

	accuracy_weight =request.POST.get('a_w','')
	accuracy_weight = int(accuracy_weight) if len(accuracy_weight) != 0 else 0

	unique_condition = request.POST.get('u_condition','')

	unique_input = request.POST.get('u_text','')
	unique_input = int(unique_input) if len(unique_input) != 0 else 0


	unique_weight= request.POST.get('u_w','')
	unique_weight = int(unique_weight) if len(unique_weight) != 0 else 0

	data = Dataset.objects.get(id = ID)
	"""
	col_detail contain [mean(index=0),min(index=1),max(index=2),distict(index=3), 
						std(index=4),type(index=5),missing_num(index=6)]
	"""
	col_detail = (data.column_summary)[col] 

	if complet_weight+fresh_weight+accuracy_weight+unique_weight != 100 :
		messages.warning(request, "The sum of weight must be equal to 100. Please write again ")
		return redirect(request.META.get('HTTP_REFERER', '..'))
	
	"""
	This formula is for the completness point of the column
	"""

	completness = ((data.total_records -col_detail[6])/data.total_records)*100
	if completness >= complet_rate and complet_weight != 0:
		complet_point = 1
	else:
		complet_point = 0

	"""
	This formula is for the freshness point of the column
	"""
	#print((data.updated_at).tzinfo) 
	Age = (timezone.now() - data.pub_date )
	Currency = timezone.now() - data.updated_at
	Volatility = timezone.now() - data.updated_at + expiry_time
	Timeliness = max(1- Currency/Volatility,0)*100
	print("Timeliness:"+str(Timeliness))
	if Timeliness >fresh_rate and fresh_weight != 0:
		time_point =1
	else:
		time_point =0


	"""
	This formula is for the accuracy point of the column
	"""


	num_fit = 0
	accuracy_point = 0
	if accuracy_condition == 'contain':
		with open(data.host_link, 'r') as csvfile:
			csvreader = csv.reader(csvfile)
			column_names = next(csvreader)
			index = column_names.index(col)
			for row in csvreader:
				if accuracy_input in row[index]:
					num_fit+=1
	elif accuracy_condition == 'n_contain':
		with open(data.host_link, 'r') as csvfile:
			csvreader = csv.reader(csvfile)
			column_names = next(csvreader)
			index = column_names.index(col)
			for row in csvreader:
				if accuracy_input not in row[index]:
					num_fit+=1
	elif accuracy_condition == 'less':
		if isNumeric(accuracy_input):
			float(accuracy_input)
			with open(data.host_link, 'r') as csvfile:
				csvreader = csv.reader(csvfile)
				column_names = next(csvreader)
				index = column_names.index(col)
				for row in csvreader:
					if isNumeric(row[index]) and row[index] < accuracy_input:
						num_fit+=1
		else:
			messages.warning(request, "when condition is less, the input must be number. Please write again ")
			redirect(request.META.get('HTTP_REFERER', '..'))

	elif accuracy_condition == 'higher':
		if isNumeric(accuracy_input):
			float(accuracy_input)
			with open(data.host_link, 'r') as csvfile:
			# Create a reader object
				csvreader = csv.reader(csvfile)
			# Get the column names
				column_names = next(csvreader)
				index = column_names.index(col)
			# Read each row in the file
				for row in csvreader:
			# Print the first column of each row
					if isNumeric(row[index]) and float(row[index]) > accuracy_input:
						num_fit+=1
		else:
			messages.warning(request, "when condition is higher, the input must be number. Please write again ")
			redirect(request.META.get('HTTP_REFERER', '..'))
	else:
		accuracy_point = 1
	"""elif accuracy_condition == 'later':
					if isDate(accuracy_input):
						accuracy_input = datetime.strptime(accuracy_input, '%Y/%m/%d')
						with open(data.host_link, 'r') as csvfile:
						# Create a reader object
							csvreader = csv.reader(csvfile)
						# Get the column names
							column_names = next(csvreader)
							index = column_names.index(col)
							for row in csvreader:
								if row[index] > accuracy_input :
									num_fit+=1
					else:
						messages.warning(request, "when condition is later, the input must fit data format. Detail show in \
						 input format button. Please write again ")
						redirect(request.META.get('HTTP_REFERER', '..'))
				elif accuracy_condition == 'before':
					if isDate(accuracy_input):
						accuracy_input = datetime.strptime(accuracy_input, '%Y/%m/%d')
						with open(data.host_link, 'r') as csvfile:
						# Create a reader object
							csvreader = csv.reader(csvfile)
						# Get the column names
							column_names = next(csvreader)
							index = column_names.index(col)
							for row in csvreader:
								if row[index] < accuracy_input :
									num_fit+=1
					else:
						messages.warning(request, "when condition is later, the input must fit data format. Detail show in \
						 input format button. Please write again ")
						redirect(request.META.get('HTTP_REFERER', '..'))"""
	
	if (num_fit/ data.total_records)> accuracy_rate and accuracy_weight != 0:
		accuracy_point = 1

	"""
	This formula is for the Uniqueness point of the column
	"""
	if unique_weight != 0:
		if unique_condition == 'bigger':
			if unique_input >col_detail[3]: 
				unique_point = 1
			else:
				unique_point = 0
		elif unique_condition == 'smaller':
			if unique_input <col_detail[3]: 
				unique_point = 1
			else:
				unique_point = 0
		else:
			if unique_input == col_detail[3]: 
				unique_point = 1
			else:
				unique_point = 0
	else:
		unique_point = 0
	print("Uniqueness:"+str(unique_point))
	
	"""
	# when the character is satisfied, final quality += (weight of character/100)
	"""
	quality = (unique_point*(unique_weight/100) + accuracy_point*(accuracy_weight/100)+fresh_weight*(time_point/100)+\
	complet_point*(complet_weight/100))*100
	print("quality: "+str(quality))
	"""
	# store the data quality to the quality_list(stored in cache)
	# quality_list = {ID:{col:quality}}
	"""
	ip = get_ip(request)
	ip_quality = ip+"_quality"
	quality_list = cache.get(ip_quality)
	if quality_list is None:
		quality_list = {}
	ID = int(ID)
	if ID in quality_list:
		quality_list[(ID)][col] = quality
	else:
		quality_list[ID] = {col:quality}
	cache.set(ip_quality,quality_list ,3600)
	print(quality_list)
	return redirect("../../../")

def data_quality(request):
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
	context["quality"] =quality_list
	print(context["quality"])
	quality_sum={}
	if quality_list == None:
		quality_list = {}
	for ID,col_quality in quality_list.items():
		quality_sum[ID] = 0
		for col, c_quality in col_quality.items():
			quality_sum[ID]+=c_quality*(1/len(col_quality))

	context["quality_sum"] = quality_sum
	template = loader.get_template('data_quality.html')
	return HttpResponse(template.render(context,request))


