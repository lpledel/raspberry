import network
from machine import Pin
from time import sleep, sleep_ms
import umail
from raspberry.main import CustomError, mywifi


class wifi:
    def __int__(self):
        self.net = 'hby2g'
        self.pwd = 'verololo'
        self.wifi = network.WLAN(network.STA_IF)
        self.status = 0

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

    def disconnect(self):
        # deconnecte du réseau et arrete l'interface wifi
        self.wifi.disconnect()  # deconnecte du reseau
        self.wifi.active(False)  # desactive le wifi
        return

    def scan(self):
        return self.wifi.scan()


class Flotteur:

    def __init__(self):
        # initialisation de l'objet flotteur
        self.alim_flot = Pin(0, Pin.OUT)
        self.flot = Pin(1, Pin.IN, Pin.PULL_DOWN)
        self.pos_flot = 0

    def position(self):
        self.alim_flot.value(1)
        sleep(1)
        self.pos_flot = self.flot.value()
        self.alim_flot.value(0)


class Mail:
    class Mail:
        sender = 'lpledel@free.fr'
        receiver = 'vlpledel@gmail.com'
        pwd = "42719290"
        serveur = 'smtp.free.fr'
        port = 465

        def __init__(self):
            self.nb_mail_send_ok = 0
            self.nb_mail_send_ko = 0
            self.subject = ""
            self.message = ""

        def send_mail(self, subject, message):
            # msg="From: lpledel@free.fr\r\n"+"To: vlpledel@gmail.com\r\n"+"subject: problèmes pompes\r\n\r\n"
            self.message = message
            self.subject = subject
            try:
                mywifi.on()
                if mywifi.wifi.status() != 3:
                    raise CustomError
            except CustomError:
                print("problème wifi")
            else:
                msg = 'From: {}\r\n'.format(self.sender) + 'To: {}\r\n'.format(
                    self.receiver) + 'subject:{}\r\n\r\n'.format(
                    self.subject) + '{}'.format(self.message)
                smtp = umail.SMTP(self.serveur, self.port, username=self.sender, ssl=True, password=self.pwd)
                smtp.to(self.receiver)
                smtp.send(msg)
                smtp.quit()
                if self.subject == "fin problème pompes":
                    self.nb_mail_send_ko = 0
                    self.nb_mail_send_ok += 1
                if self.subject == "début problème pompes":
                    self.nb_mail_send_ok = 0
                    self.nb_mail_send_ko += 1
                print(self.nb_mail_send_ko, self.nb_mail_send_ok)

            finally:
                mywifi.disconnect()


class Led:
    def __init__(self, led_id):
        if led_id == "Green":
            self.led = Pin("LED", Pin.OUT)
        if led_id == "Red":
            Pin(3, Pin.IN, Pin.PULL_DOWN)
            self.led = Pin(2, Pin.OUT)

    def led_success(self):
        # en cas de succès lors d'une fonction essentielle, activation wifi, envoi d'email..
        print('led success')
        self.led.on()
        sleep(3)
        self.led.off()

    def led_waiting_or_alive(self):
        # utiliser quand une operation est en cours, activation du wifi ou boucle de test du flotteur
        # lettre  "."
        reference = 5
        print('led waiting')
        self.led.on()
        sleep_ms(reference)
        self.led.off()
        sleep_ms(reference)

    def led_error(self):
        # erreur empechant de communiquer , impossible d'activer le wifi, error à l'envoi de mail,panne de courant, flotteur bloqué
        self.led.value(1)
        sleep(1)
        self.led.value(0)
        sleep(1)
