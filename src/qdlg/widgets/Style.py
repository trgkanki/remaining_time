class Style:
    margin = None

    def margin(self, vertical, horizontal=None):
        if horizontal is None:
            horizontal = vertical
        self.margin = (horizontal, vertical)


class StylableWidget:
    def apply(style):
        if style.margin:
            horizontal, vertical = style.margin
            self.widget.setContentsMargins(horizontal, vertical, horizontal, vertical)
