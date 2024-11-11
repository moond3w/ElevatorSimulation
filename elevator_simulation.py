# A fun little project to simulate an elevator system through the use of multithreading in python
# ===============================================================================================
# Context:  Two elevators will be operational in the simulation, and they will mimic a real-life
#           elevator through the following:
#           1. Both elevators will listen for input (Up/Down) from any floors (1-20)
#           2. The nearest elevator will respond unless occupied (i.e. Going in other direction)
#           3. If not in use, both elevators will be at rest in floor 1 / 10 (Mid-way)
# ===============================================================================================
# Version #1 : Simulating the process with a single elevator (ele_A)

import threading
import time
import queue
from enum import Enum

class Elevator:
    def __init__ (self, id, capacity, floor):
        self.id = id # Can consider setting auto name
        self.capacity = capacity
        self.current_capacity = 0
        self.status = Status.REST
        self.floor = floor
        self.current_floor = 1

    def set_capacity(self, capacity):
        self.capacity = capacity
    
    def set_current_capacity(self, current_capacity):
        self.current_capacity = current_capacity

    # Takes in a string, and converts into Status
    def set_status(self, status):
        match(status):
            case "UP":
                self.status = Status.UP
            case "DOWN":
                self.status = Status.DOWN
            case "REST":
                self.status = Status.REST
            case "MAINTENANCE":
                self.status = Status.MAINTENANCE
            case _:
                print ("Unexpected Error in set_status")
                print ("Input data:", str(status))
    
    def set_floor(self, floor):
        self.floor = floor
    
    def set_current_floor(self, current_floor):
        self.current_floor = current_floor

    def move_up(self):
        self.current_floor += 1
        # Temporarily show status each time elevator moves
        self.show_status()

    def move_down(self):
        self.current_floor -= 1
        # Temporarily show status each time elevator moves
        self.show_status()

    def show_status(self):
        print ("----------------------------")
        print ("ID       : ", self.id)
        print ("Floor    : ", self.current_floor)
        print ("Capacity : ", self.current_capacity)
        print ("Status   : ", self.status.name)
        print ("----------------------------")
    
# Enumuerate Status in Elevator Class : Is there a way to use these values effectively?
class Status(Enum):
    REST = 0
    UP = 1
    DOWN = 2
    MAINTENANCE = 3      

# Set queue for multihreading between elevator operation and user input
input_queue = queue.Queue()

# Checks:
# 1: Current capacity + new capacity <= elevator max capacity
# 2: If UP:    current_floor < dest_floor
# 3: If DOWN:  current_floor > dest_floor
# Ignore commands if check fails
def sanity_check(elevator, dest_floor, capacity):
    if (elevator.current_capacity + capacity) <= elevator.capacity:
        if elevator.status == Status.UP and dest_floor > elevator.current_floor:
            return True
        
        if elevator.status == Status.DOWN and dest_floor < elevator.current_floor:
            return True
    
    return False

# Listen for elevator input from users
# Takes in DIRECTION, FLOOR, CAPACITY
def listen_for_input(elevator):
    elevator_running = True
    
    while elevator_running:
        # Reset after each input
        invalid_direction = True
        invalid_floor = True
        invalid_capacity = True

        # Set direction of elevator
        while invalid_direction:
            direction_input = input("Enter UP or DOWN or 'QUIT' to exit: ")
            if direction_input.upper() in ["UP", "DOWN", "QUIT"]:
                invalid_direction = False
            else:
                print ("Invalid direction.")

        # Set destination floor
        while invalid_floor:
            floor_input = input("Enter floor number or 'QUIT' to exit: ")
            # Floor must be within range set in Elevator Class
            try:
                if (floor_input.upper() == "QUIT") or (0 < int(floor_input) <= elevator.floor):
                    invalid_floor = False
                else:
                    print ("Invalid floor.")
            except ValueError:
                print ("Invalid floor.")
            
        while invalid_capacity:
            capacity_input = input("Enter capacity or 'QUIT' to exit: ")
            # Capacity must be within range of capacity elevator can hold: This might cause issues when multithreading?
            try:
                if (capacity_input.upper() == "QUIT") or (0 <= int(capacity_input) <= (elevator.capacity - elevator.current_capacity)):
                    invalid_capacity = False
                else:
                    print ("Invalid capacity.")
            except ValueError:
                print ("Invalid capacity.")

        # Put into queue in order of DIRECTION, FLOOR, CAPACITY
        input_queue.put([direction_input, floor_input, capacity_input])

        # Exit program
        if direction_input.upper() == "QUIT" or floor_input.upper() == "QUIT" or capacity_input.upper() == "QUIT":
            elevator_running = False

# Elevator function to process input
def process_elevator(elevator):
    elevator_running = True

    while elevator_running:
        # Wait for input to appear in the queue
        if not input_queue.empty():
            data = input_queue.get()

            # Data in form of [DIRECTION, FLOOR]
            if data[0].upper() != "QUIT" and data[1].upper() != 'QUIT' and data[2].upper() != 'QUIT':
                # To standardize input
                direction = data[0].upper()
                dest_floor = int(data[1])
                capacity = int(data[2])

                # Simulate elevator
                if direction == "UP" or direction == "DOWN":
                    elevator.set_status(direction)
                # For debugging
                else:
                    print ("Unexpected Error in processing elevator UP or DOWN")
                    print ("Current data:", data)
                
                # Sanity check on value
                if sanity_check(elevator, dest_floor, capacity):
                    # Increase current capacity of elevator
                    elevator.current_capacity += capacity
                    print (capacity, "passengers boarded", elevator.id, ".")

                    # Move elevator to floor
                    while elevator.current_floor != dest_floor:
                        if elevator.status == Status.UP:
                            elevator.move_up()
                            time.sleep(2) # Simulate some processing time

                        elif elevator.status == Status.DOWN:
                            elevator.move_down()
                            time.sleep(2) # Simulate some processing time

                        else:
                            print("Unexpected error while moving elevator.")
                            break
                    
                    # Once done, go back to rest
                    print ("Floor reached.")
                    elevator.set_status("REST")
                    
                    # Passengers leave the elevator
                    elevator.current_capacity -= capacity
                    print (capacity, "passengers left", elevator.id, ".")
                    elevator.show_status()
                
                else:
                    print ("Ignored command. Failed sanity check.")

            # Exit program
            else:
                elevator_running = False


def __main__():
    # Set up variables 
    max_capacity = 15
    max_floors = 20

    # Initialization
    ele_A = Elevator(id="ELEVATOR_A", capacity=max_capacity, floor=max_floors)
    ele_A.show_status()

    # For future implementation
    #ele_B = Elevator("ELEVATOR_B", capacity=max_capacity, floor=max_floors)
    #ele_B.show_status()

    # Creating threads
    input_thread = threading.Thread(target=listen_for_input, args=(ele_A, ))
    processing_thread = threading.Thread(target=process_elevator, args=(ele_A, ))

    # Starting threads
    input_thread.start()
    processing_thread.start()

    # Joining threads to wait for them to finish
    input_thread.join()
    processing_thread.join()

    print ("Test Done.")

__main__()