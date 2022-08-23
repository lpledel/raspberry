import network
from machine import Pin
from time import sleep, sleep_ms, time
import umail
from temperature import sensor


class CustomError(Exception):
    pass


class Wifi:
    def __init__(self):
        self.net = 'hby_2G'
        self.pwd = 'verololo'
        self.wifi = network.WLAN(network.STA_IF)
        self.status = 0

    def on(self):
        self.wifi.active(True)
        self.wifi.connect(self.net, self.pwd)
        for loop in range(10):
            if self.wifi.status() <= 0:
                ledRed.led_error()
                break
            else:
                if self.wifi.isconnected():
                    ledGreen.led_success()
                    break
            ledGreen.led_waiting_or_alive()
            sleep(2)

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
    def __init__(self):
        self.sender = 'xxx@free.fr'
        self.receiver = 'xxxxx@gmail.com'
        self.pwd = "xxxxx"
        self.serveur = 'smtp.free.fr'
        self.port = 465
        self.subject = ""
        self.message = ""
        self.free = None
        self.msg = ""
        # status à 1 si problème lors de l'envoi du mail
        self.status = 0

    def send_mail(self, subject, message):
        # msg="From: xxxxx@free.fr\r\n"+"To: xxxxxx@gmail.com\r\n"+"subject: problèmes pompes\r\n\r\n"
        self.message = message
        self.subject = subject
        try:
            mywifi.on()
            if mywifi.wifi.status() != 3:
                raise CustomError
        except (OSError, AssertionError, CustomError):
            print("problème wifi le code de retour est: ", mywifi.wifi.status())
            self.status = 1
        else:
            print("wifi ok")
            try:
                self.msg = 'From: {}\r\n'.format(self.sender) + 'To: {}\r\n'.format(self.receiver) + 'subject:{}\r\n\r\n'.format(self.subject) + '{}'.format(self.message)
                smtp = umail.SMTP(self.serveur, self.port, username=self.sender, ssl=True, password=self.pwd)
                smtp.to(self.receiver)
                self.free = smtp.send(self.msg)
                smtp.quit()
                if self.free[0] != 250:
                    raise CustomError

            except (OSError, AssertionError, CustomError) as e:
                print("problème lors de l'envoi du mail chez smtp.free.fr", self.free, e)
                self.status = 1
            else:
                print("envoi du mail ok", self.free)
                self.status = 0
        finally:
            mywifi.disconnect()


class Led:
    def __init__(self, led_id):
        if led_id == "Green":
            Pin(20, Pin.IN, Pin.PULL_DOWN)
            self.led = Pin(21, Pin.OUT)
        if led_id == "Red":
            Pin(11, Pin.IN, Pin.PULL_DOWN)
            self.led = Pin(10, Pin.OUT)

    def led_success(self):
        # en cas de succès lors d'une fonction essentielle, activation wifi, envoi d'email..
        self.led.value(1)
        sleep(3)
        self.led.off()

    def led_waiting_or_alive(self):
        # utiliser quand une operation est en cours, activation du wifi ou boucle de test du flotteur
        # lettre  "."
        reference = 10
        self.led.value(1)
        sleep_ms(reference)
        self.led.value(0)
        sleep_ms(reference)

    def led_error(self):
        # erreur empechant de communiquer , impossible d'activer le wifi, error à l'envoi de mail,panne de courant, flotteur bloqué
        self.led.value(1)
        sleep(0.1)
        self.led.value(0)
        sleep(1)


# initialisation des objets
ledGreen = Led("Green")
ledRed = Led("Red")
mywifi = Wifi()
mailpompe = Mail()
myflotteur = Flotteur()
# et des variables
# si mail_sent >0 alors le dernier mail envoyé est un mail d'erreur
mail_sent = 0
# flag >0 si une error wifi ou serveur de mail a été rencontré dans la boucle while
flag_error = 0
# offset qui sert à calculer le temps écoulé depuis le dernier boot
boot_timestamps = time()
count_boucle = 0

# check du wifi et check du serveur de courrier au demarrage par l'envoi d'un mail
print("check du wifi et check du serveur de courrier")
mailpompe.send_mail("check wifi et serveur de courrier ", (time()-boot_timestamps)/86400)
mywifi.disconnect()
# check de la position du flotteur
while True:
    # check de la position du flotteur
    count_boucle += 1
    myflotteur.position()
    print("check du flotteur")
    if myflotteur.pos_flot == 1:
        # le flotteur est en défaut
        print("flotteur en défaut")
        # le mail d'alerte est envoyé sur les 3 premières iteration while au cas ou un ou deux mails se perdent...
        if mail_sent < 3:
            mailpompe.send_mail("flotteur en defaut", "timestamps{}".format((time()-boot_timestamps)/86400))
        mail_sent += 1
    else:
        # le flotteur est ok
        print("flotteur ok")
        # on envoi un mail de retour à la normal uniquement si le flotteur etait en defaut
        if mail_sent > 0:
            mailpompe.send_mail("flotteur ok", "timestamps{}".format((time()-boot_timestamps)/86400))
            mail_sent = 0
    flag_error = mail_sent + mailpompe.status
    print(mail_sent, mailpompe.status)
    # si des mails flotteur en defaut sont en cours  ou si problème de wifi ou serveur de mail la led rouge  s'anime
    if flag_error > 0:
        for i in range(1, 10):
            ledRed.led_error()
    else:
        sleep(1)
    # envoi d'un message de vie environ toute les 24h soit 7854 boucles
    if count_boucle > 7854:
        mailpompe.send_mail("message de vie", "nombre de boucles de test :{}, time since boot (days){}, temp ={}".format(count_boucle, (time()-boot_timestamps)/86400, sensor()))
        count_boucle = 0
