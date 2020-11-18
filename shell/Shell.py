#!/usr/bin/env python3
""""
Armando Ortiz
Program meant to replicate functionality of a shell
"""
import os, sys, re

def handleInput(args):
    """
    used to manage input and pick between different shell possibilities
    """
    if len(args) == 0:
        return
    elif args[0].lower() == 'exit':
        os.write(1,("Goodbye\n").encode())
        sys.exit(0)
    elif args[0] == 'cd':
        try:
            if len(args) == 1:
                os.chdir("..")
            else:
                os.chdir(args[1])
        except FileNotFoundError:
            os.write(1, ("Directory %s: No such file or directory\n" % args[1]).encode())
    elif "|" in args:
        piping(args)
    else:
        rc = os.fork()
        wait = True
        if "&" in args:
            args.remove("&")
            wait = False
        if rc < 0:
            os.write(2,("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            execute(args)
            sys.exit(0)
        else:
            if wait:
                childpid = os.wait()
        
def redirection(args):
    '''
    Handles input/output redirection
    '''
    if '>' in args:
        os.close(1)
        os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)
        args.remove(args[args.index('>') + 1])
        args.remove('>')
    else:
        os.close(0)
        os.open(args[args.index('<')+1], os.O_RDONLY)
        os.set_inheritable(0, True)
        args.remove(args[args.index('<') + 1])
        args.remove('<')
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        callExecve(program, args)
    os.write(2, ("Child: Error: Could not exec %s\n" % args[0]).encode())
    sys.exit(1)

def piping(args):
    '''
    Handles piping
    '''
    left_pipe = args[0:args.index("|")]
    right_pipe = args[args.index("|")+1:]
    pr,pw = os.pipe()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr,pw):
            os.close(fd)
        execute(left_pipe)
        os.write(2, ("Could not exec %s\n" % left_pipe[0]).encode())
        sys.exit(1)
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pr,pw):
            os.close(fd)
        if "|" in right_pipe:
            piping(right_pipe)
        execute(right_pipe)
        os.write(2, ("Could not exec %s\n" % right_pipe[0]).encode())
        sys.exit(1)

def execute(args):
    """
    forks and attempts to execute program using callExecve()
    """
    
    #wait = True
    if ">" in args or "<" in args:
        redirection(args)
    elif "/" in args[0]:
        program = args[0]
        call_execve(program, args)
    else:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            call_execve(program, args)
    os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
    sys.exit(1) # terminate with error

def call_execve(program, args):
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
        if not args:
            continue
        for arg in args:
            handleInput(arg.split())
    except EOFError:
        sys.exit(1)
    
