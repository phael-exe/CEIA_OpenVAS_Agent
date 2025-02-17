import webbrowser

class BrowserAgent:
    def __init__(self):
        pass

    def open_browser(self, port=9392):
        url = f"http://127.0.0.1:{port}/"
        webbrowser.open(url)
        print(f"Opening {url} in the browser...")



if __name__ == "__main__":
    test = BrowserAgent()
    test.open_browser()