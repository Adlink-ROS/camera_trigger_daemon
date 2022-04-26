# Goal

利用670/680的GNSS模組 > 1PPS > trigger camera (or LiDAR and IMU)

取得PPS的timestamp與相機 trigger timestamp做比較

PPS’s Timestamp according to UTS with GPS

ROScube’s system time accoring to UTS with NTP (need Internet to correction)

# Method

MTi 670/680 with GNSS ⇒  Send 1 PPS

ROS with mraa ⇒ GPIO ⇒ Trigger ISR + Camera

ROS with mraa ⇒ Uart ⇒ Read Timestamp ⇒ Set board rate to 15200 

## Installation Mraa

```bash
sudo add-apt-repository ppa:mraa/mraa
sudo apt-get update
sudo apt-get install libmraa2 libmraa-dev libmraa-java 
sudo apt-get install python-mraa python3-mraa node-mraa mraa-tools
```

# Test

## Timestamp test

GNSS ⇒ Uart ⇒ time.time() different

1. Uart read ⇒ OK
2. PPS + Uart
3. String split() Method ⇒ timestamp

# Next step

- msg queue
    
    **目前作法** : 
    
    PPS ⇒ ISR ⇒ timestamp append to list & trigger cameras
    
    list > timestamp.txt (10 points)
    
    **目標** :
    
    利用MQ架構(RabbitMQ) > send the timestamp list >call API ⇒ get timestamp
    

# Reference

[产品文档 : Apex Xavier 用户手册](http://doc.miivii.com/5964246.html#ApexXavier%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C-%E4%BD%BF%E7%94%A8%E8%A7%86%E9%A2%91)