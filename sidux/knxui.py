"""Simple wrapper around (X)dialog.

If the environment variable DISPLAY is set, then the X version is used, the
text based otherwise.

(C) 2003 Chris Liechti <cliechti@gmx.net>
"""

import sys, os

#find out which version to use
if os.environ.has_key('DISPLAY'):
    DIALOG = 'Xdialog'
    os.environ['XDIALOG_HIGH_COMPATDIALOG'] = '1'
    GUI = 1
else:
    DIALOG = 'dialog'
    GUI = 0

def _checkresult(exitcode, result):
    """Check exit code of (X)dialog and raise an exeception if aborted."""
    #print "XXX", exitcode
    if exitcode == 1 or exitcode >= 255:
        raise KeyboardInterrupt, "User aborted"
    return result

def get_file(path=os.curdir+'/', title="Please choose a file"):
    """Open a file entry dialog."""
    #sizing is different...
    fin = os.popen('%s --stdout --title %r --fselect %s %s' % (DIALOG, title, path, GUI and '0 0' or '14 48'))
    result = fin.read().strip()
    status = fin.close()
    return _checkresult(status, result)

def input(question, title="Enter a value", default=''):
    """Text entry field."""
    #sizing is different...
    fin = os.popen('%s --stdout --title %r --inputbox %r 0 0 %r' % (DIALOG, title, question, default))
    result = fin.read().strip()
    status = fin.close()
    return _checkresult(status, result)

def yesno(message, defaultno=0, title="", size='0 0'):
    """Ask a yes/no question, return 1 == yes, 0 == no."""
    fin = os.popen('%s --stdout %s --title %r --yesno %r %s' % (DIALOG, defaultno and '--defaultno' or '', title, message, size))
    result = fin.read()
    status = fin.close()
    return not status
    
def message(message, title="", size='0 0'):
    """Simple message box."""
    fin = os.popen('%s --stdout --title %r --msgbox %r %s' % (DIALOG, title, message, size))
    result = fin.read()
    status = fin.close()
    return _checkresult(status, result)

def menu(entries, title="", size='0 0', lines=10):
    """Menu selection.
       A list of entries is given as parameter:
       [(tag1, description1), (tag2, description2)...]
       Each element must be a string.
       The tag is returned when an entry is selected."""
    fin = os.popen('%s --stdout --menu %r %s %d %s' % (
        DIALOG, title or ' ', size, lines, ' '.join(["%r %r" % tuple(x) for x in entries]))
    )
    result = fin.read()
    status = fin.close()
    return _checkresult(status, result.strip())

def checklist(entries, title="", size='0 0', lines=10):
    """Selection.
       A list of entries is given as parameter:
       [(tag1, description1, status1), (tag2, description2, status2)...]
       tag and desc must be a string, status a number 0 or 1.
       The tag is returned when an entry is selected."""
    fin = os.popen('%s --stdout --separate-output --checklist %r %s %d %s' % (
        DIALOG, title or ' ', size, lines, ' '.join(["%r %r %s" % tuple(x) for x in entries]))
    )
    result = fin.read()
    status = fin.close()
    return _checkresult(status, [x.strip() for x in result.split('\n') if x])
    

#some poor tests...
if __name__ == '__main__':
    t = input("Enter some text")
    raw_input('Result: %r\n-ENTER-' % t)
    
    c = checklist([
    	['tag1', 'desc1', 0],
    	['tag2', 'desc2', 1],
    ])
    raw_input('Result: %r\n-ENTER-' % c)
    
    m = menu([
        ['first',  'short1'],
        ['second', 'short2'],
    ])
    message("selected %r in menu" % m)
    
    filename = get_file()
    ans = yesno("do you realy want to do this?", title="answer me")
    message("you said %r and chose %r before" % ((ans and 'yes' or 'no'), filename))
    
