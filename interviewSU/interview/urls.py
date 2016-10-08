from django.conf.urls import include, url
from django.contrib import admin
from website.views import *
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register(r'register', InterviewRegisterViewSet, base_name='register')
router.register(r'user', IntervieweeViewSet, base_name='user')
router.register(r'admin', InterviewAdminViewSet, base_name='admin')
router.register(r'judge', InterviewAdminJudgeViewSet, base_name='judge')
router.register(r'result', InterviewResultSet, base_name='result')

router.register(r'choosegroup', InterviewGroupChooseSet, base_name='result')

urlpatterns = [
    url(r'^admins/', admin.site.urls),
    url(r'^$', Home.as_view({'get': 'list'})),
    url(r'request/(?P<group>\w+)/$', requestdata, name='request board'),
    url(r'^queueboard/(?P<group>\w+)/$', queueboard, name='queue board'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + router.urls