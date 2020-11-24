from django import template
import re
import os

register = template.Library()

@register.filter(name='remove_leading_numbers_str')
def remove_leading_numbers_str(value):

	value = re.sub("^\d+(?:\.\d*)*", '', value).strip().lower()

	return value


@register.filter(name='remove_leading_numbers_list')
def remove_leading_numbers_list(list_items):

	list_items = list(map(lambda x: re.sub("^\d+(?:\.\d*)*", '', x).strip().lower(), list_items))

	return list_items

@register.filter(name='get_file_name')
def get_file_name(file_obj):

	return os.path.basename(file_obj.file.name)

@register.filter(name='convert_to_str')
def convert_to_str(value):
	return str(value)

@register.filter(name='convert_to_list')
def convert_to_list(string):
	list_items = list(re.split(" |,", string))
	return list_items

@register.filter(name='find_type')
def find_type(obj):
	return type(obj)

@register.filter(name='capitalize_sentence')
def capitalize_sentence(sentence):
	return sentence.capitalize()

@register.filter(name='get_item')
def get_item(dictionary, key):
	return dictionary.get(key)
