from time import localtime

# HELPER FUNCTION TO GET LOCAL TIME
def getLocalTime():
    timeStruct = localtime()
    timeString = ':'.join([str(timeStruct[3]), str(timeStruct[4]).zfill(2)])
    dateString = '/'.join([str(timeStruct[1]), str(timeStruct[2]), str(timeStruct[0])[2:]])
    return timeString + ' - ' + dateString