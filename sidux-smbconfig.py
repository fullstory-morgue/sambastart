#!/usr/bin/python

import sys, re
re_section = re.compile("\[(.*?)\]")
re_comment = re.compile("comment[\t ]*=(.*)")
re_path    = re.compile("path[\t ]*=(.*)")

#--
_locale_domain = "sidux-smbconfig"
_locale_dir = "/usr/share/locale"

try:
	import gettext  # python 2.0
	gettext.install(_locale_domain, _locale_dir)
except:
	def _(s): return s
#--
	
class Section:
	def __init__(self, name):
		self.name = name
		self.lines = []
	
	def getName(self):
		return self.name
		
	def getComment(self):
		desc = re_comment.search(''.join(self.lines))
		if desc:
			return desc.group(1).strip()
		else:
			return _("<no description>")

	def getPath(self):
		desc = re_path.search(''.join(self.lines))
		if desc:
			return desc.group(1).strip()
		else:
			return ""
			
	def __str__(self):
		return "%s(%s, %s)" % (self.__class__.__name__, self.name, self.getComment())
	__repr__ = __str__

class SMBConf:
	def __init__(self, filename='/etc/samba/smb.conf'):
		self.filename = filename
		self.sections = None
		self.headers = []
		self.parse(filename)
		self.changed = 0

	def parse(self, filename):
		self.sections = None
		self.headers = []
		section = None
		for line in file(filename):
			g = re_section.search(line)
			if g and line.strip()[0] != ';':
				section = Section(g.group(1))
				if self.sections is None:
					self.sections = [section]
				else:	
					self.sections.append(section)
			
			if section is not None:
				section.lines.append(line)
			if self.sections is None:
				self.headers.append(line)

	def write(self, fileobj=None):
		if fileobj is None:
			fileobj = file(self.filename, 'w')
		fileobj.write(''.join(self.headers))
		if self.sections is not None:
			for section in self.sections:
				fileobj.write(''.join(section.lines))

	def __str__(self):
		return "%s(%r)" % (self.__class__.__name__, self.sections)

	def deleteSection(self, name):
		for section in self.sections:
			if section.name == name:
				self.sections.remove(section)
				self.changed = 1
				break
		else:
			raise IndexError(_("Section with name %r not found") % name)
		
	def addSection(self, name, path, comment = None, writeable=0):
		if comment is None:
			comment = path
			
		section = Section(name) 
		section.lines = [
			'[%s]\n' % name,
			'   path = %s\n' % path,
			'   comment = %s\n' % comment,
			'   writeable = %s\n' % (writeable and 'yes' or 'no'),
			'   public = yes\n',
			'   browseable = yes\n',
		]
		self.sections.append(section)
		self.changed = 1
	
if __name__ == '__main__':
	from sidux import knxui, knxoptions
	class Options(knxoptions.Options):
		optParameters = [
		    ['name',      'n', None, _('Name of the share')],
		    ['path',      'p', None, _('Path of the share')],
		    ['comment',   'c', None, _('Comment of the share')],
		    ['conf',      'f', '/etc/samba/smb.conf',  _('Specify alternative config file')],
	        ]
		optFlags = [
		    ['writeable', 'w', _('Create writeable share')],
		    ['stdout',    's', _('Write result to stdout instead of configfile')]
	        ]
		def __str__(self):
        	    return __doc__
	    
	def getsections():
		return [(s.name, "%s [%s]" % (s.getPath(), s.getComment()), 0) 
			for s in conf.sections 
			if s.name != 'global' and s.name != 'printers' and s.name != 'homes']
		
	def interactive():
		while 1:
			what = knxui.menu([
				('list',  _('List shares')),
				('add',   _('Add a share')),
				('del',   _('Delete shares')),
				('exit',  _('Exit')),
			])
			try:
				if what == 'list':
					shares = getsections()
					if shares:
						knxui.checklist(shares, size='14 60')
					else:
						knxui.message(_("No active shares"))
				elif what == 'add':
					while 1:
						path = knxui.input(_('Directory that is expotred'))
						if path: break
						knxui.message(_('Enter a valid path'))
					while 1:
						name = knxui.input(_('Name of the share'))
						if name in [s.name for s in conf.sections]:
							knxui.message(_('A share with that name already exists'))
						elif not name or len(name) > 12:
							knxui.message(_('You need to enter a name with less than 12 characters'))
						else:
							break
					desc = knxui.input(_('Comment')) or None
					conf.addSection(name, path, desc)
				elif what == 'del':
					shares = getsections()
					if shares:
						selection = knxui.checklist(shares, size='14 60')
						for which in selection:
							conf.deleteSection(which)
					else:
						knxui.message(_("No active shares"))
				elif what == 'exit':
					break
			except KeyboardInterrupt:
				knxui.message(_('Action aborted'))
	
	o = Options()
	try:
	    	o.parseOptions()
	except knxoptions.UsageError, errortext:
		print "%s: %s" % (sys.argv[0], errortext)
		print "%s: Try --help for usage details." % (sys.argv[0])
		raise SystemExit, 1
		
	conf = SMBConf(o.opts['conf'])
	if o.args:
		action = o.args[0]
		if action == 'add':
			name = o.opts['name']
			path = o.opts['path']
			if name and path:
				conf.addSection(name,
						path,
						o.opts['comment'],
						o.opts['writeable']
				)
				conf.write(o.opts['stdout'] and sys.stdout or None)
			else:
				sys.stderr.write(_('Name and path need to be given.\n'))
				raise SystemExit, 1
		elif action == 'del':
			try:
				conf.deleteSection(o.opts['name'])
				conf.write(o.opts['stdout'] and sys.stdout or None)
			except IndexError:
				sys.stderr.write(_("No share with that name found: %r\n") % o.opts['name'])
				raise SystemExit, 1
		else:
			sys.stderr.write(_('Possible actions: add, del'))
			raise SystemExit, 1
	else:
		try:
			interactive()
			if conf.changed:
				conf.write(o.opts['stdout'] and sys.stdout or None)
				if not o.opts['stdout']:
					knxui.message(_('Configuartion updated'))
		except KeyboardInterrupt:
			raise SystemExit, 1
		
	#print conf
	#conf.deleteSection('cdrom')
	#print conf
	#conf.write(sys.stdout)
	#conf.write(file("/etc/samba/smb.conf", "w"))
	
