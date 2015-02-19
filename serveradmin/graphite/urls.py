from django.conf.urls import patterns, url

urlpatterns = patterns(
    'serveradmin.graphite.views',
    url(r'^$', 'index', name='graphite_index'),
    url(r'^graph_table/(.+)$', 'graph_table', name='graphite_graph_table'),
    url(r'^graph_popup$', 'graph_popup', name='graphite_graph_popup'),
)