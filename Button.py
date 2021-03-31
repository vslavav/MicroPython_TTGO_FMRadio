import utime
import machine

class button():

    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.lastValue = self.pin.value()
        self.lastTime_ms = 0
        self.bouncing_ms = 10
        self.isPressed = False
        self.isTransition_1_to_0 = False


    def poll(self):

        value = self.pin.value()
        if(value == self.lastValue):
            return

        if(value == 1):
            self.lastValue = value  
            return   
        
        if(self.isTransition_1_to_0 == False):
            self.isTransition_1_to_0 = True
            self.lastTime_ms = utime.ticks_ms()
            
            return

        if(self.isTransition_1_to_0 == True and utime.ticks_ms() - self.lastTime_ms >= self.bouncing_ms):
            self.isPressed = True
            self.lastValue = value 
            self.isTransition_1_to_0 = False
            
            


    def pressed(self):
        val = self.isPressed
        self.isPressed = False
        return val
           