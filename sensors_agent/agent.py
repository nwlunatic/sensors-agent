import os
import sys

import sensors

from .server import Server


def check_root():
    if os.getuid() != 0:
        raise Exception("should run as root to call hddtemp")


def daemonize(pidfile):
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError:
        raise

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            if pidfile is not None:
                with open(pidfile, "w+") as pf:
                    pf.write(str(pid))
            sys.exit(0)
    except OSError:
        raise


def serve(port):
    sensors.init()
    server = Server("localhost", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    finally:
        sensors.cleanup()


def main(args):
    check_root()
    if args.daemonize:
        daemonize(args.pidfile)
    serve(args.port)