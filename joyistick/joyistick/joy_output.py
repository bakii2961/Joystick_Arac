from pydoc import cli
from paho.mqtt import client as mqtt
from std_msgs.msg import Bool, Float32, Int8
from dolasim_msgs.msg import IcVeriDolasim
import json , os, sys, rclpy, time 
from rclpy.node import Node
from threading import Thread

class esp_output(Thread):
    def __init__(self, logger=print):
        Thread.__init__(self)
        self.logger = logger
        self.direksiyon = 0
        self.fren = 0
        self.gaz = 0
        self.guc=0

        self.el_freni = False

        self.broker_ip = "192.168.0.157"
        self.broker_port = 1883
        self.id = "joyOutput_mqtt"

        self.client = self.connect_mqtt()

        self.flag = True
        self.logger = logger
       

    def connect_mqtt(self):
        client = mqtt.Client(self.id+"1")
        client.on_connect = self.on_connect
        client.connect_async(self.broker_ip, self.broker_port)
        client.on_disconnect= client.reconnect
        client.loop_start()
        return client
        
    def on_connect(self, client, userdata,  rc, flag):
        if rc == 0:
           self.logger("mqtt -> connected to broker on" + self.broker_ip + ":" + self.broker_port)
        
        else:
           self.logger("mqtt -> broker connection failed: " + str(rc))

    def pub(self, topic, data):
        res = self.client.publish(topic, data, qos=0)
        if res[0] != 0:
           self.logger("problem on publishing " + str(topic) + ", error code:")
           for r in res:
               self.logger(str(r))

    def run(self):
        while self.flag:
            self.pub("direksiyon2" , str(self.direksiyon * 550))
            self.pub("gaz" ,str(self.gaz ))
            self.pub("fren",  str(self.fren))
            self.pub("guc", str(int(self.guc)))
            #self.client.loop_write()
            #self.client.loop_misc()
            time.sleep(0.033)
            self.logger("output is send")

    def __del__(self):
        self.client.loop_stop()

#class joyOutput_mqtt(Node):

class joyOutput_mqtt(Node):
    def __init__(self):
        super().__init__('joy_output')
        self.sub1 = self.create_subscription(IcVeriDolasim, "/input/main", self.get_main_data, 10)
        
        self.direksiyon = 0
        self.gaz = 0
        self.fren = 0
        self.anlik_hiz = 0
        self.hedef_hiz = 0
        self.guc = 0
        self.serit_secim = 0
        self.guc = True
        self.el_freni = False

        self.joy_hz = 0
        self.velocity_input_hz = 0
        self.io_output_hz = 0

        self.mqtt = esp_output(self.get_logger().info)
        self.mqtt.start()

        self.get_logger().info("mqtt -> ros is ok, starting mqtt")

    def get_main_data(self, data):
        self.direksiyon = data.direksiyon
        self.gaz = data.gaz
        self.fren = data.fren
        self.hedef_hiz = data.hedef_hiz
        self.anlik_hiz = data.anlik_hiz
        self.guc = data.guc
        self.el_freni = data.el_freni

    def output(self):
        self.mqtt.direksiyon = self.direksiyon
        self.mqtt.gaz = self.gaz
        self.mqtt.fren = self.fren
        self.mqtt.guc=self.guc     
def main(args=None):
    rclpy.init(args=args)
    joy_output= joyOutput_mqtt()
    rate = joy_output.create_rate(15)
    while rclpy.ok():
        try:
            rclpy.spin_once(joy_output)
            joy_output.output()
        except KeyboardInterrupt:
            print("Bye Bye!")
            joy_output.mqtt.flag = False

    rclpy.shutdown() 

if __name__ == "__main__":
    main(args)
