import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2


class CameraViewer(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraViewer, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.camera_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.8))
        self.checkbox_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))

        self.cameras = []
        self.images = []
        self.camera_checkboxes = []
        self.current_camera_index = 0
        self.selected_checkbox = None

        self.button_layout = BoxLayout(size_hint=(1, None), height=50, padding=(10, 0))

        self.button = Button(text="Next Camera", size_hint=(0.5, None), height=50)
        self.button.bind(on_press=self.switch_camera)
        self.button_layout.add_widget(self.button)

        self.submit_button = Button(text="Submit", size_hint=(0.5, None), height=50)
        self.submit_button.bind(on_press=self.submit)
        self.button_layout.add_widget(self.submit_button)

        checkbox_names = ['Right', 'Left', 'Middle', 'Top Left', 'Top Middle', 'Top Right', "Liner"]
        for i, name in enumerate(checkbox_names):
            checkbox_box = BoxLayout(orientation='vertical', size_hint=(None, None), size=(140, 100), padding=(20, 0))
            checkbox = CheckBox(group='cameras', size_hint=(None, None), size=(50, 50), active=i == 0)
            checkbox.number = i + 1
            checkbox.bind(active=self.checkbox_selected)
            label = Label(text=name, size_hint=(None, None), size=(50, 50))
            checkbox_box.add_widget(checkbox)
            checkbox_box.add_widget(label)
            self.camera_checkboxes.append(checkbox)
            self.checkbox_layout.add_widget(checkbox_box)

        self.add_widget(self.camera_layout)
        self.add_widget(self.checkbox_layout)
        self.add_widget(self.button_layout)

    def start_cameras(self):
        camera_indexes = [index for index in range(10)]

        for index in camera_indexes:
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                self.cameras.append(cap)

        for _ in self.cameras:
            image = Image()
            self.images.append(image)
            self.camera_layout.add_widget(image)

        Clock.schedule_interval(self.update_frames, 1 / 30)  # 30 FPS

    def update_frames(self, dt):
        camera = self.cameras[self.current_camera_index]
        ret, frame = camera.read()
        frame = cv2.flip(frame, 0)
        if ret:
            texture = self._frame_to_texture(frame)
            self.images[self.current_camera_index].texture = texture

    def switch_camera(self, instance):
        self.current_camera_index += 1
        if self.current_camera_index >= len(self.cameras):
            self.current_camera_index = 0

        for i, checkbox in enumerate(self.camera_checkboxes):
            checkbox.active = i == self.current_camera_index

    def checkbox_selected(self, checkbox, value):
        if value:
            self.selected_checkbox = checkbox

    def submit(self, instance):
        if self.selected_checkbox:
            print("Selected checkbox:", self.selected_checkbox.number)
        else:
            print("No checkbox selected")

    def _frame_to_texture(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame_rgb.shape
        texture = Texture.create(size=(width, height))
        texture.blit_buffer(frame_rgb.flatten(), colorfmt='rgb', bufferfmt='ubyte')
        return texture


class CameraViewerApp(App):
    def build(self):
        viewer = CameraViewer()
        viewer.start_cameras()
        return viewer


if __name__ == '__main__':
    CameraViewerApp().run()