from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from typographus import typo


__all__ = ['typograph', ]


@csrf_exempt
def typograph(request):
    text = request.POST.get('text', u'')
    response = HttpResponse(typo(text), mimetype="text/plain")
    response['Cache-Control'] = 'no-cache'
    return response
