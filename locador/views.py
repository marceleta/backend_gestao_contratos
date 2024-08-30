from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Locador
from .serializers import LocadorSerializer
from django.shortcuts import get_object_or_404

class LocadorViewSet(viewsets.ModelViewSet):
    queryset = Locador.objects.all()
    serializer_class = LocadorSerializer

    def get_queryset(self):
        """
        Custom queryset to filter data based on user's permissions or other criteria.
        """
        # Add custom filtering logic here if necessary
        return super().get_queryset()

    def perform_create(self, serializer):
        """
        Custom behavior for creating a Locador instance.
        """
        # Add any pre-save logic here if necessary
        serializer.save()
        # Add any post-save logic here if necessary

    def perform_update(self, serializer):
        """
        Custom behavior for updating a Locador instance.
        """
        # Add any pre-save logic here if necessary
        serializer.save()
        # Add any post-save logic here if necessary

    def perform_destroy(self, instance):
        """
        Custom behavior for deleting a Locador instance.
        """
        # Add any pre-delete logic here if necessary
        instance.delete()

    @action(detail=False, methods=['get'], url_path='active')
    def list_active(self, request):
        """
        Custom action to list only active locadors.
        """
        active_locadors = self.get_queryset().filter(ativo=True)
        serializer = self.get_serializer(active_locadors, many=True)
        return Response(serializer.data)

