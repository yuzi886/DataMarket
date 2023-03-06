from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    if dictionary == None:
        return "undefined"
    if dictionary.get(key) == 0:
        return 0
    return dictionary.get(key)

@register.filter
def length(dictionary):
    return len(dictionary)+3

