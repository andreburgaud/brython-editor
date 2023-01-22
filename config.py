from browser import document

class Config:
    def __init__(self, app):
        self.app = app
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
        theme = [o.value for o in evt.srcElement.options if o.selected][0]
        self.app.set_theme(theme)

    def on_show_config(self, _):
        self.modal_config.classList.add('is-active')
        for o in self.sel_theme:
            if o.value == self.app.theme:
                o.selected = True

        self.input_font_size.value = self.app.font_size

    def on_close_config(self, _):
        self.modal_config.classList.remove('is-active')

    def on_font_size_changed(self, _):
        self.app.set_font_size(int(self.input_font_size.value))
