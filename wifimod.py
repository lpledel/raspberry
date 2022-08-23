import network
import led_indicator as led
import time

class wifi:
    def __int__(self):
        self.net = 'hby2g'
        self.pwd = 'verololo'
        self.wifi = network.WLAN(network.STA_IF)
    def on(self):
        self.wifi.active(True)
        self.wifi.connect(self.net, self.pwd)
        for loop in range(10):
            if self.wifi.status() <= 0:
                led.led_failed()
                break
            else:
                if self.wifi.isconnected():
                    led.led_success()
                    break
            led.led_waiting_or_alive()
            time.sleep(2)
    def status(self):
        # True or False, si 1,2 en cours de connexion si 3 ok si <0 problème,true/false
        return self.wifi.isconnected(), self.wifi.status(),self.wifi.active()

    def disconnect(self):
        #deconnecte du réseau et arrete l'interface wifi
        self.wifi.disconnect() # deconnecte du reseau
        self.wifi.active(False) #desactive le wifi
        return

    def scan(self):
        return self.wifi.scan()

