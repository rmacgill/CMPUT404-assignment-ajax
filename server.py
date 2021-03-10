#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Modifications copyright 2021 Robert MacGillivray
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, jsonify
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data
        self.notify_all(entity, data)

    def clear(self):
        self.space = dict()
        self.listeners = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

    # Listener setup adapted from: https://github.com/uofa-cmput404/cmput404-slides/blob/master/examples/ObserverExampleAJAX/server.py
    # Downside to this setup is that any dropped communications result in a slowly desyncronizing world
    def notify_all(self, entity, data):
        for listener in self.listeners:
            self.listeners[listener][entity] = data

    def add_listener(self, listener_name):
        self.listeners[listener_name] = dict()

    def get_listener(self, listener_name):
        # Better than throwing an error if there's a connection hiccup
        # when the listener was first supposed to be created
        if (listener_name not in self.listeners):
            self.add_listener(listener_name)

        return self.listeners[listener_name]

    def clear_listener(self, listener_name):
        self.listeners[listener_name] = dict()

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    """
    Simple redirect to our HTML. Could probably also simply serve HTML from here instead.
    """
    return redirect("/static/index.html", code=302)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    """
    Updates the specified entity, and then returns the updated
    JSON representation of that world entity (I'd rather not - but it's in the tests)
    """
    myWorld.set(entity, flask_post_json())
    return jsonify(myWorld.get(entity))

@app.route("/world", methods=['POST','GET'])    
def world():
    """
    Returns a JSON representation of the entire world
    """
    return jsonify(myWorld.world())

@app.route("/entity/<entity>")    
def get_entity(entity):
    """
    Returns a JSON representation of a specific world entity
    """
    return jsonify(myWorld.get(entity))

@app.route("/clear", methods=['POST','GET'])
def clear():
    """
    Clears the world, and then returns the cleared representation
    """
    myWorld.clear()
    return jsonify(myWorld.world())

# Listener setup adapted from: https://github.com/uofa-cmput404/cmput404-slides/blob/master/examples/ObserverExampleAJAX/server.py
@app.route("/listener/<entity>", methods=['POST', 'PUT'])
def add_listener(entity):
    """
    Registers a listener that will store updates until retrieved.
    Returns the current state of the world to get a new user up to date.
    """
    myWorld.add_listener(entity)
    return jsonify(myWorld.world())

@app.route("/listener/<entity>")
def get_listener(entity):
    """
    Retrieves all stored updates for a listener and clears it
    """
    data = myWorld.get_listener(entity)
    myWorld.clear_listener(entity)
    return jsonify(data)

if __name__ == "__main__":
    app.run()
