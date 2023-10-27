import django
from django.conf.urls import url

from ho600_ajax import views as ho600_ajax_views

urlpatterns = [
    url(r'^helper/(?P<module>[^/]*)/?$', ho600_ajax_views.helper, name='helper'),
    url(r'^$', ho600_ajax_views.callback, name='callback'),
]
