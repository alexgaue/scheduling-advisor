from django.urls import path

from . import views

app_name = 'organizer'
urlpatterns = [
    #POST Requests
    path('assignments/add/', views.add_assignment, name='new assignment'),
    path('assignments/delete/<int:assignment_id>', views.remove_assignment, name='delete assignment'),
    path('assignments/update/<int:assignment_id>/<int:status>', views.update_assignment_status, name='update assignment status'),
    path('classes/enroll/', views.joinClass, name='join class'),
    path('classes/unenroll/<int:cid>', views.unenrollClass, name='delete class'),
    
    #View
    path('assignments/view/calendar/<int:month>/<int:year>/', views.assigments_view_calendar, name='View_Assignments_Calendar'),
    path('assignments/view/list/', views.assignments_view_list, name='View_Assignments_List'),
    path('assignments/view/default/', views.assignments_view_redirect, name='View_Assignments_Redirect'),

    #Classes
    path('classes/view/class-list', views.classFinder, name='View_Class_List'),
    path('classes/view/my-classes/', views.myClasses, name='View_Classes'),
    path('classes/view/<int:cid>/', views.courseView, name='View_Class_Details'),
    
    path('notes/',views.notes_list, name ='Notes_list'),
    path('notes/upload/', views.upload_note, name='Upload_note'),
]
