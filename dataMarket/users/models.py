#from django.contrib.auth import get_user_model
from django.db import models
import datetime
from django.utils import timezone


class TimeStamps():
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now = True)
	"""created_at = models.DateTimeField(auto_now_add=True,)
				updated_at = models.DateTimeField(auto_now=True,)"""

"""Dataset Domain Model"""
class Domain(models.Model, TimeStamps):
	id = models.AutoField(primary_key=True,)
	name = models.CharField(
		max_length=100,
		blank=False,
		unique=True,
	)
	def __str__(self) -> str:
		return self.name

class Sub_Domain(models.Model, TimeStamps):
#Dataset Sub Domain Model
	id = models.AutoField(primary_key=True)
	name = models.CharField(
		max_length=100,
		blank=False,
		unique=True,
	)
	domain = models.ForeignKey(
		Domain,
		models.SET_NULL,
		blank=True,
		null=True,
	)
	def __str__(self) -> str:
		return self.name

class Task(models.Model, TimeStamps):
#Buyer purpose of buying dataset Model
	id = models.AutoField(primary_key=True)
	name = models.CharField(
		max_length=100,
		blank=False,
		unique=True,
	)
	def __str__(self) -> str:
		return self.name

class Dataset(models.Model, TimeStamps):
#Dataset Model
	id = models.AutoField(primary_key=True,)
	"""user = models.ForeignKey(
				get_user_model(),
					on_delete=models.CASCADE,
					unique=False,
					default=1
				)"""
	user_id  = models.CharField(
		max_length=100,
		unique=False,
		default=1
	)
	title = models.CharField(
		max_length=100,
		blank=False,
	)
	description = models.TextField(
		blank=True,
		default='',
	)
	dataset_file_name = models.CharField(
		max_length=100,
		blank=False,
		db_index=True,
		unique=True,
	)
	host_link = models.FilePathField (
		blank=True,
	)
	price = models.DecimalField(
		max_digits=8, 
		decimal_places=2,
		blank=True,
		default=0.0,
	)
	domain = models.ForeignKey(
		Domain,
		models.SET_NULL,
		blank=True,
		null=True,
	)
	pub_date = models.DateTimeField('date published')
	pub_by = models.CharField(
		max_length=200,
		blank=False,
		default='Owner',
	)
	License = models.CharField(
		max_length=200,
		blank=False,
		default='Open source',
	)
	total_records = models.IntegerField(
		blank=True,
		default=0,
	)
	total_columns = models.IntegerField(
		blank=True,
		default=0,
	)
	file_size = models.DecimalField(
		max_digits=8, 
		decimal_places=2,
		blank=True,
		default=0.0,
	)
	total_columns = models.IntegerField(
		blank=True,
		default=0,
	)
	completeness = models.DecimalField(
		max_digits=3, 
		decimal_places=3,
		blank=True,
		default=0.0,
	)
	timeliness = models.CharField(
		max_length=200,
		blank=False,
	)
	sample = models.JSONField(
		blank=True,
	)
	column_summary = models.JSONField(
		blank=True,
	)

	def was_published_recently(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

	def __str__(self) -> str:
		return self.title
#return self.title + ' ... ' + str(self.pub_date)


