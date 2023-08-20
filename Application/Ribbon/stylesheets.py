
stylesheet_instance = None


def get_stylesheet(name):
    global stylesheet_instance
    if not stylesheet_instance:
        stylesheet_instance = Stylesheets()
    return stylesheet_instance.get_stylesheet(name)


class Stylesheets:
    def __init__(self):
        self._stylesheets = {}
        self.make_stylesheet("main", "Application/Ribbon/stylesheets/main.css")
        self.make_stylesheet("ribbon", "Application/Ribbon/stylesheets/ribbon.css")
        self.make_stylesheet("ribbonPane", "Application/Ribbon/stylesheets/ribbonPane.css")
        self.make_stylesheet("ribbonButton", "Application/Ribbon/stylesheets/ribbonButton.css")
        self.make_stylesheet("ribbonSmallButton", "Application/Ribbon/stylesheets/ribbonSmallButton.css")

    def make_stylesheet(self, name, path):
        with open(path) as data_file:
            stylesheet = data_file.read()

        self._stylesheets[name] = stylesheet

    def get_stylesheet(self, name):
        stylesheet = ""
        try:
            stylesheet = self._stylesheets[name]
        except KeyError:
            print("stylesheet " + name + " not found")
        return stylesheet
