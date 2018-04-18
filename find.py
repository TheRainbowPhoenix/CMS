import platform
import os
import subprocess

message = "Hello i am an important message\n"
home = ''

#print subprocess.call(["echo","message",">","{}".format(i),"2>","/dev/null"])
#echo "lol" > /dev/tty 2> /dev/null

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# print which("zenity")

def TTY_Send(msg):
	dev = subprocess.check_output(["ls","/dev/"])
	ttys = [i for i in dev.split() if i[:3]=="tty"]
	for i in ttys:
		try:
			f = open("/dev/{}".format(i), 'wb')
			f.write(msg)
			f.close()
		except:
			continue

def BASH_Exec(file):
	if platform.system()=='Linux':
		if (which("bash") != None):
			outp = subprocess.check_output(["bash","{}".format(file)])
		else :
			if platform.machine()=='x86_64':
				outp = subprocess.check_output(["./bin/busybox-amd64","sh","{}".format(file)])
			elif platform.machine()=='i386':
				outp = subprocess.check_output(["./bin/busybox-i386","sh","{}".format(file)])
			elif platform.machine()=='i486':
				outp = subprocess.check_output(["./bin/busybox-i486","sh","{}".format(file)])
			elif platform.machine()=='i586':
				outp = subprocess.check_output(["./bin/busybox-i586","sh","{}".format(file)])
			elif platform.machine()=='i686':
				outp = subprocess.check_output(["./bin/busybox-i686","sh","{}".format(file)])
			elif platform.machine()=='armv4l':
				outp = subprocess.check_output(["./bin/busybox-armv4l","sh","{}".format(file)])
			elif platform.machine()=='armv4tl':
				outp = subprocess.check_output(["./bin/busybox-armv4tl","sh","{}".format(file)])
			elif platform.machine()=='armv5l':
				outp = subprocess.check_output(["./bin/busybox-armv5l","sh","{}".format(file)])
			elif platform.machine()=='armv6l':
				outp = subprocess.check_output(["./bin/busybox-armv6l","sh","{}".format(file)])
			elif platform.machine()=='armv7l':
				outp = subprocess.check_output(["./bin/busybox-armv7l","sh","{}".format(file)])
			elif platform.machine()=='m68k':
				outp = subprocess.check_output(["./bin/busybox-m68k","sh","{}".format(file)])
			elif platform.machine()=='mips':
				outp = subprocess.check_output(["./bin/busybox-mips","sh","{}".format(file)])
			elif platform.machine()=='mips64':
				outp = subprocess.check_output(["./bin/busybox-mips64","sh","{}".format(file)])
			elif platform.machine()=='mipel':
				outp = subprocess.check_output(["./bin/busybox-mipsel","sh","{}".format(file)])
			elif platform.machine()=='ppc':
				outp = subprocess.check_output(["./bin/busybox-powerpc","sh","{}".format(file)])
			elif platform.machine()=='powerpcle':
				outp = subprocess.check_output(["./bin/busybox-powerpc-440fp","sh","{}".format(file)])
			elif platform.machine()=='sh64':
				outp = subprocess.check_output(["./bin/busybox-sh4","sh","{}".format(file)])
			elif platform.machine()=='sparc':
				outp = subprocess.check_output(["./bin/busybox-sparc","sh","{}".format(file)])
			elif platform.machine()=='aarch64':
				outp = subprocess.check_output(["./bin/busybox-arm64","sh","{}".format(file)])
			else:
				outp = ''	
	elif platform.system()=='Windows':
		if platform.machine() == 'AMD64':
			outp = subprocess.check_output(['bin\\busybox64.exe','sh','{}'.format(file)], shell=True)
		else:
			outp = subprocess.check_output(['bin\\busybox.exe','sh','{}'.format(file)], shell=True)
	return '{}'.format(outp.decode("utf-8"))

def CON_Form(msg, title="System", type=0, width=80, height=4, nowrap=False, clear=False, dialog=True, bell=True):
	out = '\n'
	if clear:
		out += '\033[H\033[2J'
	if bell:
		out += '\07'
	if type == 1:
		out += '\033[43m' # yellow
	elif type == 2:
		out += '\033[41m' # red
	else:
		out += '\033[46m' # cyan
	if dialog:
		for i in xrange(width):
			out += " "
		out += '\n'
	if title == '':
		title = "System"
	out += ' {} '.format(title)
	if dialog:
		for i in xrange(len(title)+2, width):
			out += " "
		out += '\n'
		for i in xrange(width):
			out += " "
		out += '\n'
		out += '\033[7m' # dialog body
		for i in xrange(width):
			out += " "
		out += '\n'
		for i in msg.split('\\n'):
			splt = [ i[j:j+width-2] for j in range(0, len(i), width-2)]
			for k in splt:
				out += ' {}'.format(k.rstrip())
				for i in xrange(len(k.rstrip())+1, width):
					out += " "
				out += '\n'
		for i in xrange(width):
			out += " "
		out += '\n'
		out += '\033[m'
		out += '\n'
	else:
		out += '\033[m'
		out += ' : \033[7m' 
		out += msg
		out += '\033[m'
		out += '\n'
	return out
	
def ZEN_Send(msg, title="System", type=0, width=0, height=0, nowrap=False):
	zarg = ''
	if type == 1:
		zarg += '--warning '
	elif type == 2:
		zarg += '--error '
	else:
		zarg += '--info '
	if title != '':
		zarg += '--title="{}" '.format(title)
	else:
		zarg += '--title="{}" '.format("System")
	if nowrap:
		zarg += '--no-wrap '	
	if width != 0:
		zarg += '--width={} '.format(width)
	if height != 0:
		zarg += '--height={} '.format(height)
	if msg != '':
		zarg += '--text="{}" '.format(msg)
	else:
		zarg += '--text="{}" '.format("Missingno")
		
	print(zarg)
		
	if platform.system()=='Linux':
		if 'DISPLAY' in os.environ:
			try:
				xset = subprocess.check_output(["xset","q"])
			except:
				xset = ''
			if xset == '':
				print("No X Server started ...")
				TTY_Send(CON_Form(msg, title, type))
			else:
				if (which("zenity") != None):
					home = ''
					subprocess.call(['zenity {}'.format(zarg)], shell=True)
				else:
					if platform.machine()=='x86_64':
						subprocess.call(['./bin/zenity-amd64 {}'.format(zarg)], shell=True)
					elif platform.machine()=='i386':
						subprocess.call(['./bin/zenity-i386 {}'.format(zarg)], shell=True)
					else:
						print("Intall zenity ...")
						TTY_Send(CON_Form(msg, title, type))
		else:
			TTY_Send(CON_Form(msg, title, type))

	elif platform.system()=='Windows':
		exe = ['bin\zenity.exe']
		exe.extend(["--"+i.replace('"','').rstrip() for i in zarg.split("--")[1:]])
		subprocess.call(exe, shell=True)
	else:
		TTY_Send(message)
	
def GET_Home():
	return BASH_Exec("./home.sh").rstrip()


print(GET_Home())

ZEN_Send(message)
ZEN_Send("CPU Surcharge", title="CPU Error", type=2)
ZEN_Send(message, title="System Notifier : Read Me", type=1)
message = "<big><b>Some message: Im angry. Trust me</b></big> \n Or not...".replace("\n","\\n")
ZEN_Send(message, title="..:: System Notifier : Read Me ::..", type=1, width=512, height=256, nowrap=True)

