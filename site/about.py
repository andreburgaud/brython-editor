from browser import document, bind

modal = document['modal-about']

@bind(document['btn-about'], 'click')
def on_about(_):
    modal.classList.add('is-active')

@bind(document['btn-close-about'], 'click')
def on_close_about(_):
    modal.classList.remove('is-active')
