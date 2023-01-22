from browser import window

if hasattr(window, 'localStorage'):
  from browser.local_storage import storage
else:
  storage = None

def get_value(key, default_value):
  if storage is not None and key in storage and storage[key]:
    return storage[key]
  return default_value

def set_value(key, value):
    if storage is not None and storage.get(key) != value:
      storage[key] = value
