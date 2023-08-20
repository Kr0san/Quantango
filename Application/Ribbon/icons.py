from PyQt6.QtGui import QIcon, QPixmap

icons_instance = None


def get_icon(name):
    global icons_instance
    if not icons_instance:
        icons_instance = Icons()
    return icons_instance.icon(name)


class Icons:
    def __init__(self):
        self._icons = {}
        self.make_icon("app_icon", "Application/Icons/app_icon.png")
        self.make_icon("folder", "Application/Icons/folder.png")
        self.make_icon("open", "Application/Icons/folder.png")
        self.make_icon("save", "Application/Icons/save.png")
        self.make_icon("icon", "Application/Icons/icon.png")
        self.make_icon("exit", "Application/Icons/exit.png")
        self.make_icon("paste", "Application/Icons/paste.png")
        self.make_icon("zoom", "Application/Icons/zoom.png")
        self.make_icon("copy", "Application/Icons/copy.png")
        self.make_icon("about", "Application/Icons/about.png")
        self.make_icon("license", "Application/Icons/license.png")
        self.make_icon("default", "Application/Icons/folder.png")
        self.make_icon("portfolio_list", "Application/Icons/prf_list.png")
        self.make_icon("new_portfolio", "Application/Icons/new_prf.png")
        self.make_icon("delete_portfolio", "Application/Icons/del_prf.png")
        self.make_icon("load_portfolio", "Application/Icons/load_prf.png")
        self.make_icon("time_series", "Application/Icons/time_series.png")
        self.make_icon("options_pricing", "Application/Icons/options_pricing.png")
        self.make_icon("app_logo", "Application/Icons/app_logo.png")
        self.make_icon("new_trade", "Application/Icons/new_trade.png")
        self.make_icon("delete_trade", "Application/Icons/delete_trade.png")
        self.make_icon("import_trades", "Application/Icons/import_trades.png")
        self.make_icon("export_trades", "Application/Icons/export_trades.png")
        self.make_icon("subscribe_funds", "Application/Icons/plus.png")
        self.make_icon("redeem_funds", "Application/Icons/minus.png")

    def make_icon(self, name, path):
        icon = QIcon()
        icon.addPixmap(QPixmap(path), QIcon.Mode.Normal, QIcon.State.Off)
        self._icons[name] = icon

    def icon(self, name):
        icon = self._icons["default"]
        try:
            icon = self._icons[name]
        except KeyError:
            print("icon " + name + " not found")
        return icon
