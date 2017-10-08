#!/usr/bin/env python3

'''General utilities.'''


import sys
import os
import subprocess
import shlex
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = True


def run_pipe(steps, outfile=None):
    # TODO:  capture stderr
    from subprocess import Popen, PIPE
    p = None
    p_next = None
    first_step_n = 1
    last_step_n = len(steps)
    for n, step in enumerate(steps, start=first_step_n):
        logger.debug("step %d: %s" % (n, step))
        if n == first_step_n:
            if n == last_step_n and outfile:  # one-step pipeline with outfile
                with open(outfile, 'w') as fh:
                    print("one step shlex: %s to file: %s" % (shlex.split(step), outfile))
                    p = Popen(shlex.split(step), stdout=fh)
                break
            print("first step shlex to stdout: %s" % (shlex.split(step)))

            p = Popen(shlex.split(step), stdout=PIPE)
        elif n == last_step_n and outfile:  # only treat the last step specially if you're sending stdout to a file
            with open(outfile, 'w') as fh:
                print("last step shlex: %s to file: %s" % (shlex.split(step), outfile))
                p_last = Popen(shlex.split(step), stdin=p.stdout, stdout=fh)
                p.stdout.close()
                p = p_last
        else:  # handles intermediate steps and, in the case of a pipe to stdout, the last step
            print("intermediate step %d shlex to stdout: %s" % (n, shlex.split(step)))
            p_next = Popen(shlex.split(step), stdin=p.stdout, stdout=PIPE)
            p.stdout.close()
            p = p_next
    out, err = p.communicate()
    return out, err


def strip_extensions(filename, extensions):
    '''Strips extensions to get basename of file.'''

    basename = filename
    for extension in extensions:
        basename = basename.rpartition(extension)[0] or basename

    return basename
