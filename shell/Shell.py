#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re

def handleInput(input):
    args = userInput.split(' ')
    if userInput.lower() == 'exit':
        sys.exit(0)
    elif len(args) == 0:
        pass
    elif args[0] == 'cd':
        try:
            os.chdir(args[1])
            os.write(1, (os.getcwd()+"\n").encode())
        except FileNotFoundError:
            os.write(1, ("Directory %s: No such file or directory\n" % args[1]).encode())
            pass
    elif '/' in args[0][0]:
        callExecve(args[0],args)
        os.write(2, ("Command %s No such command.\n" % args[0]).encode())
        sys.exit(1)# terminate with error    

    else:
        execute(args)

def execute(args):
    pid = os.getpid()
    rc = os.fork()
    if rc < 0 :
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            callExecve(program, args)
        os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
        sys.exit(1) # terminate with error    

    else:
        childpid = os.wait()

#Made to call execve for the programs that need it
def callExecve(program, args):
    try:
        os.execve(program, args, os.environ)
    except FileNotFoundError:
        pass
    except IndexError:
        sys.exit(1)
    except Exception:
        sys.exit(1)

# Main
while True:
    if 'PS1' in os.environ:
        os.write(1, os.environ['PS1'].encode())
    
    else:
        os.write(1, ("$ ").encode())

    try:
        userInput = input()
    except EOFError:
        sys.exit(1)
        
    handleInput(userInput)
    
    
