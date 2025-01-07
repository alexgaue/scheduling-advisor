from django.shortcuts import render, redirect

from .models import *
from .forms import *
from .calendar import *

from django.contrib.auth.mixins import LoginRequiredMixin

from google.oauth2 import service_account
from googleapiclient.discovery import build 

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

import json
import requests

#https://blog.benhammond.tech/connecting-google-cal-api-and-django
#service_account_email = "djangoservice@django-oauth-a29.iam.gserviceaccount.com "
credentials = service_account.Credentials.from_service_account_file('service_account.json')
scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/calendar"])

#Retrieve User Settings Account
def GetUserAccount(request_user):
    user_account = Account.objects.filter(user=request_user)
    
    if (len(user_account) == 0):
        #No Saved Account - Create Default Account
        account = Account()
        account.user = request_user
        account.default_view = "calendar"
        account.save()
        return account

    return user_account[0]

def add_assignment(request):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')

    if request.method != "POST":
        return redirect('/')
    
    form = AssignmentForm(request.POST)
    new_assignment = None
    if form.is_valid():
        new_assignment = form.save(commit=False)
        new_assignment.user = request.user
        new_assignment.save()
        messages.success(request, "Assignment has been added successfully.")
    
    #Add to Calendar
    service = build("calendar", "v3", credentials=credentials)

    service.events().insert(
        calendarId="primary",
        body={
            "summary": "Foo",
            "description": "Bar",
            "start": {"dateTime": new_assignment.deadline.isoformat()},
            "end": {"dateTime": new_assignment.deadline.isoformat()},
        },
    ).execute()

    if (request.META.get('HTTP_REFERER')):
        return redirect(request.META.get('HTTP_REFERER'))

    return redirect("organizer:View_Assignments_Redirect")

def remove_assignment(request, assignment_id):
    Assignment.objects.get(pk=assignment_id).delete()
    
    if (request.META.get('HTTP_REFERER')):
        return redirect(request.META.get('HTTP_REFERER'))

    return redirect("organizer:View_Assignments_Redirect")

def update_assignment_status(request, assignment_id, status):
    assignment = Assignment.objects.get(pk=assignment_id)

    if (status == 1):
        assignment.assignment_status = Assignment.AssignmentStatus.Todo
    elif (status == 2):
        assignment.assignment_status = Assignment.AssignmentStatus.InProgress
    elif (status == 3):
        assignment.assignment_status = Assignment.AssignmentStatus.Completed

    assignment.save()

    if (request.META.get('HTTP_REFERER')):
        return redirect(request.META.get('HTTP_REFERER'))

    return redirect("organizer:View_Assignments_Redirect")
    
#View Assignments Page
def assignments_view_redirect(request):  
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    user_account = GetUserAccount(request.user)

    if (user_account.default_view == "calendar"):
        now = datetime.now()
        return redirect("organizer:View_Assignments_Calendar", year=now.year, month=now.month)

    elif (user_account.default_view == "list"):
        return redirect("organizer:View_Assignments_List")    
    
def assigments_view_calendar(request, month, year):    
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')

    if (year < 0 or month < 0 or month > 12):
        now = datetime.now()
        return redirect("organizer:View_Assignments_Calendar", year=now.year, month=now.month)
        
    return render(request, 'organizer/assignments_view_calendar.html',
        context = {
            "calendar":Calendar(year, month).formatmonth(request.user),
            "form":AssignmentForm()
        }) 

def assignments_view_list(request):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    return render(request, 'organizer/assignments_view_list.html',
        context = {
            "assignments": Assignment.objects.filter(user=request.user),
            "form":AssignmentForm(),
            "cur_month":datetime.now().month,
            "cur_year":datetime.now().year
        }) 

def classFinder(request):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    course = request.GET.get('cnumber')
    object_list = []
    query = False
    if course:
        course = course.strip().lower()
        department = False
        query = True
        if " " in course:
            department, cnumber = course.split()
        else:
            department = course
            cnumber = False
        url = 'https://api.devhub.virginia.edu/v1/courses'
        data = requests.get(url).json()
        if cnumber:
            for course in data['class_schedules']['records']:
                if course[0].lower() == department and course[1] == cnumber and course[-1] == "2022 Spring":
                    object_list.append(course)
        else:
            for course in data['class_schedules']['records']:
                if course[0].lower() == department and course[-1] == "2022 Spring":
                    object_list.append(course)
    return render(request, 'organizer/classList.html', context = {'courses': object_list, 'query':query})

def joinClass(request):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    cid = int(request.POST.get('cid'))
    try:
        course = Course.objects.get(courseid=cid)
        course.roster.add(request.user)
    except Course.DoesNotExist:
        new_course = Course(courseid=cid, course_name=request.POST.get('cname'))
        new_course.save()
        new_course.roster.add(request.user)
        
    return HttpResponseRedirect(reverse('organizer:View_Class_Details', args=(cid,)))

def unenrollClass(request, cid):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    course = Course.objects.get(courseid=cid)
    course.roster.remove(request.user)
    course.save()
    
    return HttpResponseRedirect(reverse('organizer:View_Classes'))
    
def myClasses(request):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    courses = request.user.course_set.all()
    cids = []
    for course in courses:
        cids.append(course.courseid)
    url = 'https://api.devhub.virginia.edu/v1/courses'
    data = requests.get(url).json()
    my_courses = []
    for course in data['class_schedules']['records']:
        if course[3] in cids and course[-1] == "2024 Spring":
            my_courses.append(course)
    return render(request, 'organizer/myClasses.html',
                  context = {
                      'courses': my_courses,
                      'cids':cids,
                      'form':NotesForm(request=request)
                      }
                  )

def courseView(request, cid):
    if (str(request.user).strip() == 'AnonymousUser'):
        return redirect('/')
    
    course = Course.objects.get(courseid=cid)
    notes = ClassNotes.objects.filter(notes_class_id = cid)
    url = 'https://api.devhub.virginia.edu/v1/courses'
    data = requests.get(url).json()
    students = course.roster.all()
    for classDetails in data['class_schedules']['records']:
        if classDetails[3] == cid and classDetails[-1] == "2024 Spring":
            coursedata = tuple(classDetails)
    return render(request, 'organizer/classView.html',
                  context = {
                      'course': coursedata,
                      'students': students,
                      'notes':notes
                      }
                  )


def notes_list(request):
    notes = ClassNotes.objects.all()
    return render(request, 'organizer/noteslist.html',{
        'notes': notes
    })

def upload_note(request):
    if request.method == 'POST':
        form = NotesForm(request.POST,request.FILES,request=request)

        if form.is_valid():
            form.save()
            messages.success(request, "Note added to class.")
    else:
        form = NotesForm(request=request)

    if (request.META.get('HTTP_REFERER')):
        return redirect(request.META.get('HTTP_REFERER'))

    return redirect(request, "organizer:View_Classes")

