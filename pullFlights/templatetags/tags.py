from django import template

register = template.Library()


# Ended up not using them, but it is an extremely useful functionality of django
@register.filter
def return_item_name(l, i):
    try:
        return l[i]['name']
    except:
        return None

@register.filter
def return_item_country(l, i):
    try:
        return l[i]['country']
    except:
        return None

@register.filter
def return_item_code(l, i):
    try:
        return l[i]['code']
    except:
        return None

@register.filter
def return_number(s):
    try:
        return int(s)
    except:
        return None