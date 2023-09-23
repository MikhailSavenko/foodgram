from rest_framework import mixins, viewsets


class CreateDestroyView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass
