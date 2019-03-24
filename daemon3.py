"""
This file contains helper function to make other python scripts daemons
"""
import sys
import os


# When called the script will be come daemon and save pid to given file.
def daemonize(pid_path='/home/psimolin/runnin_pids/alert_any_tweet.pid',
              error_log=os.devnull):
    if os.path.isfile(pid_path):
        print("pid file found")
    else:
        print(pid_path)
        print("Pid file not found. Cannot fork.")
        sys.exit()
    try:
        pid = os.fork()
        if pid > 0:   # exit the parent
            sys.exit(0)
    except OSError:
        print("fork failed %s" % sys.exc_info()[0])
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:    # exit the parent
            sys.exit(0)

    except OSError:
        sys.stderr.write("fork failed %s\n" % sys.exc_info()[0])
        sys.exit(1)

    sys.stderr.write("both forks done\n")
    sys.stdout.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(error_log, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # write pid
    pid_str = str(os.getpid())
    with open(pid_path, 'w') as pid_file:
        pid_file.write("%s\n" % pid_str)

