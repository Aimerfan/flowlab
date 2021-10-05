from base64 import b64decode

from django.shortcuts import render
from django.http import JsonResponse

from repo.utils import get_repo_title
from .pipeparser import PipeParser


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    project_info = get_repo_title(user, project)

    if request.method == 'POST':
        print(request.POST.getlist('stage'))
        print(request.POST.getlist('single_sh'))
        print(request.POST.getlist('multi_sh'))
        print(request.POST.getlist('echo'))
        print(request.POST.get('data', ''))
        print(request.POST.get('context', ''))

    return render(request, 'jenkins/jenkins_file.html', {'info': project_info})


def post_jenkinsfile_api(request):

    # valid ajax request
    if not request.is_ajax() or request.method != 'POST':
        return JsonResponse({"error": ""}, status=400)

    post_form_keys = request.POST.keys()
    for key in post_form_keys:
        if key == 'context':
            # decode_context = b64decode(request.POST.getlist(key)[0]).decode('utf-8')
            pipe_tree = PipeParser.parse(request.POST.get('context', None))
            print(pipe_tree.str())
        else:
            print(f'{key}: {request.POST.getlist(key)}')
