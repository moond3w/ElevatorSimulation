#  A fun little project to simulate an elevator system through the use of multithreading in python
#  ===============================================================================================
#  Context:  Two elevators will be operational in the simulation, and they will mimic a real-life
#            elevator through the following:
#            1. Both elevators will listen for input (Up/Down) from any floors (1-20)
#            2. The nearest elevator will respond unless occupied (i.e. Going in other direction)
#            3. If not in use, both elevators will be at rest in floor 1 / 10 (Mid-way)
#  ===============================================================================================
#  Version #1 : Simulating the process with a single elevator (ele_A)

import threading
import time
from queue import Queue
from enum import Enum

class Elevator:
    def __init__ (self, id: str, capacity: int, floor: int):
        self.id = id  # Can consider setting auto name
        self.capacity = capacity
        self.current_capacity = 0
        self.status = Status.REST
        self.floor = floor
        self.current_floor = 1

    def set_capacity(self, capacity: int):
        self.capacity = capacity
    
    def set_current_capacity(self, current_capacity: int):
        self.current_capacity = current_capacity

    def set_status(self, status: str):
        """
        Convert string to Status Enum
        """
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
    
    def set_floor(self, floor: int):
        self.floor = floor
    
    def set_current_floor(self, current_floor: int):
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
    

class Status(Enum):
    """
    Enumuerate Status in Elevator Class : Is there a way to use these values effectively?
    """
    REST = 0
    UP = 1
    DOWN = 2
    MAINTENANCE = 3      


def create_signal(elevator: Elevator) -> tuple:
    """
    Creates signal for elevator to respond -> Look to simplify?
    """
    # Reset after each input
    invalid_direction = True
    invalid_dest_floor = True
    invalid_capacity = True
    invalid_start_floor = True

    # Set direction of elevator
    while invalid_direction:
        direction_input = input("Enter UP or DOWN or 'QUIT' to exit: ")
        if direction_input.upper() == "QUIT":
            return "QUIT"
        if direction_input.upper() in ["UP", "DOWN"]:
            invalid_direction = False
        else:
            print ("Invalid direction.")

    # Set destination floor
    while invalid_dest_floor:
        dest_floor_input = input("Enter destination floor number or 'QUIT' to exit: ")
        # Floor must be within range set in Elevator Class
        try:
            if (dest_floor_input.upper() == "QUIT"):
                return "QUIT"
            elif (0 < int(dest_floor_input) <= elevator.floor):
                invalid_dest_floor = False
            else:
                print ("Invalid floor.")
        except ValueError:
            print ("Invalid floor.")
        
    while invalid_capacity:
        capacity_input = input("Enter capacity or 'QUIT' to exit: ")
        # Capacity must be within range of capacity elevator can hold: This might cause issues when multithreading?
        try:
            if (capacity_input.upper() == "QUIT"):
                return "QUIT"
            elif 0 <= int(capacity_input) <= (elevator.capacity - elevator.current_capacity):
                invalid_capacity = False
            else:
                print ("Invalid capacity.")
        except ValueError:
            print ("Invalid capacity.")
    
    # Set starting floor
    while invalid_start_floor:
        start_floor_input = input("Enter starting floor number or 'QUIT' to exit: ")
        # Floor must be within range set in Elevator Class
        try:
            if (start_floor_input.upper() == "QUIT"):
                return "QUIT"
            elif (0 < int(start_floor_input) <= elevator.floor):
                invalid_start_floor = False
            else:
                print ("Invalid floor.")
        except ValueError:
            print ("Invalid floor.")
    
    return (direction_input, dest_floor_input, capacity_input, start_floor_input)


def sanity_check(elevator: Elevator, direction: str, dest_floor: int, capacity: int) -> bool:
    """
    Checks:
    1: Current capacity + new capacity <= elevator max capacity
    2: If UP:    current_floor < dest_floor
    3: If DOWN:  current_floor > dest_floor
    Ignore commands if check fails
    """
    if (elevator.current_capacity + capacity) <= elevator.capacity:
        if direction == "UP" and dest_floor > elevator.current_floor:
            return True
        
        if direction == "DOWN" and dest_floor < elevator.current_floor:
            return True
    
    return False


def listen_for_input(elevator: Elevator, input_queue: Queue):
    """
    Listen for elevator input from users
    Takes in DIRECTION, FLOOR, CAPACITY
    """
    elevator_running = True
    
    while elevator_running:
        signal = create_signal(elevator)

        # Signal either an array or "QUIT"
        input_queue.put(signal)

        if signal == "QUIT":
            elevator_running = False
        

def process_elevator(elevator: Elevator, input_queue: Queue):
    """
    Elevator function to process input
    """
    elevator_running = True

    while elevator_running:
        # Check for input every 0.5 seconds
        if input_queue.empty():
            time.sleep(0.5)
            continue
        
        signal = input_queue.get()

        # Program ends if receives "QUIT"
        if signal == "QUIT":
            elevator_running = False
            return

        # Set up variables from input
        direction = signal[0].upper()
        dest_floor = int(signal[1])
        capacity = int(signal[2])
        start_floor = int(signal[3])

        print ("Received Signal : ", signal)
        print ("Moving to floor : ", start_floor)

        # Elevator will respond by moving to the signaled start floor regardless of sanity check
        if (elevator.current_floor - start_floor > 0):
            elevator.set_status("DOWN")
        elif (elevator.current_floor - start_floor < 0):
            elevator.set_status("UP")
        else:
            pass
        
        while elevator.current_floor != start_floor:
            if elevator.status == Status.UP:
                elevator.move_up()
                time.sleep(2)  # Simulate some processing time

            elif elevator.status == Status.DOWN:
                elevator.move_down()
                time.sleep(2)  # Simulate some processing time
        
        print ("Arrived at floor : ", start_floor)
        elevator.set_status("REST")
        
        # Sanity check on values before executing
        if not sanity_check(elevator, direction, dest_floor, capacity):
            print ("Ignored command. Failed sanity check.")
            continue

        # Start response to elevator signal
        elevator.current_capacity += capacity
        print (capacity, "passengers boarded", elevator.id, ".")

        if direction == "UP" or direction == "DOWN":
            elevator.set_status(direction)
        else:
            print ("Unexpected Error in processing elevator UP or DOWN")
            print ("Current signal:", signal)

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


def __main__():
    # Set up variables 
    max_capacity = 15
    max_floors = 10

    # Initialization
    ele_A = Elevator(id="ELEVATOR_A", capacity=max_capacity, floor=max_floors)
    ele_A.show_status()

    # Set queue for multihreading between elevator operation and user input
    input_queue = Queue()

    # For future implementation
    #ele_B = Elevator("ELEVATOR_B", capacity=max_capacity, floor=max_floors)
    #ele_B.show_status()

    # Creating threads
    input_thread = threading.Thread(target=listen_for_input, args=(ele_A, input_queue))
    processing_thread = threading.Thread(target=process_elevator, args=(ele_A, input_queue))

    # Starting threads
    input_thread.start()
    processing_thread.start()

    # Joining threads to wait for them to finish
    input_thread.join()
    processing_thread.join()

    print ("Test Done.")


if __name__ == "__main__":
    __main__()