from paho.mqtt import client as mqtt
from sensor_msgs.msg import  Joy
from std_msgs.msg import Float32, Int8, Bool
from dolasim_msgs.msg import IcVeriDolasim
from rclpy.node import Node
from std_msgs.msg import Header
import rclpy, time 
import threading

axes = {"direksiyon" : 0, "gaz-fren" : 3   , "sag-sol": 4, "ileri": 5}
buttons = {"ileri": 3, "geri": 1, "el-freni": 2, "guc": 0}

class joystick(Node):
    def __init__(self): 
        super().__init__('joy_input')
        self.sub7 = self.create_subscription(Joy, "/joy", self.get_joy_input, 10)

        self.pub1 = self.create_publisher(IcVeriDolasim, "/input/main", 10)

        self.guc_enabled = True
        self.el_freni = False
        self.serit_secim = 0
        self.hedef_hiz = 0
        self.joy_enable = True
        
        self.direksiyon = 0.0
        self.gaz = 0.0  
        self.fren = 0.0
        self.vites = 1
       # self.get_logger().info("mqtt -> ros is ok, starting mqtt")

        self.broker_ip = "192.168.0.157"
        self.broker_port = 1883
        self.id = "joyOutput_mqtt"
        self.client = self.connect_mqtt()
        # self.client=threading.Thread(target=self.connect_mqtt)
        # self.client.start()
        # self.get_logger().info("mqtt basarili")

    def get_joy_input(self, data):
        self.direksiyon = data.axes[axes["direksiyon"]]
        self.get_logger().info("joy_in_drk" + (str(self.direksiyon)))
        
        
        #self.el_freni= data.buttons[buttons["el-freni"]]
        #self.get_logger().info("fren" + str(self.el_freni))

        self.gaz= -data.axes[axes["gaz-fren"]]
        self.get_logger().info("gaz-fren" + str(self.gaz))

        self.guc=data.buttons[buttons["guc"]]
        self.get_logger().info("guc"+str(self.guc))

        if data.axes[axes["gaz-fren"]] >= 0:
            self.fren = 0.0
            self.gaz = data.axes[axes["gaz-fren"]]

        else:
            self.gaz = 0.0
            self.fren = -data.axes[axes["gaz-fren"]]
        
        if data.axes[axes["sag-sol"]] > 0:
            self.serit_secim = 2
        
        elif data.axes[axes["sag-sol"]] < 0:
            self.serit_secim = 1

        if data.axes[axes["ileri"]] > 0:
            self.serit_secim = 0

        if data.buttons[buttons["ileri"]]:
            self.vites = 1

        elif data.buttons[buttons["geri"]]:
            self.vites = 2

        elif data.buttons[buttons["guc"]]:
            if self.guc_enabled:    
                self.guc_enabled = False
            else:
                self.guc_enabled = True

        elif data.buttons[buttons["el-freni"]]:
            if self.el_freni:
                self.el_freni = False
	
            else:
                self.el_freni = True

    def get_hedef_hiz(self, data):
        self.hedef_hiz = data.data    

    def check_cruise_control(self):
        if self.hedef_hiz > 0 and self.fren == 0.0:
            self.pid.setpoint = self.hedef_hiz
            out = self.pid(self.vel_data.velocity)
            if out >= 0:
                gaz, fren = (float(out / 10), 0.0)
            else:
                gaz, fren = (0.0, float(out / -10))
            return (gaz, fren)
        
        else:
            self.pid.setpoint = 0
            out = self.pid(self.vel_data.velocity)
            if out >= 0:
                gaz, fren = (float(out / 10), 0.0)
            else:
                gaz, fren = (0.0, float(out / -10))
            return (gaz, fren)
    
    def output(self):
        self.out = IcVeriDolasim()

        self.out.serit_secim = self.serit_secim
        self.out.vites = self.vites

        self.out.direksiyon = self.direksiyon
        if not self.joy_enable:
            self.out.gaz, self.out.fren = self.check_cruise_control()
        else:
            self.out.gaz, self.out.fren = self.gaz, self.fren
        self.out.anlik_hiz = 2.5

        self.out.guc = self.guc_enabled
        self.out.el_freni = self.el_freni

        self.pub1.publish(self.out)    

    def connect_mqtt(self):
        client = mqtt.Client(self.id)
        client.on_connect = self.on_connect
        client.connect(self.broker_ip, self.broker_port)
        client.loop_start()
        return client
        
    def on_connect(self, client, userdata,  rc, flag):
        if rc == 0:
            self.get_logger().info("mqtt -> connected to broker on" + self.broker_ip + ":" + self.broker_port)
        
        else:
            self.get_logger().info("mqtt -> broker connection failed: " + str(rc))


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# client.connect("localhost", 1883)

# client.loop_forever() #kodu burda bekletir

def main(args=None):
    rclpy.init(args=args)
    joy_input = joystick()
    rate = joy_input.create_rate(30)
    while rclpy.ok():
        try:
            rclpy.spin_once(joy_input)
            joy_input.output()
        except KeyboardInterrupt:
            print("gule gule")
            joy_input.client.loop_stop()

    rclpy.shutdown()

if __name__ == "__main__":
    main(args)