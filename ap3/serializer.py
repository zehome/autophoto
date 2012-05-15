# -*- coding: utf-8 -*-

import json

def JsonSerializer(data):
    return json.dumps(data)

def PrettyJsonSerializer(data):
    return json.dumps(data, sort_keys=True, indent=4)
