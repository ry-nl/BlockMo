from time import localtime
from app.routes import session

# GET USER FROM SESSION HELPER 
def getUserFromSession():
    if 'user' in session:
        return session['user']
    else:
        return None

# GET LOCAL TIME HELPER
def getLocalTime():
    timeStruct = localtime()
    timeString = ':'.join([str(timeStruct[3]), str(timeStruct[4]).zfill(2)])
    dateString = '/'.join([str(timeStruct[1]), str(timeStruct[2]), str(timeStruct[0])[2:]])
    return timeString + ' - ' + dateString