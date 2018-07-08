#!/usr/bin/python3

#http://www.jonwitts.co.uk/archives/896
# adapted from https://github.com/recantha/EduKit3-RC-Keyboard/blob/master/rc_keyboard.py

import sys, termios, tty, os, time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


#! Needs keyboard layout adjustment - where is the GDK alias wrap?
#! Needs non-fail stop
#! Needs adjustable charmap
#! fonts for pictures?
#! lowercase
#! modifiers
#! get focus back after clear
#! Button to enable Symbols
#! Enable position display, or something else, in the statusbar
#? gray background like Gedit

#extraSymbols = {
#chr(32) : '[space]',
#chr(9) : '[tab]',
#chr(27) : '[esc]',
#chr(13) : '[newline/enter]',
#chr(127) : '[go back]',
##chr(67) : '[go right]',
##chr(68) : '[go left]',
##chr(65) : '[go up]',
##chr(66) : '[go down]',
#}

#textMap = {
#'q' : 'Quiet',
#'a' : 'And',
#'z' : 'laZy',
#'w' : 'Washup',
#'s' : 'Says',
#'x' : 'eXpert',  
#'e' : 'Eggs',
#'d' : 'Do',
#'c' : 'Cook', 
#'r' : 'Run',
#'f' : 'From',
#'v' : 'Vaccum', 
#'t' : 'To',
#'g' : 'Get',
#'b' : 'Bath', 
#'y' : 'Yogurt',
#'h' : 'Honey',
#'n' : 'Nuts', 
#'u' : 'Under',
#'j' : 'Jam',
#'m' : 'Marmalade', 
#'i' : 'In',
#'k' : 'Kettle',
#',' : '[pause]', 
#'o' : 'Old',
#'l' : 'Lemon',
#'.' : '[stop]', 
#'p' : 'Prayer',
#';' : '[wait]',
#'/' : '[question]', 
#}


# If wrapped and where, I dunno
# https://github.com/tindzk/GTK/blob/master/gdk/gdkkeysyms.h
        
symbols = {
32 : '[space]',
65289 : '[tab]',
65307 : '[esc]',
65293 : '[newline/enter]',
65288 : '[go back]',
65363 : '[go right]',
65361 : '[go left]',
65362 : '[go up]',
65364 : '[go down]',
}

mnemonicMap = {
113 : 'Quiet',
97 : 'And',
122 : 'laZy',
119 : 'Washup',
115 : 'Says',
120 : 'eXpert',  
101 : 'Eggs',
100 : 'Do',
99 : 'Cook', 
114 : 'Run',
102 : 'From',
118 : 'Vaccum', 
116 : 'To',
103 : 'Get',
98 : 'Bath', 
121 : 'Yogurt',
104 : 'Honey',
110 : 'Nuts', 
117 : 'Under',
106 : 'Jam',
109 : 'Marmalade', 
105 : 'In',
107 : 'Kettle',
44 : '[pause]', 
111 : 'Old',
108 : 'Lemon',
46 : '[stop]', 
112 : 'Prayer',
59 : '[wait]',
47 : '[question]', 
}

# Python <3.5
fullMap = mnemonicMap.copy()
fullMap.update(symbols)
#print(fullMap)
# Python 3.5+
#fullMap = {**textMap, **extraSymbols}

    
    
    
    
class MyWindow(Gtk.Window):
    ## mirror file chooser

    def __init__(self):
        Gtk.Window.__init__(self, title="Lear To Touch-Type")
        #self.set_border_width(10)
        # Try opening with enough size not to bother users with other
        # controls
        self.set_default_size(450, 350)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.box)

        toolbar = Gtk.Toolbar()
        self.box.pack_start(toolbar, False, True, 0)
        
        button_clear = Gtk.ToolItem()
        button_clear_button = Gtk.Button("Remove Typing")
        button_clear.add(button_clear_button)        
        toolbar.insert(button_clear, 0)
        button_clear_button.connect("clicked", self.on_clear_clicked)
        #        toolbar.insert(Gtk.SeparatorToolItem(), 10)
        
        button_extended_symbols = Gtk.ToolItem()
        self.button_extended_button = Gtk.ToggleButton("Show Special Keys")
        button_extended_symbols.add(self.button_extended_button)        
        toolbar.insert(button_extended_symbols, 0)
        self.button_extended_button.connect("toggled", self.on_extended_symbols_clicked)

        self.createTextView()
        self.createStatusbar()
    
        # take the edge off of that whiteout start 
        self.init_text_view()

    def init_text_view(self):
        self.insert('Start...\n')
        self.textView.grab_focus()
    
    def createTextView(self):
        scrollwin = Gtk.ScrolledWindow.new()
        scrollwin.set_property("vscrollbar-policy", Gtk.PolicyType.ALWAYS)
        # leave horizontal scrollbar on Gtk.PolicyTypeAUTO
        
        # set a min size to stop horizontal crush to nothing
        # (Gedit does something like this)
        scrollwin.set_size_request(350, -1)
        self.box.pack_start(scrollwin, True, True, 0)

        self.textView = Gtk.TextView.new()
        self.textView.set_property("wrap_mode", Gtk.WrapMode.WORD)
        self.textView.set_property("left_margin", 4)
        self.textView.set_property("right_margin", 4)

        #? currently unused
        self.textBuffer = self.textView.get_buffer()
        scrollwin.add(self.textView)
        self.textViewKeypress = self.textView.connect("key-press-event", self.keyPress)

    def createStatusbar(self):
        self.statusBar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.box.pack_start(self.statusBar, False, True, 6)
        self.posDisplay = Gtk.Label().new()
        self.posDisplay.set_text('Ln:1 Col:1')
        self.statusBar.pack_end(self.posDisplay, False, True, 24)

    def on_extended_symbols_clicked(self, widget):
        self.textView.grab_focus()

    def on_clear_clicked(self, widget):
        start = self.textBuffer.get_start_iter()
        end = self.textBuffer.get_end_iter()
        self.textBuffer.delete(start, end)
        self.init_text_view()
        
    def insert(self, string):
        Gtk.TextView.do_insert_at_cursor(self.textView,  string) 
        
    def keyPress(self, widget, event):
        #https://lazka.github.io/pgi-docs/Gdk-3.0/classes/EventKey.html#Gdk.EventKey
        #print(str(widget))
        #print(str(event))
        #print(str(event.keyval))
        ## for mod keys
        #print(str(event.state))
        textToAdd = None
        try:
            if (self.button_extended_button.get_active()):
                textToAdd = fullMap[event.keyval]
            else:
                textToAdd = mnemonicMap[event.keyval]
        except:
            pass
        if (textToAdd):
            self.insert(textToAdd)       
            self.insert(' ')
        else:
           pass
        #! must be enabled, but not confirmed
        #Gdk.EventMask.KEY_PRESS_MASK 
        return True
        
        
        
        
def end(widget, event):
    #widget._settingsFromPopulation()
    #self.textView.disconnect(self.textViewKeypress)
    Gtk.main_quit()


win = MyWindow()
win.connect("delete-event", end)
win.show_all()

# Populate
#win._populateFromSettings()
Gtk.main()
