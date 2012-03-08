###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

import sys
import time
import threading
from math import pi
import socket

from pivy.coin import *
from pivy.sogui import *


PORT = 4567
TORAD = pi / 180


def connect_to_socket(host, port):
    print "Connecting to %s on port %d" % (host, port)
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Connected"
    connection.connect((host, port))
    socketfile = connection.makefile('rw', 0)
    return socketfile


def serve_socket_connection(port):
    print ("Serving connection on all interfaces on %s port %d" %
           (socket.gethostname(), port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((socket.gethostname(), port))
    sock.listen(1)
    time.sleep(1)
    (connection, addr) = sock.accept()
    print 'Connected from ', addr, ' accepted'
    socket_file = connection.makefile('rw', 0)  # no buffering
    return socket_file


def node_name(anglename):
    return 'dad_' + anglename + '_frame'


class SceneUpdatingThread(threading.Thread):

    def __init__(self, scene, axisnames):
        threading.Thread.__init__(self)
        self.scene = scene

        # Infer rotation axes based on initial orientation
        self.rotation_axes = {}
        self.axies_nodes = {}
        for axisname in axisnames:
            node = self.scene.getByName(node_name(axisname))
            self.axies_nodes[axisname] = node
            value = node.rotation.getValue()
            self.rotation_axes[axisname] = value.getAxisAngle()[0]

    def run(self):
        socket_file = serve_socket_connection(PORT)

        while True:
            msg = socket_file.readline()
            if msg == '':
                print '***Socket closed'
                socket_file = serve_socket_connection(PORT)
                continue
            print msg.strip()
            d = eval(msg.strip())  # msg should be a dictionary representation
            for axisname in d:
                self.set_axis_rotation(axisname, d[axisname])

    def set_axis_rotation(self, anglename, degrees):
        nodename = node_name(anglename)
        angle = degrees * TORAD
        while angle < 0:
            angle = 2 * pi + angle
        node = self.scene.getByName(nodename)
        getattr(node, 'rotation').setValue(
            self.rotation_axes[anglename], angle)


class Animator(object):

    def __init__(self, filename, axisnames):
        print "filename : " + filename
        print "    axes : " + ' '.join(axisnames)
        # Create viewer
        self.myWindow = SoGui.init(sys.argv[0])  # @UndefinedVariable
        if self.myWindow is None: sys.exit(1)
        viewer = SoGuiExaminerViewer(self.myWindow)  # @UndefinedVariable
        # load file into scene
        so_input = SoInput()  # @UndefinedVariable
        so_input.openFile(filename)
        self.scene = SoDB.readAll(so_input)  # @UndefinedVariable
        # Add scene to viewer
        viewer.setSceneGraph(self.scene)
        viewer.setTitle(' '.join(axisnames))
        viewer.show()

        self.start_update_scene_thread(axisnames)

    def start_update_scene_thread(self, axisnames):
        t = SceneUpdatingThread(self.scene, axisnames)
        t.setDaemon(True)
        t.start()

    def show(self):
        SoGui.show(self.myWindow)  # @UndefinedVariable
        SoGui.mainLoop()  # @UndefinedVariable

def main():
    animator = Animator(sys.argv[1], sys.argv[2:])
    animator.show()

if __name__ == "__main__":
    main()

