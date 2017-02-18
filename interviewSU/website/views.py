from django.shortcuts import render
from rest_framework import viewsets, mixins
from user.serializer import *
from user.permissions import *
from django.http import JsonResponse
from rest_framework.decorators import detail_route, renderer_classes
from rest_framework.response import Response
from rest_framework import status
from .customrenderers import *
from django.http import HttpResponseRedirect


# TODO: remove all magic number

def requestdata(request, group):
    arr = []
    for q in InterviewDepartment.objects.filter(group__name=group):
        arr.append([])
        arr[-1].append(q.name)
        for w in q.interviewRegister.exclude(status=3).order_by('queueNumber'):
            arr[-1].append([w.interviewee.name, w.status])
    return JsonResponse({'data': arr})


def queueboard(request, group):
    return render(request, 'rest_framework/board.html', {'group': group})


@renderer_classes([AdminResultRenderer, ])
class InterviewGroupChooseSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    queryset = InterviewGroup.objects.all()
    serializer_class = InterviewGroupSerializer

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseRedirect('../../queueboard/' + kwargs['pk'])


class Home(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = InterviewHomeSerializer
    renderer_classes = [AdminHomeRenderer, ]

    def get_queryset(self):
        try:
            return self.request.user.interviewee.interviewRegister.exclude(status=3)
        except:
            return []


class InterviewResultSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Interviewee.objects.all().order_by('-countAccepted')
    serializer_class = InterviewResultSerializer
    renderer_classes = [AdminResultRenderer, ]
    permission_classes = (IsBoss,)


class InterviewAdminViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    queryset = InterviewRegister.objects.filter(status=0).order_by('queueNumber')
    serializer_class = InterviewAdminSerializer
    renderer_classes = [AdminInterviewerRenderer, ]
    permission_classes = (IsInterviewer,)

    @detail_route()
    def call(self, request, pk):
        instance = InterviewRegister.objects.get(pk=pk)
        serializer = InterviewAdminSerializer(instance)
        rep = Response(serializer.data)
        rep.data['last_action'] = request.user.interviewer.lastAction
        return rep

    @detail_route()
    def startinterview(self, request, pk):
        instance = InterviewRegister.objects.get(pk=pk)
        if not (
                    instance.status == 1 and request.user.interviewer.status == 1 and request.user.interviewer.statusDesc == instance.pk):
            return HttpResponseRedirect('/admin/')
        instance.status = 2
        instance.save()
        request.user.interviewer.status = 2
        request.user.interviewer.save()
        return HttpResponseRedirect('../interview')

    @detail_route(renderer_classes=[BrowsableAPIInterviewerRenderer], methods=['GET', 'PUT'],
                  serializer_class=InterviewMainSerializer)
    def interview(self, request, pk):
        # bisa masuk sini kalo interview register, interviewer status == 2
        instance = InterviewRegister.objects.get(pk=pk)

        if not (
                    instance.status == 2 and request.user.interviewer.status == 2 and instance.pk == request.user.interviewer.statusDesc):
            return HttpResponseRedirect('../../')

        if request.method == 'GET':
            serializer = InterviewMainSerializer(instance)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = InterviewMainSerializer(instance=instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                instance.status = 3
                request.user.interviewer.status = 0
                instance.save()
                request.user.interviewer.save()
            return HttpResponseRedirect('/admin')

    @detail_route()
    def cancel(self, request, pk):
        if request.user.interviewer.status == 1 or request.user.interviewer.status == 2:
            instance = InterviewRegister.objects.get(pk=request.user.interviewer.statusDesc)
            instance.status = 0
            instance.save()
            request.user.interviewer.status = 0
            request.user.interviewer.save()
        return HttpResponseRedirect('../../')

    @detail_route()
    def absent(self, request, pk):
        if request.user.interviewer.status == 1 or request.user.interviewer.status == 2:
            instance = InterviewRegister.objects.get(pk=request.user.interviewer.statusDesc)
            instance.status = 0
            instance.queueNumber = instance.department.queueLast + 1
            instance.department.queueLast += 1
            instance.department.save()
            instance.interviewee.countAccepted = instance.interviewee.hitung()
            instance.interviewee.save()
            instance.save()
            request.user.interviewer.status = 0
            request.user.interviewer.save()

        return HttpResponseRedirect('../../')

    def list(self, request, *args, **kwargs):
        if request.user.interviewer.status == 0:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.filter(department=request.user.interviewer.department)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        elif request.user.interviewer.status == 1 or request.user.interviewer.status == 2:
            return HttpResponseRedirect('./' + str(request.user.interviewer.statusDesc))

    def retrieve(self, request, *args, **kwargs):
        # can get in here if (0,0) , (1,1), (2,2)
        if request.user.interviewer.status == 0:
            instance = InterviewRegister.objects.get(pk=kwargs['pk'])
            # ini buat interviewer lain yg nyerobot org punya/ This created another interviewer who has people nyero boat
            if not (instance.status == 0 or instance.status == 3):
                return HttpResponseRedirect('/admin/')
            request.user.interviewer.status = 1
            request.user.interviewer.statusDesc = kwargs['pk']
            request.user.interviewer.save()
            instance.status = 1
            instance.save()
            return self.call(request, kwargs['pk'])
        else:
            if kwargs['pk'] != str(request.user.interviewer.statusDesc):
                return HttpResponseRedirect('/admin/' + str(request.user.interviewer.statusDesc))

            if request.user.interviewer.status == 1:
                return self.call(request, kwargs['pk'])
            elif request.user.interviewer.status == 2:
                return HttpResponseRedirect('/admin/' + kwargs['pk'] + '/interview')
            else:
                return Response({'detail': 'bug!!, please report how you can come up here!!!'})


class InterviewAdminJudgeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = InterviewJudgeSerializer
    renderer_classes = [AdminJudgeRenderer, ]
    permission_classes = (IsInterviewer,)

    def get_queryset(self):
        return InterviewRegister.objects.filter(status=3, department=self.request.user.interviewer.department).order_by(
            'score')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route()
    def markpending(self, request, pk):
        try:
            instance = InterviewRegister.objects.get(pk=pk)
        except:
            return HttpResponseRedirect('../../')
        instance.resultPending = 0
        instance.interviewee.countAccepted = instance.interviewee.hitung()
        instance.interviewee.save()
        instance.save()
        return HttpResponseRedirect('../../')

    @detail_route()
    def markaccept(self, request, pk):
        try:
            instance = InterviewRegister.objects.get(pk=pk)
        except:
            return HttpResponseRedirect('../../')
        instance.resultPending = 1
        instance.interviewee.countAccepted = instance.interviewee.hitung()
        instance.interviewee.save()
        instance.save()
        return HttpResponseRedirect('../../')

    @detail_route()
    def cancel(self, request, pk):
        try:
            instance = InterviewRegister.objects.get(pk=pk)
        except:
            return HttpResponseRedirect('../../')
        instance.status = 0
        instance.queueNumber = instance.department.queueLast + 1
        instance.department.queueLast += 1
        instance.resultPending = 0
        instance.department.save()
        instance.interviewee.countAccepted = instance.interviewee.hitung()
        instance.interviewee.save()
        instance.save()
        return HttpResponseRedirect('../../')


class InterviewRegisterViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                               mixins.CreateModelMixin, viewsets.GenericViewSet):
    "Queue registration"
    serializer_class = InterviewRegistrationSerializer
    renderer_classes = [BrowsableAPIRendererInterviewRegister]
    permission_classes = (permissions.IsAuthenticated, IsInterviewee)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InterviewRegistrationSerializer
        else:
            return InterviewRegistrationSerializer2

    def get_queryset(self):
        return InterviewRegister.objects.filter(status=0, interviewee=self.request.user.interviewee)

    @detail_route()
    def delete(self, request, pk):
        try:
            a = request.user.interviewee.interviewRegister.get(status=0, pk=pk)
            a.delete()
            return HttpResponseRedirect('../../')
        except:
            return HttpResponseRedirect('../../')


class IntervieweeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    User Page
    """
    queryset = Interviewee.objects.all()
    serializer_class = IntervieweeRegistrationSerializer
    renderer_classes = [BrowsableAPIRendererIntervieweeRegister, ]
    def list(self, request, *args, **kwargs):
        return Response(IntervieweeRegistrationSerializer.data)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAnonymous()]
        else:
            return [IsIntervieweeHimself()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Interviewee.objects.get(pk=kwargs['pk'])
        serializer = IntervieweeRegistrationUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return IntervieweeRegistrationUpdateSerializer
        else:
            return IntervieweeRegistrationSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            if kwargs['pk'] != str(request.user.interviewee.pk):
                return HttpResponseRedirect('../' + str(request.user.interviewee.pk))
        except:
            return HttpResponseRedirect('../../')

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)
