import webbrowser

def open_browser(porta=9392):
    url = f"http://127.0.0.1:{porta}/"
    webbrowser.open(url)
    print(f"Opening {url} in the browser...")


open_browser()  