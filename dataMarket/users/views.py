from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Dataset
from django.urls import reverse
from datetime import datetime 
def index(request):
	template = loader.get_template('first.html')
	return HttpResponse(template.render())
# Create your views here.

def seller(request):
	template = loader.get_template('seller.html')
	return HttpResponse(template.render({}, request))

def addData(request):# basic one
	Title = request.POST['title']
	File_name = request.POST['file_name']
	License = request.POST['license']
	Published_by = request.POST['published_by']
	Last_update_date = request.POST['last_update_date']
	Price = request.POST['price']
	Description = request.POST['description']
	#File_path = request.POST['file_path']
	#do not add data input
	
	
	data = Dataset(title = Title,dataset_file_name = File_name,
		price = Price,pub_by = Published_by,timeliness = 0,
		License = License,description = Description,pub_date = datetime.now(),sample = {
    'default': {
        'default': 'null',
        }},column_summary = {
    'default': {
        'default': 'null',
        }})
	data.save()
	"""except:
					print("has error")"""
	return HttpResponseRedirect(reverse('seller'))


	