# camera_trigger_daemon

## Method

MTi 670/680 with GNSS ⇒  Send 1 PPS

ROS with mraa ⇒ GPIO ⇒ Trigger ISR + Camera

ROS with mraa ⇒ Uart ⇒ Read Timestamp ⇒ Set board rate to 15200
