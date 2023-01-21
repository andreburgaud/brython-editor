import sys, time
from browser import worker, document, html, timer, window
from browser.widgets.dialog import InfoDialog

if hasattr(window, 'localStorage'):
  from browser.local_storage import storage
else:
  storage = None

CODE_EXAMPLE = '''# This is a Python comment\nprint('Hello Python World!')'''

class App:
  MIN_WIDTH_EDITOR = 150
  MIN_WIDTH_OUTPUT = 100
  SPLITTER_WIDTH = 8
  EXECUTOR = False
  LIGHT_THEME = "ace/theme/chrome"
  #DARK_THEME = "ace/theme/chaos"
  DARK_THEME = "ace/theme/ambiance"
  STORE_EDITOR_CODE = "brython_scratchpad_code"
  STORE_EDITOR_THEME = "brython_scratchpad_theme"

  def __init__(self, editor):
    self.is_resizing = False
    self.editor = editor
    self.init_code()
    self.session = editor.getSession()
    self.mainframe = document['mainframe']
    self.toolbar = document['toolbar']
    self.container_edit = document['container-edit']
    self.splitter = document['splitter']
    self.output = document['output']
    self.stb_status = document['stb-status']
    self.btn_run = document['btn-run']

    self.btn_clear = document['btn-clear']
    self.btn_theme = document['btn-theme']
    self.btn_reset = document['btn-reset']
    self.btn_about = document['btn-about']
    self.btn_close_about = document['btn-close-about']
    self.modal_about = document['modal-about']

    if App.EXECUTOR:
      self.btn_terminate = document['btn-terminate']
      self.executor = self.create_executor()
      self.create_executor()

    self.bind_events()
    self.init_theme()

  def init_code(self):
    if storage is not None and App.STORE_EDITOR_CODE in storage and storage[App.STORE_EDITOR_CODE]:
      self.editor.setValue(storage[App.STORE_EDITOR_CODE])
    else:
      self.editor.setValue(CODE_EXAMPLE)
    self.editor.scrollToRow(0)
    self.editor.gotoLine(0)

  def init_theme(self):
    if storage is not None and App.STORE_EDITOR_THEME in storage:
      self.update_theme_button(storage[App.STORE_EDITOR_THEME])
    else:
      self.update_theme_button(App.DARK_THEME)


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

  def reset_code(self):
    self.editor.setValue(CODE_EXAMPLE)

  def on_reset(self, evt):
    self.reset_code()
    self.reset_size()
    self.clear_output()
    self.clear_status()

  def on_about(self, evt):
    self.modal_about.classList.add('is-active')
    self.modal_about.classList.add('is-clipped')

  def on_close_about(self, evt):
    self.modal_about.classList.remove('is-active')

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
      if App.EXECUTOR:
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
    if App.EXECUTOR:
      self.btn_terminate.bind('click', self.on_terminate)
    self.btn_theme.bind('click', self.toggle_theme)
    self.btn_reset.bind('click', self.on_reset)
    self.btn_clear.bind('click', self.on_clear)
    self.btn_about.bind('click', self.on_about)
    self.btn_close_about.bind('click', self.on_close_about)
    self.editor.bind('blur', self.on_blur)
    window.onresize = self.on_window_resize
    window.onmouseup = self.end_resize

  def start_resize(self, evt):
    self.is_resizing = True
    #self.mainframe.style.cursor = 'col-resize'
    self.splitter.style.cursor = 'col-resize'

  def end_resize(self, evt):
    if self.is_resizing:
      self.is_resizing = False
      self.splitter.style.cursor = 'ew-resize'

  def resize(self, evt):
    if evt.clientX > self.mainframe.clientWidth - App.MIN_WIDTH_OUTPUT:
      editor_width = self.mainframe.clientWidth - App.MIN_WIDTH_OUTPUT
    elif evt.clientX < App.MIN_WIDTH_EDITOR:
      editor_width = App.MIN_WIDTH_EDITOR
    else:
      editor_width = evt.clientX
    output_width = self.mainframe.clientWidth - (editor_width + App.SPLITTER_WIDTH)
    self.mainframe.style.gridTemplateColumns = f'{editor_width}px {App.SPLITTER_WIDTH}px {output_width}px'

  def on_resize(self, evt):
    if self.is_resizing:
      self.resize(evt)
      evt.preventDefault()

  def on_window_resize(self, evt):
    editor_width = self.container_edit.clientWidth + 2 # Border 1 x 2
    output_width = self.mainframe.clientWidth - (App.SPLITTER_WIDTH + editor_width)
    self.mainframe.style.gridTemplateColumns = f'{editor_width}px {App.SPLITTER_WIDTH}px {output_width}px'

  def reset_size(self):
    self.mainframe.style.gridTemplateColumns = f'1fr {App.SPLITTER_WIDTH}px 1fr'

  def on_blur(self, *args):
    self.save()

  def save(self):
    code = self.editor.getValue()
    if storage is not None and storage.get(App.STORE_EDITOR_CODE) != code:
      storage[App.STORE_EDITOR_CODE] = code

  def update_theme_button(self, theme):
    self.editor.setTheme(theme)
    self.btn_theme.text = 'Dark' if theme == App.LIGHT_THEME else "Light"

  def toggle_theme(self, evt):
    theme = App.DARK_THEME
    if self.editor.getTheme() == theme:
        theme = App.LIGHT_THEME
    self.update_theme_button(theme)
    if storage is not None:
       storage[App.STORE_EDITOR_THEME] = theme

class EditorFrame:
  def __init__(self):
    window.ace.config.set('basePath', 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11')
    self.editor = window.ace.edit('container-edit')
    self.init_editor()

  def init_editor(self):
    session = self.editor.getSession()
    session.setMode("ace/mode/python")
    self.editor.setFontSize(14)
    self.editor.setOptions({
      'enableLiveAutocompletion': True,
      'enableSnippets': True,
      'highlightActiveLine': True,
      'highlightSelectedWord': True
    })
    self.editor.scrollToRow(0)
    self.editor.gotoLine(0)


editor_frame = EditorFrame()
app = App(editor_frame.editor)
sys.stdout.write = app.write_out
sys.stderr.write = app.write_err
