#!/usr/bin/python3

#http://www.jonwitts.co.uk/archives/896
# adapted from https://github.com/recantha/EduKit3-RC-Keyboard/blob/master/rc_keyboard.py

import sys, termios, tty, os, time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


#! Needs keyboard layout adjustment - where is the GDK alias wrap?
#! make 'Enable backspace and newline' button
#! handle missed keys
#! Needs adjustable charmap
#! fonts for pictures?
#! modifiers
#! Enable position display, or something else, in the statusbar
#? gray background like Gedit
#? put preferences in a preferences meni
#x (GTK makes impossible) Some form of zoom?
#x ('close window' will do) Needs non-fail stop

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
BACKSPACE = 65288
BASIC_EDIT_CONTROLS = {
    32 : '[space]',
    65293 : '[new line/send]',
    65288 : '[delete backwards]',
    }
       
 # classiying TAB as navigation-control becuaese
 # - it is in GUIs and forms
 # - no real person uses tabs
 # - no real person should use tabs, they're awful (cf. makefiles)
NAVIGATION_CONTROLS = {
    65289 : '[tab]',
    #65307 : '[esc]',
    65363 : '[go right]',
    65361 : '[go left]',
    65362 : '[go up]',
    65364 : '[go down]',
    }

TYPE_NAVIGATION_CONTROLS = BASIC_EDIT_CONTROLS.copy()
TYPE_NAVIGATION_CONTROLS.update(NAVIGATION_CONTROLS)

MNEMONIC_MAP = {
    81 : 'Quiet',
    65 : 'And',
    90 : 'laZy',
    87 : 'Washup',
    83 : 'Says',
    88 : 'eXpert',  
    69 : 'Eggs',
    68 : 'Do',
    67 : 'Cook', 
    82 : 'Run',
    70 : 'From',
    86 : 'Vaccum', 
    84 : 'To',
    71 : 'Get',
    66 : 'Bath', 
    89 : 'Yogurt',
    72 : 'Honey',
    78 : 'Nuts', 
    85 : 'Under',
    74 : 'Jam',
    77 : 'Marmalade', 
    73 : 'In',
    75 : 'Kettle',
    60 : '[pin left]', 
    79 : 'Old',
    76 : 'Lemon',
    62 : '[pin right]', 
    80 : 'Prayer',
    58 : '[long wait]',
    63 : '[question]', 
    # lowercase
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
    47 : '[forward slash]', 
    }
  
# Python <3.5
FULL_MAP = MNEMONIC_MAP.copy()
FULL_MAP.update(TYPE_NAVIGATION_CONTROLS)
#print(fullMap)
# Python 3.5+
#fullMap = {**textMap, **extraSymbols}

    
    
    
PROMPT = 'Start...\n'
PROMPT_LENGTH = len(PROMPT)

