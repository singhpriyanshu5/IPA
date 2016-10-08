from __future__ import unicode_literals
from rest_framework.renderers import BrowsableAPIRenderer, AdminRenderer

class BrowsableAPIInterviewerRenderer(BrowsableAPIRenderer):
    template = 'rest_framework/api_interviewer.html'

class BrowsableAPIRendererIntervieweeRegister(BrowsableAPIRenderer):
    template = 'rest_framework/api_register.html'

class BrowsableAPIRendererInterviewRegister(AdminRenderer):
    template = 'rest_framework/api_interview_register.html'

class AdminJudgeRenderer(AdminRenderer):
    template = 'rest_framework/admin_judge.html'

class AdminResultRenderer(AdminRenderer):
    template = 'rest_framework/admin_result.html'

class AdminHomeRenderer(AdminRenderer):
    template = 'rest_framework/admin_home.html'

class AdminInterviewerRenderer(AdminRenderer):
    template = 'rest_framework/admin_interviewer.html'