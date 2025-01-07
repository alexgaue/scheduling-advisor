from django import forms
from django.db.models import query
from .models import Assignment, ClassNotes, Course, User
from django.contrib.admin import widgets



# ModelForm for creating assignments
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['deadline', 'title']
        widgets = {
            'deadline': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield'}),
        }
class NotesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(NotesForm, self).__init__(*args, **kwargs)
        self.fields["notes_class"].queryset = self.request.user.course_set.all()

    class Meta:
        model = ClassNotes
        fields = '__all__'