class MyWindow(Gtk.Window):
    ## mirror file chooser

    def __init__(self):
        Gtk.Window.__init__(self, title="Learn To Touch-Type")
        #self.set_border_width(10)
        # Try opening with enough size not to bother users with other
        # controls
        self.set_default_size(450, 350)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.box)

        self.createToolbar()
        self.createTextView()
        self.createStatusbar()
    
        self.init_text_view()

    def init_text_view(self):
        '''
        Actions on start or clear.
        Takes the edge off a whiteout start by adding a message. Moves
        focus to typing area.
        '''
        self.insert(PROMPT)
        self.textView.grab_focus()
      
    def createToolbar(self):
        toolbar = Gtk.Toolbar()
        self.box.pack_start(toolbar, False, True, 0)
        
        toolitem_clear = Gtk.ToolItem()
        button_clear = Gtk.Button("Remove Typing")
        toolitem_clear.add(button_clear)        
        toolbar.insert(toolitem_clear, 0)
        button_clear.connect("clicked", self.on_clear_clicked)
        #        toolbar.insert(Gtk.SeparatorToolItem(), 10)
        
        toolitem_print_controls = Gtk.ToolItem()
        self.button_print_controls = Gtk.ToggleButton("Print Control Keys")
        toolitem_print_controls.add(self.button_print_controls)        
        toolbar.insert(toolitem_print_controls, 0)
        self.button_print_controls.connect("toggled", self.on_print_controls_clicked)
       
        toolitem_use_basic_controls = Gtk.ToolItem()
        self.button_use_basic_controls = Gtk.ToggleButton("Use Edit Controls")
        toolitem_use_basic_controls.add(self.button_use_basic_controls)        
        toolbar.insert(toolitem_use_basic_controls, 0)
        self.button_use_basic_controls.connect("toggled", self.on_use_basic_controls_clicked)

        #self.button_zoom = Gtk.ToolButton()
        #self.button_zoom.set_icon_name("zoom-in")
        #toolbar.insert(self.button_zoom, 0)
        #self.button_zoom.connect("clicked", self.on_zoom_clicked)
        
        #self.button_unzoom = Gtk.ToolButton()
        #self.button_unzoom.set_icon_name("zoom-out")
        #toolbar.insert(self.button_unzoom, 0)
        
        #self.button_reset_zoom = Gtk.ToolButton()
        #self.button_reset_zoom.set_icon_name("zoom-original")
        #toolbar.insert(self.button_reset_zoom, 0)
              
      
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

        self.textBuffer = self.textView.get_buffer()
        #self.textBuffer.“delete-range"
        scrollwin.add(self.textView)
        self.textViewKeypress = self.textView.connect("key-press-event", self.keyPress)

    def createStatusbar(self):
        self.statusBar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.box.pack_start(self.statusBar, False, True, 6)
        self.posDisplay = Gtk.Label().new()
        self.posDisplay.set_text('Ln:1 Col:1')
        self.statusBar.pack_end(self.posDisplay, False, True, 24)

    def on_print_controls_clicked(self, widget):
        # logic like a radio button, with none ooption
        if (self.button_print_controls.get_active()):
            self.button_use_basic_controls.set_active(False)
        self.textView.grab_focus()

    def on_use_basic_controls_clicked(self, widget):
        # logic like a radio button, with none ooption
        if (self.button_use_basic_controls.get_active()):
            self.button_print_controls.set_active(False)
        self.textView.grab_focus()
        
    def on_clear_clicked(self, widget):
        start = self.textBuffer.get_start_iter()
        end = self.textBuffer.get_end_iter()
        self.textBuffer.delete(start, end)
        self.init_text_view()
    
    def word_delete(self):
        # for Gtk.TextView.do_delete_from_cursor() niether display lines
        # nor WORDS is working and the function wrap requires 'static' 
        # type nomenclature. 
        #
        # Ten years later, GTK progresses yet by exploring every pit 
        # of shit before deciding a plank may be a good idea.
        # No wonder---Geany uses Scitie.
        cp = self.textBuffer.get_property("cursor-position")
        itStart = self.textBuffer.get_iter_at_offset(cp)
        itEnd = self.textBuffer.get_iter_at_offset(cp)
        itEnd.backward_word_start()
        # Don't erase the prompt
        if (itEnd.get_offset() >= PROMPT_LENGTH):
            self.textBuffer.delete(itStart, itEnd)

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
            if (self.button_print_controls.get_active()):
                textToAdd = FULL_MAP[event.keyval]
            else:
                textToAdd = MNEMONIC_MAP[event.keyval]
        except:
            pass
        if (textToAdd):
            self.insert(textToAdd)       
            self.insert(' ')
        else:
           pass

        # sometimes, allow a few naviagtion keys to do their usual work.
        # This reverts BACKSPACE to a usual one-codepoint delete.
        if (
            self.button_use_basic_controls.get_active()
            and event.keyval in BASIC_EDIT_CONTROLS
            ):
            # allow these keys to do their usual job.
            return False 

        # if set as stock, ask backspace to delete works
        if(
            not self.button_print_controls.get_active()
            and event.keyval == BACKSPACE
            ):
            self.word_delete()
            
        # stop every other key action.
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
