import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from repo.utils import get_repo_title
from .pipeparser import PipeParser


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    project_info = get_repo_title(user, project)

    return render(request, 'jenkins/jenkins_file.html', {'info': project_info})


@csrf_exempt
def post_jenkinsfile_api(request):
    # valid ajax request
    if not request.is_ajax() or request.method != 'POST':
        return HttpResponseBadRequest('error request type, must be ajax by POST method.')
    
    pipe_tree = PipeParser.parse(json.loads(request.body))
    return HttpResponse(pipe_tree.__str__(), headers={
        'Content-Type': 'text/plain',
    })
