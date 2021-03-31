import machine 
import network
from TEA5767 import Radio
import Button
import utime
import st7789
from uctypes import bytearray_at, addressof
import ntptime
import usocket as socket
import uselect
import FreeSans_40 as font_40
import FreeSans_30 as font_30

def connect2WiFi(display):
    essid = 'BELL810'
    password = '27452E1FF2E7'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    printScreen ( 'connecting...',display,font_30,20, 20)
    if not wlan.isconnected():
        
        wlan.connect(essid, password)
        while not wlan.isconnected():
            #pass
            utime.sleep(0.1)
            print('connecting to network...')
    print('network config:', wlan.ifconfig())  
    display.fill(st7789.BLACK)
    printScreen ( 'connected',display,font_30,20, 20)
    return wlan.ifconfig()[0]

def setLocalTime():
    try:
        ntptime.settime()
    except:
        print('ntp failed')    

def showLocalTime(display):
    
    local_time = utime.localtime()
    hour = local_time[3] - 4
    
    hour = hour + 24 if hour < 0 else hour
    tm = '{:02d}:{:02d}:{:02d} '.format(hour, local_time[4], local_time[5])
    fg = st7789.RED
    
    printScreen( tm,display, font_30,60, 80, fg)
     


def printScreen(string,display,font, col_start, row_start, fg=st7789.YELLOW, bg=st7789.BLACK):
   
    
    for char in string:
        
        glyph, char_height, char_width = font.get_ch(char) 
        buf = bytearray_at(addressof(glyph), len(glyph))
        
        buffer = bytearray(char_width*char_height*2)    
        display.map_bitarray_to_rgb565(buf, buffer, char_width, fg,bg) 
                

              
        display.blit_buffer(buffer, col_start, row_start, char_width, char_height)
        col_start += char_width  

def display_init():
    spi = machine.SPI(1, baudrate=30000000, polarity=1, phase=1,
                    sck=machine.Pin(18),
                    #miso=machine.Pin(2, machine.Pin.IN),  # NC
                    mosi=machine.Pin(19))

    display = st7789.ST7789(
            spi,
            135,
            240,
            reset=machine.Pin(23, machine.Pin.OUT),
            cs=machine.Pin(5, machine.Pin.OUT),
            dc=machine.Pin(16, machine.Pin.OUT),
            rotation=3)    

    display.init()   
    back_light = machine.Pin(4, machine.Pin.OUT)
    back_light.value(1)

    return display

            
def radio_init():
    i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
    radio = Radio(i2c) 
    return radio

def radio_setFreq(radio, freq):
    radio.set_frequency(freq)   

radio_ready = False
def radio_control(radio, display,cmd_up, cmd_down):
    global radio_ready
    if(radio_ready == False):
            radio.read()
            radio_ready = radio.is_ready
            freq = radio.frequency
            if(radio_ready):
                if(freq < 100):
                    printScreen("{:.2f}".format(freq),display,font_40, 10, 20, fg = st7789.WHITE, bg = st7789.BLACK)
                else:
                    printScreen("{:.1f}".format(freq),display, font_40, 10, 20, fg = st7789.WHITE, bg = st7789.BLACK)        
                printScreen("Mhz".format(freq),display,font_40, 120, 20, fg = st7789.WHITE, bg = st7789.BLACK)    
            print('radio ready = {}'.format(radio_ready))
        
        

    if(cmd_up is True):
        radio.search(True)
        radio.change_freqency(0.1)
        radio_ready = False
        
    if(cmd_down is True):
        radio.search(True)
        radio.change_freqency(-0.1)
        radio_ready = False


def getUdp_poll_init(ip):
    port = 4000
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip,port)) 
    poller = uselect.poll()
    poller.register(s, uselect.POLLIN)

    return s, poller

def getUdp_poll(s,poller):
    
    #print('polling ... ')
    res = poller.poll(1) # time in milliseconds
        
    if(len(res) != 0):
        data,addr=s.recvfrom(1024)
        print('received:',data,'from',addr)
        return True, data  
    else:
        return False,      



def processUdpCommand(radio, display,msg):
    command = msg.split()
    if(len(command) in [0,1]):
        return
    if(command[0].decode() == 'radio'):
        if(command[1].decode() == 'up'):
            radio_control(radio, display,True, False)
            print('radio up')
        elif (command[1].decode() == 'down'):
            radio_control(radio, display,False, True)
            print('radio down')   


def main():
    buttonL = Button.button(0)
    buttonR = Button.button(35)

    display = display_init()
    ip = connect2WiFi(display)
    utime.sleep(0.5)
    setLocalTime()
    utime.sleep(2)
    display.fill(st7789.BLACK)
    utime.sleep(2)
    radio = radio_init()

    s,poller = getUdp_poll_init(ip)
    
    

    radio_setFreq(radio, 99.1) 
    #printScreen("99.1 MHz",display, 20, 20, fg = st7789.WHITE, bg = st7789.BLACK)

    ready = False
    while(True):
        buttonL.poll()
        buttonR.poll()

        radio_control(radio, display, buttonR.pressed(), buttonL.pressed())
        showLocalTime(display)

        res = getUdp_poll(s,poller)
        if res[0] is True:
             processUdpCommand(radio, display,res[1])

        
                

        utime.sleep(0.1)

main()        
