import sys, time
from browser import worker, document, timer, window
import storage
import about # about binding initializiation
import config
import editor

CODE_EXAMPLE = '''# This is a Python comment\nprint('Hello Python World!')'''
MIN_WIDTH_EDITOR = 150
MIN_WIDTH_OUTPUT = 100
SPLITTER_WIDTH = 8
EXECUTOR = False
DEFAULT_THEME = "ambiance"
DEFAULT_FONT_SIZE = 14
STORE_EDITOR_CODE = "brython_scratchpad_code"
STORE_EDITOR_THEME = "brython_scratchpad_theme"
STORE_EDITOR_FONT_SIZE = "brython_scratchpad_font_size"

class App:

  def __init__(self, editor):
    self.theme = DEFAULT_THEME
    self.font_size = DEFAULT_FONT_SIZE
    self.is_resizing = False
    self.editor = editor
    self.init_editor()
    self.session = editor.getSession()
    self.mainframe = document['mainframe']
    self.toolbar = document['toolbar']
    self.container_edit = document['container-edit']
    self.splitter = document['splitter']
    self.output = document['output']
    self.stb_status = document['stb-status']

    self.btn_run = document['btn-run']
    self.btn_clear = document['btn-clear']

    self.burger = document['burger']
    self.menu = document['menu']

    if EXECUTOR:
      self.btn_terminate = document['btn-terminate']
      self.executor = self.create_executor()
      self.create_executor()

    self.bind_events()

  def init_editor(self):
    code = storage.get_value(STORE_EDITOR_CODE, CODE_EXAMPLE)
    self.editor.setValue(code)

    font_size = storage.get_value(STORE_EDITOR_FONT_SIZE, DEFAULT_FONT_SIZE)
    self.set_font_size(int(font_size))

    theme = storage.get_value(STORE_EDITOR_THEME, DEFAULT_THEME)
    self.set_theme(theme)

    self.editor.scrollToRow(0)
    self.editor.gotoLine(0)

  def set_theme(self, theme):
    self.editor.setTheme(f'ace/theme/{theme}')
    storage.set_value(STORE_EDITOR_THEME, theme)
    self.theme = theme

  def set_font_size(self, font_size):
    # TODO: consider updating output pane font size
    self.editor.setFontSize(font_size)
    storage.set_value(STORE_EDITOR_FONT_SIZE, str(font_size))
    self.font_size = font_size

  def create_executor(self):
    w = worker.Worker('worker')
    w.bind('message', self.on_message)
    return w

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

  def on_terminate(self, evt):
    print("Kill the executor")
    self.executor.terminate()
    self.executor = self.create_executor()

  def on_message(self, evt):
    """Message from executor worker"""
    print(evt.data)

  def exec_code(self):
    src = self.editor.getValue()
    line_count = len(src.split('\n'))
    t0 = time.perf_counter()

    try:
      if EXECUTOR:
        self.executor.send(src)
      else:
        ns = {'__name__':'__main__'}
        exec(src, ns)

    except SyntaxError as err:
      self.handle_syntax_error(line_count)

    except Exception as exc:
      self.handle_error(line_count)

    except:
      # TODO
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

  def bind_events(self):
    self.splitter.bind('mousedown', self.start_resize)
    self.mainframe.bind('mousemove', self.on_resize)
    self.btn_run.bind('click', self.on_run)
    if EXECUTOR:
      self.btn_terminate.bind('click', self.on_terminate)
    self.btn_clear.bind('click', self.on_clear)

    self.editor.bind('blur', self.on_blur)
    window.onresize = self.on_window_resize
    window.onmouseup = self.end_resize

    self.burger.bind('click', self.on_burger)

  def on_burger(self, evt):
    self.menu.classList.toggle('is-active')
    self.burger.classList.toggle('is-active')

  def start_resize(self, evt):
    self.is_resizing = True
    #self.mainframe.style.cursor = 'col-resize'
    self.splitter.style.cursor = 'col-resize'

  def end_resize(self, evt):
    if self.is_resizing:
      self.is_resizing = False
      self.splitter.style.cursor = 'ew-resize'

  def resize(self, evt):
    if evt.clientX > self.mainframe.clientWidth - MIN_WIDTH_OUTPUT:
      editor_width = self.mainframe.clientWidth - MIN_WIDTH_OUTPUT
    elif evt.clientX < MIN_WIDTH_EDITOR:
      editor_width = MIN_WIDTH_EDITOR
    else:
      editor_width = evt.clientX
    output_width = self.mainframe.clientWidth - (editor_width + SPLITTER_WIDTH)
    self.mainframe.style.gridTemplateColumns = f'{editor_width}px {SPLITTER_WIDTH}px {output_width}px'

  def on_resize(self, evt):
    if self.is_resizing:
      self.resize(evt)
      evt.preventDefault()

  def on_window_resize(self, evt):
    editor_width = self.container_edit.clientWidth + 2 # Border 1 x 2
    output_width = self.mainframe.clientWidth - (SPLITTER_WIDTH + editor_width)
    self.mainframe.style.gridTemplateColumns = f'{editor_width}px {SPLITTER_WIDTH}px {output_width}px'

  def reset_size(self):
    self.mainframe.style.gridTemplateColumns = f'1fr {SPLITTER_WIDTH}px 1fr'

  def on_blur(self, *args):
    self.save()

  def save(self):
    code = self.editor.getValue()
    storage.set_value(STORE_EDITOR_CODE, code)

editor_frame = editor.Frame()
app = App(editor_frame.editor)
config.Config(app)
sys.stdout.write = app.write_out
sys.stderr.write = app.write_err
