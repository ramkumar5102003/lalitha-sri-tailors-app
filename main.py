from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
import datetime
import os
import json
import platform

# --- CONFIGURATION ---
SHOP_NAME = "లలిత శ్రీ టైలర్స్"
SHOP_ADDRESS = "షాప్ నెం:30, కరాచీ సెంటర్, మండపేట"
SHOP_MOBILE = "+91 95023 84443"
HISTORY_FILE = "receipt_history.json"

# --- THEME COLORS (Red & Gold Style) ---
COLOR_PRIMARY = get_color_from_hex('#D32F2F')  # Deep Red
COLOR_ACCENT = get_color_from_hex('#FFD700')   # Gold
COLOR_BG = get_color_from_hex('#F5F5F5')       # Light Gray
COLOR_CARD = get_color_from_hex('#FFFFFF')     # White
COLOR_TEXT = get_color_from_hex('#212121')     # Black

# --- FONT SETUP ---
if os.path.exists('NotoSansTelugu-Regular.ttf'):
    APP_FONT = 'NotoSansTelugu-Regular.ttf'
else:
    APP_FONT = 'Roboto'  # Fallback

class ReceiptApp(App):
    def build(self):
        Window.clearcolor = COLOR_BG
        self.cart = {}
        
        # Permissions
        if platform.system() == 'Android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE, 
                    Permission.READ_EXTERNAL_STORAGE
                ])
            except:
                pass

        self.items = [
            "పెద్ద షర్ట్", "పెద్ద ఫ్యాంటు", "పెద్ద నిక్కర్",
            "కుర్తా", "స్కూల్ యూనిఫామ్", "చిన్న షర్టు",
            "చిన్న ఫ్యాంటు", "చిన్న నిక్కర్", "ఇతర ఆల్టరేషన్స్"
        ]

        self.sm = ScreenManager()
        
        # 1. SPLASH SCREEN (Logo Only)
        self.splash_screen = Screen(name='splash')
        splash_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        if os.path.exists('logo.png'):
            img = Image(source='logo.png', size_hint=(0.6, 0.6))
            splash_layout.add_widget(img)
        else:
            splash_layout.add_widget(Label(text="Loading...", font_size='24sp', color=COLOR_TEXT))
        
        self.splash_screen.add_widget(splash_layout)
        self.sm.add_widget(self.splash_screen)

        # 2. HOME SCREEN
        self.home_screen = Screen(name='home')
        self.setup_home_screen()
        self.sm.add_widget(self.home_screen)

        # 3. HISTORY SCREEN
        self.hist_screen = Screen(name='history')
        self.setup_history_screen()
        self.sm.add_widget(self.hist_screen)

        # Auto-switch to home after 2 seconds
        Clock.schedule_once(self.switch_to_home, 2)
        return self.sm

    def switch_to_home(self, dt):
        self.sm.current = 'home'

    def setup_home_screen(self):
        # Main Layout with Padding (Desktop Frame Look)
        root = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # --- CARD FRAME (White Box on Gray BG) ---
        with root.canvas.before:
            Color(*COLOR_CARD)
            self.rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._update_rect, pos=self._update_rect)

        # HEADER
        header = BoxLayout(size_hint_y=0.18, spacing=10)
        if os.path.exists('logo.png'):
            header.add_widget(Image(source='logo.png', size_hint_x=0.3))
        
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=SHOP_NAME, font_name=APP_FONT, font_size='22sp', bold=True, color=COLOR_PRIMARY))
        info.add_widget(Label(text=SHOP_ADDRESS, font_name=APP_FONT, font_size='12sp', color=COLOR_TEXT))
        info.add_widget(Label(text=SHOP_MOBILE, font_name=APP_FONT, font_size='12sp', color=COLOR_TEXT))
        header.add_widget(info)
        
        # History Button (Styled)
        btn_hist = Button(text="History", background_color=COLOR_PRIMARY, size_hint_x=0.25, font_size='12sp')
        btn_hist.bind(on_press=self.show_history)
        header.add_widget(btn_hist)
        root.add_widget(header)

        # CUSTOMER DETAILS
        inputs = BoxLayout(size_hint_y=0.1, spacing=10)
        self.cust_name = TextInput(hint_text="Customer Name", font_name=APP_FONT, multiline=False)
        self.cust_mobile = TextInput(hint_text="Mobile No", input_filter='int', multiline=False)
        inputs.add_widget(self.cust_name)
        inputs.add_widget(self.cust_mobile)
        root.add_widget(inputs)

        # ITEM LIST HEADERS
        heads = BoxLayout(size_hint_y=None, height=40)
        heads.add_widget(Label(text="Sel", size_hint_x=0.15, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Item Name", size_hint_x=0.45, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Qty", size_hint_x=0.2, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Price", size_hint_x=0.2, color=COLOR_TEXT, bold=True))
        root.add_widget(heads)

        # SCROLLABLE ITEMS
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for item in self.items:
            row = BoxLayout(size_hint_y=None, height=50)
            chk = CheckBox(size_hint_x=0.15, color=COLOR_TEXT)
            chk.bind(active=self.on_check)
            
            lbl = Label(text=item, font_name=APP_FONT, size_hint_x=0.45, color=COLOR_TEXT, halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            qty = TextInput(text='1', disabled=True, size_hint_x=0.2, opacity=0.3, input_filter='int', halign='center')
            rate = TextInput(hint_text='0', disabled=True, size_hint_x=0.2, opacity=0.3, input_filter='int', halign='center')
            
            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(qty)
            row.add_widget(rate)
            grid.add_widget(row)
            self.cart[chk] = {'name': item, 'qty': qty, 'rate': rate}

        scroll.add_widget(grid)
        root.add_widget(scroll)

        # GENERATE BUTTON
        btn_gen = Button(text="GENERATE BILL", font_name=APP_FONT, size_hint_y=0.1, background_color=COLOR_PRIMARY, font_size='18sp', bold=True)
        btn_gen.bind(on_press=self.generate_bill)
        root.add_widget(btn_gen)

        self.home_screen.add_widget(root)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def setup_history_screen(self):
        root = BoxLayout(orientation='vertical', padding=10)
        # Back Button
        top = BoxLayout(size_hint_y=0.1)
        btn = Button(text="< Back", size_hint_x=0.3, on_press=lambda x: setattr(self.sm, 'current', 'home'))
        top.add_widget(btn)
        top.add_widget(Label(text="History", color=COLOR_TEXT, bold=True, font_size='20sp'))
        root.add_widget(top)
        
        self.hist_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.hist_container.bind(minimum_height=self.hist_container.setter('height'))
        root.add_widget(ScrollView(children=[self.hist_container]))
        self.hist_screen.add_widget(root)

    def on_check(self, chk, val):
        self.cart[chk]['qty'].disabled = not val
        self.cart[chk]['rate'].disabled = not val
        self.cart[chk]['qty'].opacity = 1 if val else 0.3
        self.cart[chk]['rate'].opacity = 1 if val else 0.3

    def generate_bill(self, instance):
        # 1. Calculate Data
        items = []
        total = 0
        for chk, data in self.cart.items():
            if chk.active:
                try:
                    q = float(data['qty'].text or 0)
                    r = float(data['rate'].text or 0)
                    if q > 0 and r > 0:
                        amt = q * r
                        total += amt
                        items.append((data['name'], int(q), int(amt)))
                except: pass
        
        if not items: return

        # 2. Create Popup Content (White Paper Look)
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        with content.canvas.before:
            Color(1, 1, 1, 1) # White Paper
            Rectangle(pos=content.pos, size=content.size)
        
        # Logo in Receipt
        if os.path.exists('logo.png'):
            content.add_widget(Image(source='logo.png', size_hint_y=None, height=80))

        # Receipt Text (Using Markup for Color)
        txt = f"[b][color=#D32F2F]{SHOP_NAME}[/color][/b]\n"
        txt += f"[color=000000]{SHOP_ADDRESS}\nPh: {SHOP_MOBILE}[/color]\n\n"
        txt += f"[color=000000]Name: {self.cust_name.text}\nDate: {datetime.datetime.now().strftime('%d-%m-%Y')}[/color]\n"
        txt += "[color=000000]---------------------------------------[/color]\n"
        
        for name, q, amt in items:
            # Formatting to align text
            txt += f"[color=000000]{name} (x{q}) : Rs.{amt}[/color]\n"
            
        txt += "[color=000000]---------------------------------------[/color]\n"
        txt += f"[b][color=#D32F2F]TOTAL: Rs. {int(total)}[/color][/b]\n"
        txt += "[color=000000]Thank You![/color]"

        lbl = Label(text=txt, markup=True, font_name=APP_FONT, color=COLOR_TEXT)
        content.add_widget(lbl)

        # Buttons
        btns = BoxLayout(size_hint_y=0.2, spacing=10)
        btn_cls = Button(text="Close", background_color=(0.5,0.5,0.5,1))
        
        # Share Button (Green)
        btn_share = Button(text="SHARE RECEIPT", background_color=(0,0.8,0,1))
        
        self.popup = Popup(title="", separator_height=0, content=content, size_hint=(0.9, 0.85), background='white_pixel.png')
        # Hack to make popup background white if image missing
        self.popup.background_color = (1,1,1,1)
        
        btn_cls.bind(on_press=self.popup.dismiss)
        btn_share.bind(on_press=lambda x: self.share_screenshot(content))
        
        btns.add_widget(btn_cls)
        btns.add_widget(btn_share)
        content.add_widget(btns)
        
        self.popup.open()
        
        # Save to History
        self.save_history(self.cust_name.text, total, txt)
        
        # Reset
        self.cust_name.text = ""
        self.cust_mobile.text = ""
        for chk in self.cart: chk.active = False

    def share_screenshot(self, widget_content):
        # 1. Export widget to PNG
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        filename = f"Bill_{timestamp}.png"
        path = os.path.join(self.user_data_dir, filename)
        
        widget_content.export_to_png(path)
        
        # 2. Share via Android
        try:
            from plyer import share
            share.share_file(path)
        except Exception as e:
            print(f"Share failed: {e}")

    def save_history(self, name, total, text):
        data = {'name': name, 'date': datetime.datetime.now().strftime('%d-%m'), 'total': total, 'text': text}
        try:
            hist = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f: hist = json.load(f)
            hist.insert(0, data)
            with open(HISTORY_FILE, 'w') as f: json.dump(hist, f)
        except: pass

    def show_history(self, instance):
        self.hist_container.clear_widgets()
        self.sm.current = 'history'
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                for item in json.load(f):
                    btn = Button(text=f"{item['date']} - {item['name']} - Rs.{item['total']}", size_hint_y=None, height=60, font_name=APP_FONT)
                    self.hist_container.add_widget(btn)

if __name__ == '__main__':
    ReceiptApp().run()
