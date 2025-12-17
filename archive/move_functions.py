# 実際のロボットの代わりに動作をプリント
def move_to(room_name):
    return f"Moved to {room_name}"

def pick_object(obj):
    return f"Picked up {obj}"

def place_object_next_to(obj, target):
    return f"Placed {obj} next to {target}"

def place_object_on(obj, target):
    return f"Placed {obj} on {target}"

def place_object_in(obj, target):
    return f"Placed {obj} in {target}"

def detect_object(obj):
    return f"Detect {obj}"

def search_about(obj):
    return f"Searched about {obj}"

def push(obj):
    return f"Pushed {obj}"

def say(text):
    return f"Said {text}"