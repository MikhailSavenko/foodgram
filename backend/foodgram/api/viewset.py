from rest_framework import viewsets,  mixins


class CreateDestroyView(mixins.CreateModelMixin, 
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    pass