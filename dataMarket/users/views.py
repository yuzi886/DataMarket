from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Dataset,Domain
from django.urls import reverse
from datetime import datetime 
import operator
from . import Keyword_Generation as kg
import json
from django.contrib import messages

data = None
#keyword_set = {}
keyword__domain = {}
#IDS = {} #store matching level between searching word and all dataset
domain =""

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
			if domain not in keyword__domain:
				keyword_set = {}
			#if len(keyword_set) == 0:
				#dataset = Dataset.objects.all()
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
				keyword__domain[domain] = keyword_set
				#print(keyword_set)


			# processed input query and displays candidate datasets
			IDS = {}
			keyword_set = keyword__domain[domain]
			search_word_set = kg.extact(search1)
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
			if search2 != '' :
				search(search2)
			context["metadata"]=data
		elif search2 != '' and search1 == '':
			 messages.error(request, 'type in keywords of title, description,seller name firstly') 






	names = Domain.objects.values_list('name')
	domains = []
	for name in names:
		domains.append(name[0])
	template = loader.get_template('first.html')
	context["domains"]=domains
	template = loader.get_template('first.html')
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
	return HttpResponse(template.render(context,request))