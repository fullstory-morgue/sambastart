"""Simple options parser.
It wraps arount getopt, but it takes a list of options and calls getopt
then. It automaticaly handles --help and all options are initialized
with the default values.

Basic behaviour like twisted.python.usage.Options.

Example:
    class TestOptions(Options):
        optParameters = [
            #long name, short name, default value, description
            ["test",    "t",        None,          "value param"],
        ]
        optFlags = [
            #long name, short name, description
            ["flag",    "f",        "flag param"],
        ]
    o = TestOptions()
    o.parseOptions()
    print o.opts
    print o.args

o.opts is a dictionary that contains _all_ the options, flags default to 0.
o.args is a list with the rest of the command line that is not an option.

(C) 2003 Chris Liechti <cliechti@gmx.net>

Python license for this implementation. See license.txt.
"""

import sys, getopt, os

class UsageError(Exception): pass

class Options:
    """Options parser and container."""
    optParameters = []
    optFlags = []

    def __init__(self):
        """initialize options form the class attributes optParameters and optFlags"""
        self.shortparams = []
        self.longparams = []
        self.help = []
        for longname, shortname, default, description in self.optParameters:
            if len(shortname) != 1:
                raise ValueError, "short options must be one character"
            self.shortparams.append("%s:" % shortname)
            self.longparams.append("%s=" % longname)
            self.help.append(("-%s, --%s=" % (shortname, longname), 
                              "%s [default: %s]" % (description, default)))
        for longname, shortname, description in self.optFlags:
            if len(shortname) != 1:
                raise ValueError, "short options must be one character"
            self.shortparams.append("%s" % shortname)
            self.longparams.append("%s" % longname)
            self.help.append(("-%s, --%s " % (shortname, longname), 
                              "%s" % (description, )))
        self.shortparams.append("h")
        self.longparams.append("help")
        self.help.append(("-h, --help", "This help text"))

    def parseOptions(self):
        """parse options in sys.argv. It print the help and raises a
           SystemExit exception if --help is provided."""
        #print self.shortparams, self.longparams
        try:
            opts, self.args = getopt.getopt(sys.argv[1:],
                ''.join(self.shortparams),
                self.longparams
            )
        except getopt.GetoptError, message:
            # print help information and exit:
            raise UsageError, message
            
        self.opts = {}
        for longname, shortname, default, description in self.optParameters:
            self.opts[longname] = default
        for longname, shortname, description in self.optFlags:
            self.opts[longname] = 0
            
        for o, a in opts:
            if o in ("-h", "--help"):
                #self.help.sort()
                sys.stdout.write('USAGE: %s [options] [args]\n' % os.path.basename(sys.argv[0]))
                sys.stdout.write('\n'.join(["  %-20s %s" %h for h in self.help]) + '\n\n')
                sys.stdout.write(self.__str__())
                sys.stdout.write('\n')
                raise SystemExit, 0
            else:
                for longname, shortname, default, description in self.optParameters:
                    if o in ("-%s" % shortname, "--%s" % longname):
                        self.opts[longname] = a
                for longname, shortname, description in self.optFlags:
                    if o in ("-%s" % shortname, "--%s" % longname):
                        self.opts[longname] = 1

        def __str__(self):
            """override this method to write out more dscriptive text on --help"""
            return ""

#simple test
if __name__ == '__main__':
    class TestOptions(Options):
        optParameters = [
            ["test", "t", None, "value param"],
        ]
        optFlags = [
            ["flag", "f", "flag param"],
        ]
    o = TestOptions()
    o.parseOptions()
    print o.opts
    print o.args

