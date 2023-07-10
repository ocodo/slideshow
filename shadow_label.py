import pyglet

class ShadowLabel:
    def __init__(self, text, x, y, font_name='Arial', font_size=14,
                 opacity=255, color=(255,255,255,255), shadow_color=(0,0,0,127),
                 offset_x=2, offset_y=-2,
                 anchor_x='center', anchor_y='center'):
        self._text = text
        self._x = x
        self._y = y
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._opacity = opacity
        self.main_label = pyglet.text.Label(
            self._text,
            font_name=font_name,
            font_size=font_size,
            x=self._x,
            y=self._y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = color
        )
        self.shadow_label = pyglet.text.Label(
            self._text,
            font_name = font_name,
            font_size = font_size,
            x = self._x + self._offset_x,
            y = self._x + self._offset_y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color=shadow_color
        )

    def show(self, message):
        self.text = message
        self.opacity = 255

    def hide(self):
        self.opacity = 0

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.main_label.opacity = value
        self.shadow_label.opacity = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.main_label.text = value
        self.shadow_label.text = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.main_label.x = value
        self.shadow_label.x = value + self._x_offset

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.main_label.y = value
        self.shadow_label.y = value + self._y_offset

    def draw(self):
        self.shadow_label.draw()
        self.main_label.draw()
