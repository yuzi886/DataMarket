from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, StreamingHttpResponse
from django.template import loader
from .models import Dataset,Domain
from django.urls import reverse
from datetime import datetime 
import operator
from . import Keyword_Generation as kg
import json
from django.contrib import messages
import json
import csv
import os
from django.core.cache import cache

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
	for d in data:
		#print(d.column_summary)
		#data_dict = json.loads(d.column_summary)
		context["column"] = d.column_summary

	context["metadata"]=data
	template = loader.get_template('dataList.html')
	print(cache.get('guest'))
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
	"""for key,value in cart_list.items():
					data = Dataset.objects.get(id = key)
					data_list.append({data:values})"""
	template = loader.get_template('shop_cart.html')
	return HttpResponse(template.render(context,request))

def formula(request,ID,col):
	context ={}
	context["choices"]= [1,2,3,4,5,6,7,8,9]
	context["col"] = col

	template = loader.get_template('formula.html')
	return HttpResponse(template.render(context,request))

def formula_add(request,ID,col):
	complet_rate = request.POST.get('c_c','')
	complet_weight =  request.POST.get('c_c_w','')
	expire_time = request.POST.get('e_t','')
	fresh_weight = request.POST.get('f_w','')
	accuracy_condition = request.POST.get('a_condition','')
	accuracy_input = request.POST.get('a_text','')
	accuracy_rate =request.POST.get('a_p','')
	accuracy_weight =request.POST.get('a_w','')
	unique_condition = request.POST.get('u_condition','')
	unique_input = request.POST.get('u_condition','')
	unique_weight= request.POST.get('u_w','')

	#formula = {"Completeness":[complet_rate,complet_weight],"Freshness":[expire_time,fresh_weight],"Accuracy":[]}
	return redirect("../../../")

def data_quality(request):
	context={}
	ip = get_ip(request)
	cart_list = cache.get(ip)
	if cart_list is None:
		cart_list = {}
	cart={}


	for key,value in cart_list.items():
		data = Dataset.objects.get(id = key)
		cart[data] = value
	context["cart"] =cart
	template = loader.get_template('data_quality.html')
	return HttpResponse(template.render(context,request))


