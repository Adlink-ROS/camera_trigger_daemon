"""Generic linux daemon base class for python 3.x."""

import sys
sys.path.append(
    "/opt/adlink/neuron-sdk/neuron-library/lib/python3.6/dist-packages")
import mraa
import argparse
import signal
import atexit
import time
import os

class Camera:
    def __init__(self, hz, gpio_pin=None):
        self.hz = hz
        self.gpio_pin = gpio_pin
        self.min_fsync_interval = 0.005
        self.interval = 1 / self.hz
        self.cameras = []

    def run(self):
        # Initialize camera list
        try:
            for n in range(51, 55):  # from 51 to 54
                cam = mraa.Gpio(n)
                time.sleep(0.05)
                cam.dir(mraa.DIR_OUT)
                time.sleep(0.05)
                self.cameras.append(cam)
        except ValueError as e:
            print(e)
        
        def isr_routine(self):
            # Trigger the cameras
            for i in range(self.hz):
                t1 = time.time()
                for cam in self.cameras:
                    cam.write(1)
                time.sleep(self.min_fsync_interval)
                for cam in self.cameras:
                    cam.write(0)
                t2 = time.time()
                # Ignore the last sleep time
                if (i != self.hz-1):
                    time.sleep(self.interval - (t2 - t1))

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
                print("Trigger camera directly without ISR.")
                while True:
                    for i in range(self.hz):
                        t1 = time.time()
                        for cam in self.cameras:
                            cam.write(1)
                        time.sleep(self.min_fsync_interval)
                        for cam in self.cameras:
                            cam.write(0)
                        t2 = time.time()
                        time.sleep(self.interval - (t2 - t1))
        except ValueError as e:
            print(e)


class daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, camera, 
                 stdin='/dev/null', stdout='/home/ros/camera_trigger_daemon/daemon.log', stderr='/dev/null',):
        # daemon
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.camera = camera

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

    def run_sync(self):
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

        # Set the camera to frame Sync mode
        try:
            os.popen("echo 1 > /sys/module/leopard_ar0233/parameters/trigger_mode").readlines
            os.popen("i2cset -f -y 2 0x66 0x04 0xff").readlines
            print("Set to frame Sync mode")
        except ValueError as e:
            print(e)

        # Start the daemon
        self.daemonize()
        self.camera.run()

    def run_free(self):
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

        # Set the camera to free mode
        try:
            os.popen("echo 0 > /sys/module/leopard_ar0233/parameters/trigger_mode").readlines
            os.popen("i2cset -f -y 2 0x66 0x04 0xf0").readlines
            print("Set to free mode")
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    # Argument definition
    # ./adlink_camera_sync [mode] [-f freq] [-t gpio_num]
    # * mode:
    #   - sync:
    #     1. set frame sync mode
    #     2. enable isr if gpio_num != None
    #     3. enable trigger daemon
    #   - free:
    #     1. disable trigger daemon
    #     2. set free run mode
    # * While sync mode, supports two options
    #   -f freq: the trigger frequency (default 5 Hz)
    #   -t gpio_num: whether triggered by GPIO in

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, choices=[
                        'sync', 'free'], help='Camera trigger mode: frame sync / free run mode')
    parser.add_argument('-f', '--freq', type=int, default='5',  choices=range(1, 21), 
                        metavar="[1~20]", help='The camera trigger frequency (default 5 Hz)')
    parser.add_argument('-t', '--gpio_num', type=int, default=None,
                        required=False, help='Whether triggered by GPIO in (default None)')
    args = parser.parse_args()
    
    # set daemon : pidfile, gpio_pin(isr), hz
    hz = args.freq
    gpio_pin = args.gpio_num
    camera = Camera(hz, gpio_pin)
    MyDaemon = daemon('/tmp/daemon-example.pid', camera)

    if 'sync' == args.mode:
        MyDaemon.run_sync()
    elif 'free' == args.mode:
        MyDaemon.run_free()
    sys.exit(0)   