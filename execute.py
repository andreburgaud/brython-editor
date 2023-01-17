from browser import worker, bind, self
import sys

class Stdout:
  def __init__(self, worker):
    self.worker = worker

  def write(self, text):
    # TODO: extra \n sent - not sure why
    if len(text.strip()) > 0:
      self.worker.send(text)

@bind(self, "message")
def message(evt):
  """Handle a message sent by the main script.
  evt.data is the message body.
  """
  sys.stdout = Stdout(self)
  try:
    src = evt.data
    ns = {'__name__':'__main__'}
    exec(src, ns)
  except:
    self.send('Problem executing the script')
