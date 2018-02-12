from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from serveradmin.changes.models import Commit, Addition, Modification, Deletion
from serveradmin.serverdb.query_committer import CommitError, QueryCommitter


@login_required
def commits(request):
    commits = Commit.objects.order_by('-change_on').prefetch_related()
    paginator = Paginator(commits, 100)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)

    return TemplateResponse(request, 'changes/commits.html', {
        'commits': page
    })


@login_required
def history(request):
    server_id = request.GET.get('server_id')
    if not server_id:
        raise Http404

    try:
        commit_id = int(request.GET['commit'])
    except (KeyError, ValueError):
        commit_id = None

    adds = Addition.objects.filter(server_id=server_id).select_related()
    updates = Modification.objects.filter(server_id=server_id).select_related()
    deletes = Deletion.objects.filter(server_id=server_id).select_related()

    if commit_id:
        adds = adds.filter(commit__pk=commit_id)
        updates = updates.filter(commit__pk=commit_id)
        deletes = deletes.filter(commit__pk=commit_id)

    change_list = ([('add', obj) for obj in adds] +
                   [('update', obj) for obj in updates] +
                   [('delete', obj) for obj in deletes])
    change_list.sort(key=lambda entry: entry[1].commit.change_on, reverse=True)

    for change in change_list:
        commit = change[1].commit
        if commit.user:
            commit.commit_by = commit.user.get_full_name()
        elif commit.app:
            commit.commit_by = commit.app.name
        else:
            commit.commit_by = 'unknown'

    return TemplateResponse(request, 'changes/history.html', {
        'change_list': change_list,
        'commit_id': commit_id,
        'server_id': server_id,
        'is_ajax': request.is_ajax(),
        'base_template': 'empty.html' if request.is_ajax() else 'base.html',
        'link': request.get_full_path()
    })


@login_required
def restore_deleted(request, change_commit):
    deleted = get_object_or_404(
        Deletion,
        server_id=request.POST.get('server_id'),
        commit__pk=change_commit,
    )

    server_obj = deleted.attributes
    try:
        QueryCommitter([server_obj], user=request.user)()
    except CommitError as error:
        messages.error(request, str(error))
    else:
        messages.success(request, 'Server restored.')

    return redirect(
        reverse('changes_history') +
        '?server_id=' + str(server_obj['object_id'])
    )