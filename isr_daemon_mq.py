"""Generic linux daemon base class for python 3.x."""

import sys
import os
import time
import atexit
import signal
import mraa
import pika


class daemon:
    """A generic daemon class.
    
    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, gpio_pin, uart_port, led_num,
                 stdin='/dev/null', stdout='/home/ros/camera_trigger_daemon/test.txt', stderr='/dev/null',):
        # daemon
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

        # mraa
        self.gpio = gpio_pin
        self.led = led_num
        self.uart = uart_port
        self.data = ""
        self.tmp = []
        self.tmp2 = ""
        self.count = 0

        # trigger time
        self.hz = 10*3
        self.min_fsync_interval = 0.005
        self.interval = (1-self.min_fsync_interval*3)/self.hz
        self.wait_idle = self.interval - self.min_fsync_interval

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

    def start(self):
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
        self.run()

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

    def message_queue(self):
        """Creat a message queue."""

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        # 宣告一個名為 'timestamp' 的訊息佇列
        self.channel.queue_declare(queue='timestamp')

    def send(self):
        """Send the message to queue."""

        self.channel.basic_publish(
            exchange='', routing_key='timestamp', body=self.data)

    def receive(self):
        """Receive the message form quese."""

        def callback(ch, method, properties, body):
            print(f" [x] Received {body}")
            # 每次成功 cossume 都會 popout
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(
            'timestamp', callback)  # 宣告消費來自 timestamp 的訊息
        self.channel.start_consuming()

    def timestamp(self):
        """Start get the timestamp form quees."""

        self.message_queue()
        self.receive()

    def uart_timestamp(self):
        """Read timestamp from uart and setting system time"""

        # flush uart inbound
        self.tmp = self.uart.readStr(10000)

        # receive the GNSS data from uart
        while not self.uart.dataAvailable():
            time.sleep(0.005)
        self.tmp = self.uart.readStr(10000).split("\n")[1].split(",")[1]

        # setting system time by timedatectl set-time "18:10:40"
        os.popen("timedatectl set-ntp false").readlines
        os.popen("timedatectl set-time " + self.tmp[0] + self.tmp[1] + ":" +
                 self.tmp[2] + self.tmp[3] + ":" + self.tmp[4] + self.tmp[5]).readlines()

    def run(self):

        def isr_routine(self):
            """Tigger LED and save timestamp."""

            # self.ti=time.time()
            # get the current system time
            self.tmp2 = time.ctime()
            self.count += 1

            # trigger the led on/off
            for i in range(self.hz - 1):
                self.led.setBrightness(1)
                time.sleep(self.min_fsync_interval)
                self.led.setBrightness(0)
                time.sleep(self.wait_idle)
            self.led.setBrightness(1)
            time.sleep(self.min_fsync_interval)
            self.led.setBrightness(0)
            # self.to=time.time()
            # print(self.to-self.ti)

        try:
            # initialise GPIO
            self.gpio = mraa.Gpio(self.gpio)
            time.sleep(0.05)
            # set direction and edge types for interrupt
            self.gpio.dir(mraa.DIR_IN)
            time.sleep(0.05)
            self.gpio.isr(mraa.EDGE_RISING, isr_routine, self)
            time.sleep(0.05)

            # initialise LED
            self.led = mraa.Led(self.led)
            time.sleep(0.05)

            # initialise UART
            self.uart = mraa.Uart(self.uart)
            time.sleep(0.05)
            # set UART parameters
            self.uart.setBaudRate(115200)
            time.sleep(0.05)
            self.uart.setMode(8, mraa.UART_PARITY_NONE, 1)
            time.sleep(0.05)
            self.uart.setFlowcontrol(False, False)
            time.sleep(0.05)

            print("Starting ISR for pin " + repr(self.gpio.getPin(True)))

            # initialise message queue
            self.message_queue()

            # setting systeam time
            self.uart_timestamp()

            while True:
                """Waitting for isr."""

                # flush uart inbound
                self.tmp = self.uart.readStr(10000)
                time.sleep(0.05)

                # correction systeam time every 10 second.
                if self.count == 10:
                    self.uart_timestamp()
                    self.count = 0

                # send the timestamp
                if self.tmp2 != self.data:
                    self.data = self.tmp2
                    self.send()

        except ValueError as e:
            print(e)

if __name__ == "__main__":

    # set daemon : pidfile, gpio_pin(isr), uart_port, led_num
    MyDaemon = daemon('/tmp/daemon-example.pid', 5, '/dev/ttyUSB0', 0)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            MyDaemon.start()
        elif 'stop' == sys.argv[1]:
            MyDaemon.stop()
        elif 'restart' == sys.argv[1]:
            MyDaemon.restart()
        elif 'timestamp' == sys.argv[1]:
            MyDaemon.timestamp()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|timestamp" % sys.argv[0])
        sys.exit(2)
