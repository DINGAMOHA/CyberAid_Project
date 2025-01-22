from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy_garden.mapview import MapView, MapMarker
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from datetime import datetime
from plyer import gps

class CustomMarker(MapMarker):
    def __init__(self, location_name=None, **kwargs):
        super().__init__(**kwargs)
        self.location_name = location_name

    def on_release(self):
        # Show location name when marker is clicked
        if self.location_name:
            content = BoxLayout(orientation='vertical', padding=dp(10))
            content.add_widget(Label(
                text=self.location_name,
                size_hint_y=None,
                height=dp(40)
            ))
            
            dismiss_button = Button(
                text='Close',
                size_hint_y=None,
                height=dp(40)
            )
            content.add_widget(dismiss_button)
            
            popup = Popup(
                title='Location Information',
                content=content,
                size_hint=(None, None),
                size=(dp(300), dp(150))
            )
            
            dismiss_button.bind(on_press=popup.dismiss)
            popup.open()

class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize safety instructions dictionary
        self.safety_instructions = {
            'Medical': [
                "1. Check if person is breathing and conscious",
                "2. If not breathing, start CPR",
                "3. Control any severe bleeding",
                "4. Keep the person still and comfortable",
                "5. Monitor vital signs until help arrives",
                "6. Call nearest hospital"
            ],
            'Fire': [
                "1. Alert everyone in the building",
                "2. Call Civil Defense",
                "3. Stay low under smoke",
                "4. Test doors for heat before opening",
                "5. Dont use elivators and Use stairs",
                "6. stay outside building"
            ],
            'Accident': [
                "1. Stay away from the scene",
                "2. Ensure scene is safe to approach",
                "3. Call emergency services",
                "4. Help injured people",
                "5. Stay with victims until help arrives"
            ],
            'Natural': [
                "1. Move to higher ground (flood) or open area",
                "2. Call Civil Defense",
                "3. Stay away from windows and exterior walls",
                "4. Take cover under sturdy furniture",
                "5. Listen to emergency broadcasts",
                "6. Follow evacuation orders immediately"
            ],
            'Other': [
                "1. Stay calm and assess the situation",
                "2. Call emergency services",
                "3. Move to a safe location",
                "4. Follow official instructions",
                "5. Help others if safe to do so",
                "6. Wait for professional help"
            ]
        }
        
        self.layout = BoxLayout(orientation='vertical')
        
        # toolbar with SOS button
        toolbar = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(5)],
            spacing=dp(5)
        )
        
        # Large SOS button
        sos_btn = Button(
            text='SOS',
            background_color=get_color_from_hex('#FF0000'),
            size_hint_x=0.7,
            font_size=dp(24),
            on_press=self.show_sos_options
        )
        
        # Help button
        help_btn = Button(
            text='Help',
            background_color=get_color_from_hex('#4CAF50'),
            size_hint_x=0.3,
            on_press=self.show_help
        )
        
        toolbar.add_widget(sos_btn)
        toolbar.add_widget(help_btn)
        
        # Initialize map centered on Qatar
        self.map_view = MapView(
            zoom=10,  # Adjusted zoom level for better view of Qatar
            lat=25.2867,  # Qatar's central latitude
            lon=51.5333,  # Qatar's central longitude
            map_source="osm",
            double_tap_zoom=True
        )
        
        # Add Civil Defence locations in Qatar
        self.civil_defence = [
            ("Al Wakra Civil Defence Centre", 25.167286783725615, 51.59788954012661),
            ("Civil Defence Al aziza Station", 25.27932, 51.52245),
            ("Messaimeer Civil Defence Centre", 25.2301, 51.4756),
            ("Al Rayyan Civil Defence Station", 25.2919, 51.4244)
        ]
        
        # Add markers for hospitals in Qatar
        self.hospitals = [
            ("Hamad General Hospital", 25.293504324034192, 51.50265152131469),
            ("Al Khor Hospital", 25.71548743109155, 51.51599019077857),
            ("Al Wakra Hospital", 25.166964140311638, 51.58805186113402),
            ("Cuban Hospital", 25.438222530650425, 50.85931514600575),
            ("Sidra Medicine", 25.32256938808695, 51.44510612875868)
        ]
        
        # hospital markers
        for hospital_name, lat, lon in self.hospitals:
            marker = CustomMarker(
                location_name=hospital_name,
                lat=lat,
                lon=lon,
                source='atlas://data/images/defaulttheme/button_pressed',
                color='blue'
            )
            self.map_view.add_marker(marker)
        
        # Civil Defence markers 
        for cd_name, lat, lon in self.civil_defence:
            marker = CustomMarker(
                location_name=cd_name,
                lat=lat,
                lon=lon,
                source='atlas://data/images/defaulttheme/button_pressed',
                color='red'
            )
            self.map_view.add_marker(marker)
        
        self.layout.add_widget(toolbar)
        self.layout.add_widget(self.map_view)
        
        # Status bar
        status_bar = BoxLayout(
            size_hint_y=None,
            height=dp(30),
            padding=[dp(5)]
        )
        self.status_label = Label(
            text='Press SOS for Emergency Assistance',
            color=get_color_from_hex('#FFFFFF')
        )
        status_bar.add_widget(self.status_label)
        self.layout.add_widget(status_bar)
        
        self.add_widget(self.layout)
        self.emergency_markers = []

    def show_safety_instructions(self, emergency_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        
        # scrollable tab
        scroll = ScrollView(size_hint=(1, 0.8))
        instructions_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        instructions_layout.bind(minimum_height=instructions_layout.setter('height'))
        
        # Add title
        title_label = Label(
            text=f'SAFETY INSTRUCTIONS FOR {emergency_type.upper()} EMERGENCY',
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex('#FF0000')
        )
        instructions_layout.add_widget(title_label)
        
        # Add instructions
        for instruction in self.safety_instructions[emergency_type]:
            inst_label = Label(
                text=instruction,
                size_hint_y=None,
                height=dp(40),
                text_size=(dp(280), None),
                halign='left'
            )
            instructions_layout.add_widget(inst_label)
        
        scroll.add_widget(instructions_layout)
        content.add_widget(scroll)
        
        # Add buttons
        buttons_layout = BoxLayout(
            size_hint_y=0.2,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        # Proceed button
        proceed_btn = Button(
            text='Send SOS',
            background_color=get_color_from_hex('#FF0000'),
            size_hint_x=0.5
        )
        proceed_btn.bind(on_press=lambda x: self.send_sos(emergency_type))
        
        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            background_color=get_color_from_hex('#666666'),
            size_hint_x=0.5
        )
        
        buttons_layout.add_widget(proceed_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        # show popup
        self.instructions_popup = Popup(
            title='EMERGENCY INSTRUCTIONS',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        cancel_btn.bind(on_press=self.instructions_popup.dismiss)
        self.instructions_popup.open()
    
    def show_sos_options(self, instance):
        content = GridLayout(cols=2, padding=dp(10), spacing=dp(10))
        
        categories = [
            ('Medical', '#FF0000'),
            ('Fire', '#FF4500'),
            ('Accident', '#FF8C00'),
            ('Natural', '#8B0000'),
            ('Other', '#800080')
        ]
        
        for cat, color in categories:
            btn = Button(
                text=cat,
                background_color=get_color_from_hex(color),
                size_hint_y=None,
                height=dp(60)
            )
            btn.bind(on_press=lambda btn=btn: self.show_safety_instructions(btn.text))
            content.add_widget(btn)
        
        self.sos_popup = Popup(
            title='SELECT EMERGENCY TYPE',
            content=content,
            size_hint=(0.8, 0.6)
        )
        self.sos_popup.open()
    
    def send_sos(self, emergency_type):  
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(
            text='SOS SIGNAL SENT\n\n'
                'Emergency services have been notified.\n'
                'Follow the safety instructions provided.\n'
                'Stay calm and wait for assistance.',
            halign='center'
        ))
        
        dismiss_button = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(dismiss_button)
        
        popup = Popup(
            title='Help',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(300))
        )
        
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()
    
    
    def show_help(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(
            text='How to use\n\n'
                '1. Press the RED SOS button for emergency\n'
                '2. Select emergency type\n'
                '3. Read and follow safety instructions\n'
                '4. Confirm to send SOS alert\n'
                '5. Your location will be marked\n'
                '6. Stay safe and wait for help\n\n',
            halign='center'
        ))
        
        dismiss_button = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(dismiss_button)
        
        popup = Popup(
            title='Help',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(300))
        )
        
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()

class CyberAidApp(App):
    def build(self):
        # Set app title
        self.title = 'CyberAid'
        
        # Create and return screen manager
        sm = ScreenManager()
        sm.add_widget(MapScreen(name='map'))
        return sm

if __name__ == '__main__':
    CyberAidApp().run()