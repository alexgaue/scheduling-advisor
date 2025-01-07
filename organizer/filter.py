import django_filters

from .models import *

class AssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = Assignment
        fields = '__all__'