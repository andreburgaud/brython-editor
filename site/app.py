import sys, time

from browser import document, timer, window

import config
import editor

MIN_HEIGHT_EDITOR = 40
MIN_HEIGHT_OUTPUT = 50
SPLITTER_HEIGHT = 8
TOOLBAR_HEIGHT = 60
STATUSBAR_HEIGHT = 30

class App:

  def __init__(self, cfg: config.Config):
    self.is_resizing = False
    self.config = cfg
    self.editor = cfg.editor
    self.init_editor()
    self.session = self.editor.getSession()
    self.mainframe = document['mainframe']
    self.toolbar = document['toolbar']
    self.container_edit = document['container-edit']
    self.splitter = document['splitter']
    self.output = document['output']
    self.stb_status = document['stb-status']

    self.btn_run = document['btn-run']
    self.btn_clear = document['btn-clear']

    self.burger = document['burger']
    self.menu = document['navMenu']

    self.google_mac_arm = self.is_google_mac_arm()

    self.bind_events()

  def init_editor(self):
    self.editor.setValue(self.config.code)
    self.editor.setFontSize(self.config.font_size)
    self.editor.setTheme(f'ace/theme/{self.config.theme}')
    self.editor.scrollToRow(0)
    self.editor.gotoLine(0)

  def is_google_mac_arm(self):
    # Overcome a bug when importing traceback with Google Chrome on Mac ARM
    canvas = document.createElement('canvas')
    try:
      gl = canvas.getContext('webgl') or canvas.getContext('experimental-webgl')
    except:
      return False
    debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
    renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
    if "Google" in window.navigator.vendor and "Apple M" in renderer:
      return True
    return False

  def write_out(self, *args):
    self.output.value += ''.join(args)

  def write_err(self, *args):
    self.output.value += ''.join(args)

  def clear_output(self):
    self.output.value = ''
    self.output.style.color = ''

  def clear(self):
    self.clear_output()
    self.clear_status()
    self.session.clearAnnotations()

  def on_clear(self, evt):
    self.clear()

  def clear_status(self):
    self.stb_status.text = ''
    self.stb_status.style.color = ''

  def start_progress(self):
    self.stb_status.text = 'Execution in progress...'

  def on_reset(self, evt):
    self.reset_code()
    self.reset_size()
    self.clear_output()
    self.clear_status()

  def on_run(self, evt):
    src = self.editor.getValue()
    if len(src.strip()) == 0:
      return
    self.clear()
    self.start_progress()
    timer.set_timeout(self.exec_code, 10)

  def exec_code(self):
    src = self.editor.getValue()
    line_count = len(src.split('\n'))
    t0 = time.perf_counter()

    try:
      ns = {'__name__':'__main__'}
      exec(src, ns)

    except SyntaxError as err:
      if self.google_mac_arm:
        self.display_simple_error(err)
      else:
        self.handle_syntax_error(line_count)

    except Exception as exc:
      if self.google_mac_arm:
        self.display_simple_error(err)
      else:
        self.handle_error(line_count)

    except:
      print("Unknown exception")

    else:
      self.stb_status.text = 'Executed in %6.2f ms' % ((time.perf_counter() - t0) * 1000.0)

  def handle_error(self, line_count):
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lineno = traceback.extract_tb(exc_traceback)[-1].lineno
    lineno = line_count if lineno > line_count else lineno
    formatted_lines = traceback.format_exc().splitlines()
    error_text =  f'Line {lineno}: {formatted_lines[-1]}'
    self.display_error(error_text, lineno)

  def handle_syntax_error(self, line_count):
    import traceback
    exc_type, exc_value, _ = sys.exc_info()
    exceptions = traceback.format_exception_only(exc_type, exc_value)
    lineno = exceptions[0].strip().split()[-1]
    if lineno.isdigit():
      lineno = int(lineno)
    else:
      lineno = line_count
    error_text = f'Line {lineno}: {exceptions[-1]}'
    self.display_error(error_text, lineno)

  def display_error(self, error_text, lineno):
    self.output.style.color = 'red'
    self.stb_status.style.color = 'red'
    self.stb_status.text = error_text
    print(error_text)
    self.editor.gotoLine(lineno, 0, True)
    self.session.setAnnotations([{
      'row': lineno-1,
      'column': 0,
      'text': "Error Message",
      'type': "error"
    }])

  def display_simple_error(self, error_text): # Bug Chrome Mac ARM
    self.output.style.color = 'red'
    self.stb_status.style.color = 'red'
    self.stb_status.text = error_text
    print(error_text)

  def bind_events(self):
    self.splitter.bind('mousedown', self.start_resize)
    self.splitter.bind('touchstart', self.start_resize)
    self.splitter.bind('touchend', self.end_resize)
    self.splitter.bind('touchcancel', self.end_resize)
    self.mainframe.bind('mousemove', self.on_resize)
    self.splitter.bind('touchmove', self.on_resize)
    self.btn_run.bind('click', self.on_run)
    self.btn_clear.bind('click', self.on_clear)
    self.editor.bind('blur', self.on_blur)
    window.onresize = self.on_window_resize
    window.onmouseup = self.end_resize

    self.burger.bind('click', self.on_burger)

  def on_burger(self, evt):
    self.menu.classList.toggle('is-active')
    self.burger.classList.toggle('is-active')
    self.resizeMobile()

  def start_resize(self, evt):
    self.is_resizing = True
    self.splitter.style.cursor = 'ns-resize'

  def end_resize(self, evt):
    if self.is_resizing:
      self.is_resizing = False
      self.splitter.style.cursor = 'ns-resize'

  def resize(self, evt):
    if evt.type == 'mousemove':
      clienty = evt.clientY
    elif evt.type == 'touchmove':
      clienty = evt.touches[0].clientY
    else:
      print(evt.type)
      return
    if clienty > self.mainframe.clientHeight - (MIN_HEIGHT_OUTPUT + STATUSBAR_HEIGHT):
      editor_height = self.mainframe.clientHeight - (MIN_HEIGHT_OUTPUT + STATUSBAR_HEIGHT)
    elif clienty < (MIN_HEIGHT_EDITOR + TOOLBAR_HEIGHT):
      editor_height = MIN_HEIGHT_EDITOR
    else:
      editor_height = clienty - TOOLBAR_HEIGHT
    output_height = self.mainframe.clientHeight - (TOOLBAR_HEIGHT + editor_height + SPLITTER_HEIGHT + STATUSBAR_HEIGHT)
    self.mainframe.style.gridTemplateRows = f'{TOOLBAR_HEIGHT}px {editor_height}px {SPLITTER_HEIGHT}px {output_height}px {STATUSBAR_HEIGHT}px'

  def resizeMobile(self):
    editor_height = self.container_edit.clientHeight + 2 # Border 1 x 2
    menu_height = self.menu.clientHeight + TOOLBAR_HEIGHT
    output_height = self.mainframe.clientHeight - (menu_height + editor_height + SPLITTER_HEIGHT + STATUSBAR_HEIGHT)
    self.mainframe.style.gridTemplateRows = f'{menu_height}px {editor_height}px {SPLITTER_HEIGHT}px {output_height}px {STATUSBAR_HEIGHT}px'

  def on_resize(self, evt):
    if self.is_resizing:
      self.resize(evt)
      evt.preventDefault()

  def on_window_resize(self, evt):
    editor_height = self.container_edit.clientHeight + 2 # Border 1 x 2
    output_height = self.mainframe.clientHeight - (TOOLBAR_HEIGHT + editor_height + SPLITTER_HEIGHT + STATUSBAR_HEIGHT)
    self.mainframe.style.gridTemplateRows = f'{TOOLBAR_HEIGHT}px {editor_height}px {SPLITTER_HEIGHT}px {output_height}px {STATUSBAR_HEIGHT}px'

  def reset_size(self):
    self.mainframe.style.gridTemplateColumns = f'{TOOLBAR_HEIGHT}px 1fr {SPLITTER_HEIGHT}px 1fr {STATUSBAR_HEIGHT}px'

  def on_blur(self, *args):
    self.save()

  def save(self):
    self.config.code = self.editor.getValue()


frame = editor.Frame()
cfg = config.Config(frame.editor)
cfg_dlg = config.Dialog(cfg)
app = App(cfg)

sys.stdout.write = app.write_out
sys.stderr.write = app.write_err
