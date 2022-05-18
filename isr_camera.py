"""Generic linux daemon base class for python 3.x."""

import sys
sys.path.append("/opt/adlink/neuron-sdk/neuron-library/lib/python3.6/dist-packages")
import mraa
import os
import time
import atexit
import signal

class Camera:
    def __init__(self, hz, gpio_pin = None):
        self.hz = hz
        self.gpio_pin = gpio_pin
        # TODO: Suggest to add comment here for how to get this number
        self.interval = (1-self.min_fsync_interval*3)/self.hz
        self.wait_idle = self.interval - self.min_fsync_interval
        # Initialize camera list
        self.cameras = []
        try:
            for n in range(51, 55): # from 51 to 54
                cam = mraa.Gpio(n)
                time.sleep(0.05)
                cam.dir(mraa.DIR_OUT)
                time.sleep(0.05)
                self.cameras.append(cam)
        except ValueError as e:
            print(e)

    def run(self):

        def isr_routine(self):
            # trigger the cameras
            for i in range(self.hz - 1):
                for cam in self.cameras:
                    self.cam.write(1)
                time.sleep(self.min_fsync_interval)
                for cam in self.cameras:
                    self.cam.write(0)
                time.sleep(self.wait_idle)
            for cam in self.cameras:
                self.cam.write(1)
            time.sleep(self.min_fsync_interval)
            for cam in self.cameras:
                self.cam.write(0)

        try:
            # Receive GPIO in and trigger camera
            if (self.gpio_pin != None):
                # Receive GPIO in interrupte
                self.gpio = mraa.Gpio(self.gpio_pin)
                time.sleep(0.05)
                self.gpio.dir(mraa.DIR_IN)
                time.sleep(0.05)
                self.gpio.isr(mraa.EDGE_RISING, isr_routine, self)
                time.sleep(0.05)

                print("Starting ISR for pin " + repr(self.gpio.getPin(True)))

                while True:
                    """waitting for isr."""
                    time.sleep(0.05)
            # Trigger camera directly
            else:
                while True:
                    for i in range(self.hz):
                        for cam in self.cameras:
                            self.cam.write(1)
                        time.sleep(self.min_fsync_interval)
                        for cam in self.cameras:
                            self.cam.write(0)
                        time.sleep(self.wait_idle)
        except ValueError as e:
            print(e)


class daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, gpio_pin, hz,
                 stdin='/dev/null', stdout='/home/ros/camera_trigger_daemon/daemon.log', stderr='/dev/null',):
        # daemon
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

    def delpid(self):
        os.remove(self.pidfile)

    def start(self, camera):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile {0} already exist. " + \
                "Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        camera.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist. " + \
                "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""

        self.stop()
        self.start()


if __name__ == "__main__":
    # TODO: Argument definition
    # ./adlink_camera_sync [mode] [-f freq] [-t gpio_num]
    # * mode:
    #   - sync:
    #     1. set frame sync mode
    #     2. enable isr daemon
    #   - free:
    #     1. disable isr daemon
    #     2. set free run mode
    # * While sync mode, supports two options
    #   -f freq: the trigger frequency (default 5 Hz)
    #   -t gpio_num: whether triggered by GPIO in

    # TODO: suggest to use Python model argparse to handle the argument
    hz = 5 if len(sys.argv) < 3 else int(sys.argv[2])
    gpio_pin = None if len(sys.argv) < 4 else int(sys.argv[3])

    # set daemon : pidfile, gpio_pin(isr), hz
    MyDaemon = daemon('/tmp/daemon-example.pid', gpio_pin, hz)

    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            camera = Camera(hz, gpio_pin)
            MyDaemon.start(camera)
        elif 'stop' == sys.argv[1]:
            MyDaemon.stop()
        elif 'restart' == sys.argv[1]:
            MyDaemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
        