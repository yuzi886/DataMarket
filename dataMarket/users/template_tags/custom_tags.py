from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    if dictionary == None:
        return "undefined"
    if dictionary.get(key) == 0:
        return 0
    return dictionary.get(key)

@register.filter
def get_item_2d(dictionary, keys):
    row_key, col_key = keys.split(",")
    row = dictionary.get(row_key, {})
    return row.get(col_key, "")

