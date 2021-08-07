from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import random as rnd
from. forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required



POPSIZE = 9
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.05
divs = Room.objects.distinct()
days = ['Mon','Tue','Wed','Thu','Fri','Sat']

class Data:
    def __init__(self):
        self._rooms = Room.objects.all()
        self._meetingTimes = MeetingTime.objects.all()
        self._instructors = Instructor.objects.all()
        self._courses = Course.objects.all()
        self._depts = Department.objects.all()

    def get_rooms(self): return self._rooms

    def get_instructors(self): return self._instructors

    def get_courses(self): return self._courses

    def get_depts(self): return self._depts

    def get_meetingTimes(self): return self._meetingTimes


class Schedule:
    def __init__(self):
        
        self._data = data
        self._classes = []
        self._numberOfConflicts = 0
        self._fitness = -1
        self._classNumb = 0
        self._isFitnessChanged = True

    def get_classes(self):
        self._isFitnessChanged = True
        return self._classes

    def get_numbOfConflicts(self): return self._numberOfConflicts

    def get_fitness(self):
        if self._isFitnessChanged:
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness

    def initialize(self):
        sections = Section.objects.all()
        for section in sections:
            dept = section.department
            n = section.maxClasses
            if n <= len(MeetingTime.objects.all()):
                courses = dept.courses.all()
                for course in courses:
                    for i in range(n // len(courses)):
                        crs_inst = course.instructors.all()
                        newClass = Class(self._classNumb, dept,
                                         section.section_id, course)
                        self._classNumb += 1
                        newClass.set_meetingTime(data.get_meetingTimes(
                        )[rnd.randrange(0, len(MeetingTime.objects.all()))])
                        newClass.set_room(
                            data.get_rooms()[rnd.randrange(0, len(data.get_rooms()))])
                        newClass.set_instructor(
                            crs_inst[rnd.randrange(0, len(crs_inst))])
                        self._classes.append(newClass)
            else:
                n = len(MeetingTime.objects.all())
                courses = dept.courses.all()
                for course in courses:
                    for i in range(n // len(courses)):
                        crs_inst = course.instructors.all()
                        newClass = Class(self._classNumb, dept,
                                         section.section_id, course)
                        self._classNumb += 1
                        newClass.set_meetingTime(data.get_meetingTimes(
                        )[rnd.randrange(0, len(MeetingTime.objects.all()))])
                        newClass.set_room(
                            data.get_rooms()[rnd.randrange(0, len(data.get_rooms()))])
                        newClass.set_instructor(
                            crs_inst[rnd.randrange(0, len(crs_inst))])
                        self._classes.append(newClass)

        return self

    def calculate_fitness(self):
        self._numberOfConflicts = 0
        classes = self.get_classes()
        for i in range(0, len(classes)):
            if classes[i].room.seating_capacity < int(classes[i].course.maxStudents):
                self._numberOfConflicts += 1
            for j in range(len(classes)):
                if j >= i:
                    if (classes[i].meeting_time == classes[j].meeting_time) and \
                            (classes[i].section_id != classes[j].section_id) and (classes[i].section == classes[j].section):
                        if classes[i].room == classes[j].room:
                            self._numberOfConflicts += 1
                        if classes[i].instructor == classes[j].instructor:
                            self._numberOfConflicts += 1
                            #Remove below line if not correct output is shown or takes too much time
    
        return 1 / (1.0 * self._numberOfConflicts + 1)


class Population:
    def __init__(self, size):
        self._size = size
        self._data = data
        self._schedules = [Schedule().initialize() for i in range(size)]

    def get_schedules(self):
        return self._schedules


class GeneticAlgorithm:
    def evovePopulation(self, population):
        return self.mutateScheduler(self.crossoverPop(population))

    def crossoverPop(self, pop):
        crossover_pop = Population(0)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPSIZE:
            schedule1 = self.tournament_Selector(pop).get_schedules()[
                0]
            schedule2 = self.tournament_Selector(pop).get_schedules()[
                0]
            crossover_pop.get_schedules().append(
                self.crossSchedule(schedule1, schedule2))
            i += 1
        return crossover_pop

    def mutateScheduler(self, population):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPSIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population

    def crossSchedule(self, schedule1, schedule2):
        crossoverSchedule = Schedule().initialize()
        for i in range(0, len(crossoverSchedule.get_classes())):
            if rnd.random() > 0.5:
                crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule

    def _mutate_schedule(self, mutateSchedule):
        schedule = Schedule().initialize()
        for i in range(len(mutateSchedule.get_classes())):
            if MUTATION_RATE > rnd.random():
                mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule

    def tournament_Selector(self, pop):
        tournament_pop = Population(0)
        i = 0
        while i < TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(
                pop.get_schedules()[rnd.randrange(0, POPSIZE)])
            i += 1
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop


class Class:
    def __init__(self, id, dept, section, course):
        self.section_id = id
        self.department = dept
        self.course = course
        self.instructor = None
        self.meeting_time = None

        #dividing meeting_time into day and time seperately
        self.day = None
        self.time = None
        ###################################################
        self.div = None


        self.room = None
        self.section = section

    def get_id(self): return self.section_id

    def get_dept(self): return self.department

    def get_course(self): return self.course

    def get_instructor(self): return self.instructor

    def get_meetingTime(self): return self.meeting_time

    def get_room(self): return self.room

    def set_instructor(self, instructor): self.instructor = instructor

    def set_meetingTime(self, meetingTime): self.meeting_time = meetingTime

    def set_room(self, room): self.room = room


data = Data()


@login_required(login_url='loginUser')
def home(request):
    return render(request, 'home.html', {})

@login_required(login_url='loginUser')
def timetable(request):
    schedule = []
    population = Population(POPSIZE)
    generation_num = 0
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
    geneticAlgorithm = GeneticAlgorithm()
    while population.get_schedules()[0].get_fitness() != 1.0:
        generation_num += 1
        print('\n> Generation #' + str(generation_num))
        population = geneticAlgorithm.evovePopulation(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        schedule = population.get_schedules()[0].get_classes()

    ###########cutsom sorting############
    from .temp_sort import t_sort
    schedule = t_sort(schedule)
    
    ###########processing data for output############
    data = {'schedule': schedule, 'sections': Section.objects.all(), 'times': MeetingTime.objects.all(),'divs':divs, 'days':days}

    from .generate_xlsx import generate_xlsx
    import pandas as pd
    
    generate_xlsx(data)
    #print("PDFs generated")

    return render(request, 'generate.html', data)
    #return render(request, 'generate.html', {"DataFrame": web_df})

@login_required(login_url='loginUser')
def add_instructor(request):
    form = InstructorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addinstructor')
    context = {
        'form': form
    }
    return render(request, 'addinstructor.html', context)

@login_required(login_url='loginUser')
def inst_list_view(request):
    context = {
        'instructors': Instructor.objects.all()
    }
    return render(request, 'showinst.html', context)


@login_required(login_url='loginUser')
def delete_instructor(request, pk):
    inst = Instructor.objects.filter(pk=pk)
    if request.method == 'POST':
        inst.delete()
        return redirect('editinstructor')

@login_required(login_url='loginUser')
def add_room(request):
    form = RoomForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addroom')
    context = {
        'form': form
    }
    return render(request, 'addroom.html', context)

@login_required(login_url='loginUser')
def room_list(request):
    context = {
        'rooms': Room.objects.all()
    }
    return render(request, 'roomlist.html', context)

@login_required(login_url='loginUser')
def delete_room(request, pk):
    rm = Room.objects.filter(pk=pk)
    if request.method == 'POST':
        rm.delete()
        return redirect('editrooms')

@login_required(login_url='loginUser')
def meeting_list_view(request):
    context = {
        'meeting_times': MeetingTime.objects.all()  # Changed
    }
    return render(request, 'showtime.html', context)

@login_required(login_url='loginUser')
def add_meeting_time(request):
    form = MeetingTimeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addmeetingtime')
        else:
            print('Invalid')
    context = {
        'form': form
    }
    return render(request, 'classtime.html', context)

@login_required(login_url='loginUser')
def delete_meeting_time(request, pk):
    mt = MeetingTime.objects.filter(pk=pk)
    if request.method == 'POST':
        mt.delete()
        return redirect('editmeetingtime')

@login_required(login_url='loginUser')
def course_list_view(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, 'removesub.html', context)

@login_required(login_url='loginUser')
def add_course(request):
    form = CourseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addcourse')
        else:
            print('Invalid')
    context = {
        'form': form
    }
    return render(request, 'addsubjects.html', context)

@login_required(login_url='loginUser')
def delete_course(request, pk):
    crs = Course.objects.filter(pk=pk)
    if request.method == 'POST':
        crs.delete()
        return redirect('editcourse')

@login_required(login_url='loginUser')
def add_department(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('adddepartment')
    context = {
        'form': form
    }
    return render(request, 'adddept.html', context)

@login_required(login_url='loginUser')
def department_list(request):
    context = {
        'departments': Department.objects.all()
    }
    return render(request, 'removedept.html', context)

@login_required(login_url='loginUser')
def delete_department(request, pk):
    dept = Department.objects.filter(pk=pk)
    if request.method == 'POST':
        dept.delete()
        return redirect('editdepartment')

@login_required(login_url='loginUser')
def add_section(request):
    form = SectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addsection')
    context = {
        'form': form
    }
    return render(request, 'adddivision.html', context)

@login_required(login_url='loginUser')
def section_list(request):
    context = {
        'sections': Section.objects.all()
    }
    return render(request, 'removediv.html', context)

@login_required(login_url='loginUser')
def delete_section(request, pk):
    sec = Section.objects.filter(pk=pk)
    if request.method == 'POST':
        sec.delete()
        return redirect('editsection')

from django.contrib import messages

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method=="POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username = username, password = password)

            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request, "Username or Password Incorrect!")
                

        context = {}
        return render(request,'login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('loginUser')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = createUserForm()
        if request.method == 'POST':
            form = createUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request,'Account Created For ' + user)

                return redirect('loginUser')


        context = {'form':form}
        return render(request,'register.html',context)
