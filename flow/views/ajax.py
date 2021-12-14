import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from ..pipeparser import PipeParser


@csrf_exempt
def create_jenkinsfile(request):
    # valid ajax request
    if not request.is_ajax() or request.method != 'POST':
        return HttpResponseBadRequest('error request type, must be ajax by POST method.')

    pipe_tree = PipeParser.parse(json.loads(request.body))
    return HttpResponse(pipe_tree.__str__(), headers={
        'Content-Type': 'text/plain',
    })
