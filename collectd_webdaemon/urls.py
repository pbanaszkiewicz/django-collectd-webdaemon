# coding: utf-8

from django.conf.urls import patterns, url

# metrics
urlpatterns = patterns('collectd_webdaemon.views',
    # it reacts for POST with a list of metrics to obtain
    # useful in Overview page
    url(r'^metrics$', 'arbitrary_metrics', name='arbitrary_metrics'),

    # obtains main (CPU/memory/net/disk) statistics from a given host (not doing
    # anything for subhosts, like VMs in a node, in terms of Ganeti)
    url(r'^metrics/(?P<host>\w+)/general$', 'arbitrary_metrics', name='arbitrary_metrics'),

    # obtains all the metrics names so the user can choose ones that he/she wants
    # to have displayed either on overview page or right away
    url(r'^get_all_names$', 'get_all_names', name='get_all_names'),
)


# thresholds
urlpatterns += patterns('collectd_webdaemon.views',
    # typical CRUD
    url(r'^threshold$', 'threshold', name='threshold'),

    # get similar
    url(r'^threshold/similar$', 'similar_thresholds', name='similar_thresholds'),

    # update collectd configuration (integrate with JOBs? Nah, I dunno)
    url(r'^threshold/update_configuration', 'update_configuration', name='update_configuration')
)

# alerts
#urlpatterns += patterns('collectd_webdaemon.views',
#    url(r'', '', ''),
#)
