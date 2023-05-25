import rtmidi
import time
import threading
import os

# Our midi input and output objects
midi_in = rtmidi.RtMidiIn()
midi_out = rtmidi.RtMidiOut()

# A list of all the notes on the keyboard
keyb_notes = {}

# A variable for keeping track of whether or not to run the key spam
run_spam = True
in_port = None
out_port = None
left_key = None
right_key = None

# For clearing the terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    

# Initalize the shit (mainly populate the notes list)
def init():
    global left_key, right_key
    
    l_key = None
    r_key = None
    
    clear()
    print("Initialization\n-----------------------")
    print("Press the leftmost key")
    while (l_key == None):
        m = midi_in.getMessage(250)
        if m:
            if m.isNoteOn():
                print("Got note nr {0} aka \"{1}\"".format(m.getNoteNumber(), m.getMidiNoteName(m.getNoteNumber()), m.getVelocity()))
                l_key = m
    
    print("\nPress the rightmost key...")
    while (r_key == None):
        m = midi_in.getMessage(250)
        if m:
            if m.isNoteOn():
                print("Got note nr {0} aka \"{1}\"".format(m.getNoteNumber(), m.getMidiNoteName(m.getNoteNumber()), m.getVelocity()))
                r_key = m
    
    print("\nCreating keyboard note array...")
    for note in range(l_key.getNoteNumber(), r_key.getNoteNumber()+1):
        keyb_notes[str(note)] = False
        
    print("Keyboard array created!")
    left_key = l_key.getMidiNoteName(l_key.getNoteNumber())
    right_key = r_key.getMidiNoteName(r_key.getNoteNumber())
    time.sleep(1)


# A function for printing an incomming node msg
def print_msg(midi):
    if midi.isNoteOn():
        print("ON: ", midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print("OFF: ", midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print("CONTROLLER: ", midi.getControllerNumber(), midi.getControllerValue())


# For connecting the output to a user choosen output port
def connect_out():
    global out_port
    
    clear()
    print("Connect Output\n-----------------------")
    port_count = midi_out.getPortCount()
    
    if port_count != 0:
        for p in range(port_count):
            print("[{0}] {1}".format(p, midi_out.getPortName(p)))
        print("[{0}] Create virtual port\n^ VIRTUAL PORTS DOES NOT WORK IN \"WINDOWS MM MIDI API\"".format(port_count))
            
        choosen_port = -1
        while choosen_port > port_count or choosen_port < 0:
            choosen_port = int(input("\nChoose a port [0..{0}] : ".format(port_count)))
            
        if choosen_port != port_count:
            print("Connecting to port {0} aka \"{1}\"...".format(choosen_port, midi_out.getPortName(choosen_port)))
            out_port = midi_out.getPortName(choosen_port)
            midi_out.openPort(choosen_port)
        else:
            out_port = input("Enter a name for the virtual port: ")
            if midi_out.openVirtualPort(out_port) == None:
                print("Virtual ports does not work in \"Windows MM MIDI API\"\nQuitting...")
                exit(0)
    else:
        print("No ports where found... enter a port name below to start a virtual port")
        out_port = input("Port name: ")
        if midi_out.openVirtualPort(out_port) == None:
            print("Virtual ports does not work in \"Windows MM MIDI API\"\nQuitting...")
            exit(0)


# For connecting the input to a user choosen input port
def connect_in():
    global in_port
    
    clear()
    print("Connect input\n-----------------------")
    port_count = midi_in.getPortCount()
    for p in range(port_count):
        print("[{0}] {1}".format(p, midi_in.getPortName(p)))
    choosen_port = -1
    while choosen_port >= port_count or choosen_port < 0:
        choosen_port = int(input("\nChoose a port [0..{0}] : ".format(port_count-1)))
    
    print("Connecting to port {0} aka \"{1}\"...".format(choosen_port, midi_in.getPortName(choosen_port)))
    in_port = midi_in.getPortName(choosen_port)
    midi_in.openPort(choosen_port)
  

# For sending all ON notes
def send_all_ON():
    global run_spam
    for note in keyb_notes.keys():
        print()
        if not keyb_notes[note]:
            m = rtmidi.MidiMessage.noteOn(1, int(note), 100)
            midi_out.sendMessage(m)
            keyb_notes[note] = True
            
    while run_spam:
        pass
    

# For sending all OFF notes and make all while loops quit
def quit_prog():
    global run_spam
    run_spam = False
    for note in keyb_notes.keys():
        print()
        if keyb_notes[note]:
            m = rtmidi.MidiMessage.noteOff(1, int(note))
            midi_out.sendMessage(m)
            keyb_notes[note] = False
    

# Flip a singular note from ON to OFF and vice versa
def flip_note(note):
    try:
        m = None
        if not keyb_notes[str(note)]:
            m = rtmidi.MidiMessage.noteOn(1, int(note), 100)
        else:
            m = rtmidi.MidiMessage.noteOff(1, int(note))
        keyb_notes[str(note)] = not keyb_notes[str(note)]
        midi_out.sendMessage(m)
    except:
        pass

    
# For getting which notes are physically pressed
def get_notes():
    global run_spam
    
    while(run_spam):
        m = midi_in.getMessage(250)
        if m:
            flip_note(int(m.getNoteNumber()))

    
# Program entry point
if __name__ == '__main__':
    connect_in()
    connect_out()
    init()
    
    all_on = threading.Thread(target=send_all_ON, daemon=True)
    get_on = threading.Thread(target=get_notes, daemon=True)
    all_on.start()
    get_on.start()
    
    clear()
    print("Program running\n-----------------------")
    print("   Intercepting all notes between {0} and {1}\n".format(left_key, right_key))
    print("   INPUT PORT:\t{0}\n   OUTPUT PORT:\t{1}".format(in_port, out_port))
    print("\nPress 'x' and hit enter to quit")
    
    while (input("").lower() != "x"):
        pass
    print("\nQuiting...")
    
    quit_prog()
    all_on.join()
    get_on.join()
    
    exit(0)