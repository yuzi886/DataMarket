from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Dataset,Domain
from django.urls import reverse
from datetime import datetime 
import operator
from . import Keyword_Generation as kg


data = None
keyword_set = {}
IDS = {} #store matching level between searching word and all dataset
def index(request):
	global data,keyword_set,IDS
	context ={}
	if request.method == 'POST':
		domain = request.POST.get('domain','')
		sort = request.POST.get('sort','')
		search = request.POST.get('search','')
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
				data = sorted(data, key=operator.attrgetter('user_id'))
				#do not do sort by username(because l do not add user name)
			context["metadata"]=data
		elif search != ''and data != None:#use keyword to search data
			if len(keyword_set) == 0:
				dataset = Dataset.objects.all()
				for d in dataset:
					sentence = ''
					#do not add seller name in sentence, because not store user name
					sentence = sentence + d.title+" "+d.description+" "
					keywords = kg.extact(sentence)
					for k in keywords:
						if k in keyword_set:
							keyword_set[k].append(d.id)
						else:
							keyword_set[k] = [d.id]
					IDS[d.id] = 0
				print(keyword_set)

			search_word_set = kg.extact(search)
			for w in search_word_set:
				if w in keyword_set:
					for i in keyword_set[w]:
						IDS[i]+=1
			print(IDS)
			IDS = sorted(IDS,reverse=True)
			print(IDS)
			data = sorted(data, key=lambda x: IDS.index(x.id))
			context["metadata"]=data



	names = Domain.objects.values_list('name')
	domains = []
	for name in names:
		domains.append(name[0])
	template = loader.get_template('first.html')
	context["domains"]=domains
	template = loader.get_template('first.html')
	return HttpResponse(template.render(context, request))
