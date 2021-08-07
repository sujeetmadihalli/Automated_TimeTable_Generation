from datetime import datetime
##############sort comparison functions############
def days_sort(var):
    days_order = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5}
    return days_order[var.day] 

def time_sort(var):
    time_order = {'9:30 - 10:30':0,'10:30 - 11:30':1,'11:30 - 12:30':2,'12:30 - 1:30':3,'2:30 - 3:30':4,'3:30 - 4:30':5,'4:30 - 5:30':6}
    return time_order[var.time]

def division_sort(var):
    div_order = {'A':0,'B':1,'C':2,'D':3}
    return div_order[var.div]

################return to main functions##################
def t_sort(var):   
    for i in var:
        temp = str(i.meeting_time)
        i.day = temp[:3]
        t = temp[-13:].strip()
        if t[0] == 'y':
            i.time = temp[-12:].strip()
        else:
            i.time = temp[-13:].strip()   
        i.div = str(i.room)
        
    var = sorted(var, key=time_sort)
    var = sorted(var, key=days_sort)
    var = sorted(var, key=division_sort)

    return var

    
    #days_order = ['Mon','Tue','Wed','Thu','Fri','Sat']
    #return sorted(var, key=lambda var: var.meeting_time, reverse=True)
    #return sorted(var, key=lambda x: datetime.strptime(var[meeting_time], '%A %-I - %-M'), reverse=True)