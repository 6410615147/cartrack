import os
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.serializer import VDOSerializer,StatusSerializer

from cartrack.task import run_detect
from cartrack.settings import BASE_DIR

from api.models import VDO
from django_celery_results.models import TaskResult
    

# Create your views here.


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class VDOViewSet(ModelViewSet):
    #queryset = VDO.objects.all()
    serializer_class = VDOSerializer
    #permission_classes = (IsAuthenticated,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
        lp = request.FILES.getlist('loop', None)
        vdo = request.FILES.getlist('vdo', None)
        if len(lp)> 0 and len(vdo)>0:
            fileobject = VDO.objects.create(loop=lp[0],vdo=vdo[0])
            loopname,vdoname =  os.path.join(BASE_DIR,fileobject.loop.name),os.path.join(BASE_DIR,fileobject.vdo.name)
            print(loopname,vdoname)
            res = run_detect.apply_async((loopname,vdoname))
            #convert task_id to pk
            return Response(data=f"/status/{res.id}", status=status.HTTP_201_CREATED)  # NOQA
        else:
            return Response(data='Bad request.', status=status.HTTP_400_BAD_REQUEST)  

class StatusViewSet(ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = StatusSerializer
    #permission_classes = (IsAuthenticated,)
    http_method_names = ['post','get']
    def retrieve(self, request,pk=None):
        ts = TaskResult.objects.get_task(pk)
        sts = StatusSerializer(ts)
        return Response(sts.data)
