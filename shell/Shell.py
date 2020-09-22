#!/usr/bin/env python3
""""
Armando Ortiz
Program meant to replicate functionality of a shell
"""
import os, sys, re

def handleInput(input_args):
    """
    used to manage input and pick between different shell possibilities
    """
    args = input_args.split(' ')
    if input_args.lower() == 'exit':
        os.write(1,("Goodbye\n").encode())
        sys.exit(0)
    elif len(args) == 0:
        pass
    elif args[0] == 'cd':
        try:
            os.chdir(args[1])
            os.write(1, (os.getcwd()+"\n").encode())
        except FileNotFoundError:
            os.write(1, ("Directory %s: No such file or directory\n" % args[1]).encode())
    elif '/' in args[0]:
        callExecve(args[0], args)
        os.write(2, ("Command %s No such command.\n" % args[0]).encode())
        sys.exit(1)# terminate with error

    else:
        execute(args)

def execute(args):
    """
    forks and attempts to execute program using callExecve()
    """
    rc = os.fork()
    wait = True
    if '&' in args:
        wait = False
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            callExecve(program, args)
        os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
        sys.exit(1) # terminate with error

    else:
        if wait:
            childpid = os.wait()
            if childpid[1] != 0 and childpid[1] != 256:
                os.write(2, ("Program terminated with exit code: %d\n" % childpid[1]).encode())


def callExecve(program, args):
    """
    made to call execve for the programs that need it
    """
    try:
        os.execve(program, args, os.environ) # try to execute program
    except FileNotFoundError:
        pass
    except Exception:
        sys.exit(1)


while True:
    if 'PS1' in os.environ:
        os.write(1, os.environ['PS1'].encode())

    else:
        os.write(1, ("$ ").encode())

    try:
        args = os.read(0, 1024)
        if len(args) == 0:
            break
        args = args.decode().split("\n")
        for arg in args:
            handleInput(arg)
    except EOFError:
        sys.exit(1)
    