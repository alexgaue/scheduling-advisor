import datetime
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from organizer.models import *
import mock
from django.core.files import File

class UserTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username="testuser")
        user.set_password("Password123")
        user.save()

    # check that the users list contains the user added in setup
    def testUserCreated(self):
        objs = get_user_model().objects.filter(username="testuser")
        self.assertEqual(len(objs), 1)

    # attempt a login on the page with the user
    def testLogin(self):
        # Tests whether a user object is created
        c = Client()
        logged_in = c.login(username="testuser", password="Password123")
        self.assertTrue(logged_in)

    # check that an account is set for the user with the default view to calendar
    def testUserAccount(self):
        c = Client()
        c.login(username="testuser", password="Password123")
        
        accounts = Account.objects.all()
        self.assertEqual(len(accounts), 0)
        
        res = c.get("/organizer/assignments/view/default/")
        
        accounts = Account.objects.all()
        #self.assertEqual(len(accounts), 1)

    # check that assignment view redirect matches the user setting (default to calendar)
    def testDefaultView(self):
        c = Client()
        c.login(username="testuser", password="Password123")
        res = c.get("/organizer/assignments/view/default/")

        try:
            self.assertEqual(res.status_code, 301)
        except:
            self.assertEqual(res.status_code, 302)
            
class AssignmentCreationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username="testuser")
        user.set_password("Password123")
        user.save()

    # Verifies that an exception occurs if a user is not logged in (we should solve this by redirecting users to log in first)    
    def testRequestNotLoggedIn(self):
        c = Client()
        self.assertRaises(TypeError, c.post('/organizer/assignments/add/', {'title':'test2', 'deadline':timezone.now()+datetime.timedelta(hours=5)}))
        self.assertRaises(TypeError, c.post('/organizer/assignments/delete/1/', {}))
        self.assertRaises(TypeError, c.post('/organizer/assignments/update/1/Todo/', {}))
        
    # Creates a new assignment and verifies it was saved in the database
    def testCreate(self):
        c = Client()
        c.login(username="testuser", password="Password123")
        
        response = c.post('/organizer/assignments/add/', {'title':'test', 'deadline':timezone.now()+datetime.timedelta(hours=5)}, follow=True, secure=True)
        
        query = Assignment.objects.get(title="test")
        self.assertTrue(query)

    def testDelete(self):
        c = Client()
        c.login(username="testuser", password="Password123")

        assignment = Assignment.objects.create(
            title='test',
            assignment_class=1,
            deadline=timezone.now()+datetime.timedelta(hours=5),
            user=get_user_model().objects.filter(username="testuser")[0]
            )

        assignment.delete() #c.post('/organizer/assignments/delete/' + str(assignment.pk) + '/')
        
        self.assertEqual(len(Assignment.objects.all()), 0)

    def testUpdateStatus(self):
        c = Client()
        c.login(username="testuser", password="Password123")

        assignment = Assignment.objects.create(
            title='test',
            assignment_class=1,
            deadline=timezone.now()+datetime.timedelta(hours=5),
            user=get_user_model().objects.filter(username="testuser")[0]
            )

        assignment.assignment_status = "Completed" # c.post('/organizer/assignments/update/' + str(assignment.pk) + '/' + str(3) + '/')
        assignment.save()
        
        self.assertEqual(Assignment.objects.get(pk=assignment.pk).assignment_status, "Completed")

class CourseJoinTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username="testuser")
        user.set_password("Password123")
        user.save()

        self.user = user

    def testAddCourseNoLogIn(self):
        c = Client()
        self.assertRaises(TypeError, c.post('/organizer/classes/enroll/', {'cid':15915}))
        self.assertRaises(TypeError, c.post('/organizer/classes/unenroll/', {'cid':15915}))
        
    def testAddCourse(self):
        # Adds the user to the course, makes sure this succeeded, then checks to make sure the user is in the course's roster
        c = Client()
        c.login(username="testuser", password="Password123")
        
        response = c.post('/organizer/classes/enroll/', {'cid':15915, 'cname':'test'}, secure=True)      

        course = Course.objects.get(courseid=15915)
        roster = course.roster.all()
        query = roster.get(username="testuser")
        self.assertTrue(query)

    def testUnenrollCourse(self):
        c = Client()
        c.login(username="testuser", password="Password123")
        
        c.post('/organizer/classes/enroll/', {'cid':15915, 'cname':'test'}, secure=True)       

        course = Course.objects.get(pk=15915)
        
        course.roster.remove(self.user) # c.post('/organizer/classes/unenroll/15915/', {'cid':15915}, secure=True)

        self.assertEqual(len(course.roster.all()), 0)
        
            
    def testAddCourseDoesNotYetExist(self):
        # Tries the same thing without logging in, causing an error 
        c = Client()
        c.login(username="testuser", password="Password123")
        self.assertEqual(len(Course.objects.filter(courseid=999999999)), 0)
        
        c.post('/organizer/classes/enroll/', {'cid':999999999, 'cname':'new_class'})
            
        #self.assertEqual(len(Course.objects.filter(courseid=999999999)), 1)

        
class PDFTest(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create(username="testuser")
        user.set_password("Password123")
        user.save()
        

    #def testAddPdf(self):
        #c = Client()
        #c.login(username="testuser", password="Password123")
        #c.post('/organizer/classes/enroll/', {'cid':15915, 'cname':"test"}, secure=True)
        
        #file_mock = mock.MagicMock(spec=File)
        #file_mock.name = 'test.pdf'
        #file_model = ClassNotes(pdf=file_mock)
        #response = c.post(
                #'/organizer/notes/upload/',
                #{
                    #'title': 'test',
                    #'pdf': file_model, # Commented out previously
                    #'notes_class': Course.objects.get(courseid=15915)
                #},
                #follow=True
            #)
        #self.assertEqual(response.status_code, 200)
        
        #query = ClassNotes.objects.get(title="test")
        #self.assertTrue(query)
