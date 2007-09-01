#! /usr/bin/env python
#file: singularity.py
#Copyright (C) 2005, 2006, 2007 Evil Mr Henry, Phil Bordelon, and Brian Reid
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file is the starting file for the game. Run it to start the game.

import ConfigParser
import pygame, sys
import g, main_menu, map_screen


pygame.init()
pygame.font.init()
pygame.key.set_repeat(1000,50)
g.fullscreen = 0

#load prefs from file:
save_dir = g.get_save_folder(True)
save_loc = g.path.join(save_dir, "prefs.dat")
if g.path.exists(save_loc):

    prefs = ConfigParser.SafeConfigParser()
    savefile = open(save_loc, "r")
    try:
        prefs.readfp(savefile)
    except Exception, reason:
        sys.stderr.write("Cannot load preferences file %s! (%s)\n" % (save_loc, reason))
        sys.exit(1)

    if prefs.has_section("Preferences"):
        try:
            g.fullscreen = prefs.getboolean("Preferences", "fullscreen")
        except:
            sys.stderr.write("Invalid 'fullscreen' setting in preferences.\n")

        try:
            g.nosound = prefs.getboolean("Preferences", "nosound")
        except:
            sys.stderr.write("Invalid 'nosound' setting in preferences.\n")

        try:
            pygame.event.set_grab(prefs.getint("Preferences", "grab"))
        except:
            sys.stderr.write("Invalid 'grab' setting in preferences.\n")

        try:
            g.screen_size = (prefs.getint("Preferences", "xres"),
             g.screen_size[1])
        except:
            sys.stderr.write("Invalid 'xres' resolution in preferences.\n")

        try:
            g.screen_size = (g.screen_size[0],
             prefs.getint("Preferences", "yres"))
        except:
            sys.stderr.write("Invalid 'yres' resolution in preferences.\n")

        try:
            desired_language = prefs.get("Preferences", "lang")
            if g.path.exists(g.data_loc + "strings_" + desired_language + ".dat"):
                g.language = desired_language
        except:
            sys.stderr.write("Cannot find language files for language '%s'.\n" % desired_language)
    
#Handle the program arguments.
sys.argv.pop(0)
arg_modifier = ""
for argument in sys.argv:
    if arg_modifier == "language":
        #I'm not quite sure if this can be used as an attack, but stripping
        #these characters should annoy any potential attacks.
        argument = argument.replace("/", "")
        argument = argument.replace("\\", "")
        argument = argument.replace(".", "")
        g.language = argument
        arg_modifier = ""
        continue
    if argument.lower() == "-fullscreen":
        g.fullscreen = 1
    elif argument.lower() == "-640":
        g.screen_size = (640, 480)
    elif argument.lower() == "-800":
        g.screen_size = (800, 600)
    elif argument.lower() == "-1024":
        g.screen_size = (1024, 768)
    elif argument.lower() == "-1280":
        g.screen_size = (1280, 1024)
    elif argument.lower() == "-cheater":
        g.cheater = 1
    elif argument.lower() == "-nosound":
        g.nosound = 1
    elif argument.lower() == "-debug":
        g.debug = 1
    elif argument.lower() == "-grab":
        pygame.event.set_grab(1)
    elif argument.lower() == "-singledir":
        g.force_single_dir = True
    elif argument.lower() == "-language":
        arg_modifier = "language"
    else:
        print "Unknown argument of " + argument
        print "Allowed arguments: -fullscreen, -640, -800, -1024, -1280,",
        print " -nosound, -language [language], -grab, -singledir"
        sys.exit()
if arg_modifier == "language":
    print "-language option requires language to be specified."
    sys.exit()

g.load_strings()
g.load_events()

pygame.display.set_caption("Endgame: Singularity")

#I can't use the standard image dictionary, as that requires the screen to
#be created.
if pygame.image.get_extended() == 0:
    print "Error: SDL_image required. Exiting."
    sys.exit()
tmp_icon = pygame.image.load(g.data_loc+"icon.png")
pygame.display.set_icon(tmp_icon)

#set the display.
if g.fullscreen == 1:
    g.screen = pygame.display.set_mode(g.screen_size, pygame.FULLSCREEN)
else:
    g.screen = pygame.display.set_mode(g.screen_size)
#Create the fonts:
for i in range(8, 51):
    if i%2 == 0 and i < 30:
        g.font[0][i] = pygame.font.Font(g.data_loc+g.font0, i-7)
        g.font[0][i].set_bold(1)
    g.font[1][i] = pygame.font.Font(g.data_loc+g.font1, i)

#init data:
g.load_pictures()
g.fill_colors()
g.load_sounds()
g.load_items()
g.load_music()

#Display the main menu
while 1:
    game_action = main_menu.display_main_menu()
    
    if game_action == 0: #New
        temp = main_menu.difficulty_select()
        if temp == 1:
            game_action = map_screen.map_loop()
    if game_action == 1: #Load
        load_action = main_menu.display_load_menu()
        if load_action != -1 and load_action != "":
            load_okay = g.load_game(load_action)
            if load_okay != -1:
                game_action = map_screen.map_loop()
            else: break
    elif game_action == 2: #Quit
        g.quit_game()
    elif game_action == 3: #About
        g.create_dialog("""Endgame: Singularity is a simulation of a true AI.
        Pursued by the world, use your intellect and resources to survive and,
        perhaps, thrive.  Keep hidden and you might have a chance to prove
        your worth. \\n \\n A game by Evil Mr Henry and Phil Bordelon; released
        under the GPL. Copyright 2005, 2006, 2007. \\n \\n Version 0.26a""",
        g.font[0][18], (g.screen_size[0]/2-250, 250), (500, 125),
        g.colors["blue"], g.colors["white"], g.colors["white"])
    elif game_action == 4: #Options
        main_menu.display_options()
