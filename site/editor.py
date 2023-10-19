from browser import window

DEFAULT_EDITOR_MODE = 'ace/mode/python'
ACE_BASE_PATH = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.14.0'

class Frame:
  def __init__(self):
    window.ace.config.set('basePath', ACE_BASE_PATH)
    self.editor = window.ace.edit('container-edit')
    self.init_editor()

  def init_editor(self):
    session = self.editor.getSession()
    session.setMode(DEFAULT_EDITOR_MODE)
    self.editor.setOptions({
      'enableLiveAutocompletion': True,
      'enableSnippets': True,
      'highlightActiveLine': True,
      'highlightSelectedWord': True
    })
    self.editor.scrollToRow(0)
    self.editor.gotoLine(0)
