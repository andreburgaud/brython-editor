from browser import document, window

if hasattr(window, 'localStorage'):
  from browser.local_storage import storage
else:
  storage = None


DEFAULT_THEME = "ambiance"
DEFAULT_FONT_SIZE = 14
DEFAULT_CODE = '''# This is a Python comment\nprint('Hello Python World!')'''

STORE_EDITOR_CODE = "brython_scratchpad_code"
STORE_EDITOR_THEME = "brython_scratchpad_theme"
STORE_EDITOR_FONT_SIZE = "brython_scratchpad_font_size"


def get_storage_value(key, default_value):
  if storage is not None and key in storage and storage[key]:
    return storage[key]
  return default_value

def set_storage_value(key, value):
    if storage is not None and storage.get(key) != value:
      storage[key] = value


class Config:

    def __init__(self, editor):
        self.editor = editor
        self._font_size = int(get_storage_value(STORE_EDITOR_FONT_SIZE, DEFAULT_FONT_SIZE))
        self._theme = get_storage_value(STORE_EDITOR_THEME, DEFAULT_THEME)
        self._code = get_storage_value(STORE_EDITOR_CODE, DEFAULT_CODE)

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = value
        self.editor.setFontSize(value)
        set_storage_value(STORE_EDITOR_FONT_SIZE, str(value))

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str) -> None:
        self._theme = value
        set_storage_value(STORE_EDITOR_THEME, value)
        self.editor.setTheme(f'ace/theme/{value}')

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        self._code = value
        set_storage_value(STORE_EDITOR_CODE, self._code)


class Dialog:

    def __init__(self, config: Config):
        self.config = config
        self.btn_config = document['btn-config']
        self.btn_close_config = document['btn-close-config']
        self.modal_config = document['modal-config']
        self.sel_theme = document['sel-theme']
        self.input_font_size = document['font-size']
        self.bind_events()

    def bind_events(self):
        self.btn_config.bind('click', self.on_show_config)
        self.btn_close_config.bind('click', self.on_close_config)
        self.input_font_size.bind('change', self.on_font_size_changed)
        self.sel_theme.bind('change', self.on_theme_changed)

    def on_theme_changed(self, evt):
        self.config.theme = [o.value for o in evt.srcElement.options if o.selected][0]

    def on_show_config(self, _):
        self.modal_config.classList.add('is-active')
        for o in self.sel_theme:
            if o.value == self.config.theme:
                o.selected = True

        self.input_font_size.value = self.config.font_size

    def on_close_config(self, _):
        self.modal_config.classList.remove('is-active')

    def on_font_size_changed(self, _):
        self.config.font_size = int(self.input_font_size.value)
