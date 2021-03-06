import pygame
from dronekit import connect,LocationGlobalRelative,VehicleMode,LocationGlobal,Command
import  time 
from pymavlink import mavutil
pygame.init()
win=pygame.display.set_mode((500,500))


print('Connecting to vehicle on: udp:127.0.0.1:14550 ')
vehicle = connect("udp:127.0.0.1:14550", wait_ready=True)
print("connected successfully")
gnd_speed=40


def arm_and_takeoff(aTargetAltitude):
    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)
    
def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,      
        0, 0,   
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, #(only speeds enabled)
        0, 0, 0, # x, y, z positions
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported)
        0, 0)    # yaw, yaw_rate 


    # send command to vehicle 
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)
def condition_yaw(heading, relative=False):
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    #yaw in degrees
        0,          #  yaw speed deg/s
        1,          #  direction -1 ccw, 1 cw
        is_relative, #  relative offset 1, absolute angle 0
        0, 0, 0)   
    # send command to vehicle
    vehicle.send_mavlink(msg)

    
print("control the vehicle with keyboard keys")
## keyboard inputs
def keyboard():
    while True:  
        event = pygame.event.wait()  
        if event.type == pygame.QUIT:  
            break  
   #WHEN THE KEY IS PRESSED
        if  event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  #UP ARROW=FORWARD
                    send_ned_velocity(gnd_speed,0,0,4)  
                elif event.key == pygame.K_DOWN:         #DOWN ARROW=BACKWARD                 
                    send_ned_velocity(-gnd_speed,0,0,4)  
                elif event.key == pygame.K_LEFT:          #LEFT ARROW=LEFT
                    send_ned_velocity(0,-gnd_speed,0,4)  #RIGHT ARROW=RIGHTR
                elif event.key == pygame.K_RIGHT:
                    send_ned_velocity(0,gnd_speed,0,4)  #
                elif event.key == pygame.K_SPACE:             #SPACE BAR= UP
                    send_ned_velocity(0,0,-gnd_speed,4)
                elif event.key == pygame.K_s:                  #S BUTTON= DOWN
                    send_ned_velocity(0,0,gnd_speed,4)
                elif event.key == pygame.K_a:               #A button=yaw left
                    condition_yaw(300,1)
                elif event.key == pygame.K_d:              #D button=yaw right
                    condition_yaw(60,1)
            

          

    # main function
arm_and_takeoff(50) 
keyboard()
