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

# --- THEME COLORS ---
COLOR_PRIMARY = get_color_from_hex('#D32F2F')  
COLOR_ACCENT = get_color_from_hex('#FFD700')   
COLOR_BG = get_color_from_hex('#F5F5F5')       
COLOR_CARD = get_color_from_hex('#FFFFFF')     
COLOR_TEXT = get_color_from_hex('#212121')     

if os.path.exists('NotoSansTelugu-Regular.ttf'):
    APP_FONT = 'NotoSansTelugu-Regular.ttf'
else:
    APP_FONT = None

# Helper to apply Telugu font strictly to Telugu text (Prevents English Boxes)
def _T(text):
    if APP_FONT:
        return f"[font={APP_FONT}]{text}[/font]"
    return text


# --- CUSTOM BACKGROUND FOR RECEIPT (Sky Blue + Watermark) ---
class ReceiptLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        with self.canvas.before:
            # 1. Sky Blue Background
            Color(*get_color_from_hex('#E1F5FE')) # Light Sky Blue Color
            self.bg_rect = Rectangle()
            
            # 2. Tailor Materials Watermark (Low Opacity)
            if os.path.exists('watermark.png'):
                Color(1, 1, 1, 0.15) # 15% Opacity (Very light)
                self.wm_rect = Rectangle(source='watermark.png')
            else:
                self.wm_rect = None
                
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if self.wm_rect:
            self.wm_rect.pos = self.pos
            self.wm_rect.size = self.size


class ReceiptApp(App):
    def build(self):
        Window.clearcolor = COLOR_BG
        self.cart = {}
        
        if platform.system() == 'Android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            except: pass

        self.items = [
            "పెద్ద షర్ట్", "పెద్ద ఫ్యాంటు", "పెద్ద నిక్కర్",
            "కుర్తా", "స్కూల్ యూనిఫామ్", "చిన్న షర్టు",
            "చిన్న ఫ్యాంటు", "చిన్న నిక్కర్", "ఇతర ఆల్టరేషన్స్"
        ]

        self.sm = ScreenManager()
        
        # SPLASH SCREEN
        self.splash_screen = Screen(name='splash')
        splash_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        if os.path.exists('logo.png'):
            splash_layout.add_widget(Image(source='logo.png', size_hint=(0.6, 0.6)))
        self.splash_screen.add_widget(splash_layout)
        self.sm.add_widget(self.splash_screen)

        # HOME SCREEN
        self.home_screen = Screen(name='home')
        self.setup_home_screen()
        self.sm.add_widget(self.home_screen)

        # HISTORY SCREEN
        self.hist_screen = Screen(name='history')
        self.setup_history_screen()
        self.sm.add_widget(self.hist_screen)

        Clock.schedule_once(lambda dt: setattr(self.sm, 'current', 'home'), 2)
        return self.sm

    def setup_home_screen(self):
        root = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        with root.canvas.before:
            Color(*COLOR_CARD)
            self.rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._update_rect, pos=self._update_rect)

        # HEADER
        header = BoxLayout(size_hint_y=0.18, spacing=10)
        if os.path.exists('logo.png'):
            header.add_widget(Image(source='logo.png', size_hint_x=0.3))
        
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=_T(SHOP_NAME), markup=True, font_size='24sp', bold=True, color=COLOR_PRIMARY))
        info.add_widget(Label(text=_T(SHOP_ADDRESS), markup=True, font_size='14sp', color=COLOR_TEXT))
        info.add_widget(Label(text=f"Ph: {SHOP_MOBILE}", font_name='Roboto', font_size='14sp', color=COLOR_TEXT))
        header.add_widget(info)
        
        btn_hist = Button(text="History", font_name='Roboto', background_color=COLOR_PRIMARY, size_hint_x=0.25, font_size='14sp', bold=True)
        btn_hist.bind(on_press=self.show_history)
        header.add_widget(btn_hist)
        root.add_widget(header)

        # INPUTS
        inputs = BoxLayout(size_hint_y=0.1, spacing=10)
        self.cust_name = TextInput(hint_text="Customer Name", font_name='Roboto', multiline=False)
        self.cust_mobile = TextInput(hint_text="Mobile No", font_name='Roboto', input_filter='int', multiline=False)
        inputs.add_widget(self.cust_name)
        inputs.add_widget(self.cust_mobile)
        root.add_widget(inputs)

        # HEADERS
        heads = BoxLayout(size_hint_y=None, height=40)
        heads.add_widget(Label(text="Sel", font_name='Roboto', size_hint_x=0.15, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Item Name", font_name='Roboto', size_hint_x=0.45, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Qty", font_name='Roboto', size_hint_x=0.2, color=COLOR_TEXT, bold=True))
        heads.add_widget(Label(text="Price", font_name='Roboto', size_hint_x=0.2, color=COLOR_TEXT, bold=True))
        root.add_widget(heads)

        # ITEMS
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for item in self.items:
            row = BoxLayout(size_hint_y=None, height=50)
            chk = CheckBox(size_hint_x=0.15, color=COLOR_TEXT)
            chk.bind(active=self.on_check)
            
            lbl = Label(text=_T(item), markup=True, size_hint_x=0.45, color=COLOR_TEXT, halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            qty = TextInput(text='1', font_name='Roboto', disabled=True, size_hint_x=0.2, opacity=0.3, input_filter='int', halign='center')
            rate = TextInput(hint_text='0', font_name='Roboto', disabled=True, size_hint_x=0.2, opacity=0.3, input_filter='int', halign='center')
            
            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(qty)
            row.add_widget(rate)
            grid.add_widget(row)
            self.cart[chk] = {'name': item, 'qty': qty, 'rate': rate}

        scroll.add_widget(grid)
        root.add_widget(scroll)

        # GENERATE BUTTON (Strictly using Roboto to prevent empty boxes)
        btn_gen = Button(text="GENERATE BILL", font_name='Roboto', size_hint_y=0.1, background_color=COLOR_PRIMARY, font_size='18sp', bold=True)
        btn_gen.bind(on_press=self.generate_bill)
        root.add_widget(btn_gen)

        self.home_screen.add_widget(root)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def setup_history_screen(self):
        root = BoxLayout(orientation='vertical', padding=10)
        top = BoxLayout(size_hint_y=0.1)
        btn = Button(text="< Back", font_name='Roboto', size_hint_x=0.3, on_press=lambda x: setattr(self.sm, 'current', 'home'))
        top.add_widget(btn)
        top.add_widget(Label(text="History", font_name='Roboto', color=COLOR_TEXT, bold=True, font_size='20sp'))
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

        # Load Custom Sky Blue Layout
        content = ReceiptLayout()
        
        if os.path.exists('logo.png'):
            content.add_widget(Image(source='logo.png', size_hint_y=None, height=80))

        # Receipt Text (Mixed English and Telugu using Markup)
        txt = f"[b][color=#D32F2F]{_T(SHOP_NAME)}[/color][/b]\n"
        txt += f"[color=000000]{_T(SHOP_ADDRESS)}\nPh: {SHOP_MOBILE}[/color]\n\n"
        txt += f"[color=000000][font=Roboto]Name:[/font] {self.cust_name.text}\n[font=Roboto]Date:[/font] {datetime.datetime.now().strftime('%d-%m-%Y')}[/color]\n"
        txt += "[color=000000]---------------------------------------[/color]\n"
        
        for name, q, amt in items:
            txt += f"[color=000000]{_T(name)} (x{q}) : Rs.{amt}[/color]\n"
            
        txt += "[color=000000]---------------------------------------[/color]\n"
        txt += f"[b][color=#D32F2F][font=Roboto]TOTAL: Rs.[/font] {int(total)}[/color][/b]\n"
        txt += "[color=000000][font=Roboto]Thank You![/font][/color]"

        lbl = Label(text=txt, markup=True, color=COLOR_TEXT)
        content.add_widget(lbl)

        btns = BoxLayout(size_hint_y=0.2, spacing=10)
        btn_cls = Button(text="Close", font_name='Roboto', background_color=(0.5,0.5,0.5,1), bold=True)
        btn_share = Button(text="SHARE RECEIPT", font_name='Roboto', background_color=(0,0.8,0,1), bold=True)
        
        self.popup = Popup(title="", separator_height=0, content=content, size_hint=(0.9, 0.85), background='white_pixel.png')
        self.popup.background_color = (1,1,1,1)
        
        btn_cls.bind(on_press=self.popup.dismiss)
        btn_share.bind(on_press=lambda x: self.capture_and_share(content))
        
        btns.add_widget(btn_cls)
        btns.add_widget(btn_share)
        content.add_widget(btns)
        
        self.popup.open()
        
        # Save History
        self.save_history(self.cust_name.text, total, txt)
        
        # Reset Menu
        self.cust_name.text = ""
        self.cust_mobile.text = ""
        for chk in self.cart: chk.active = False

    def capture_and_share(self, widget_content):
        filename = f"Bill_{datetime.datetime.now().strftime('%H%M%S')}.png"
        
        if platform.system() == 'Android':
            from android.storage import primary_external_storage_path
            save_dir = os.path.join(primary_external_storage_path(), 'Download')
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            path = os.path.join(save_dir, filename)
        else:
            path = os.path.join(self.user_data_dir, filename)

        widget_content.export_to_png(path)
        
        # Wait 1 second for the image to physically save before opening the share menu
        Clock.schedule_once(lambda dt: self.invoke_android_share(path), 1.0)

    def invoke_android_share(self, path):
        if platform.system() == 'Android':
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')
                FileProvider = autoclass('androidx.core.content.FileProvider')

                context = cast('android.content.Context', PythonActivity.mActivity)
                file_obj = File(path)

                authority = context.getPackageName() + ".fileprovider"
                uri = FileProvider.getUriForFile(context, authority, file_obj)

                intent = Intent(Intent.ACTION_SEND)
                intent.setType("image/png")
                intent.putExtra(Intent.EXTRA_STREAM, cast('android.os.Parcelable', uri))
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                chooser = Intent.createChooser(intent, "Share Bill")
                context.startActivity(chooser)
            except Exception as e:
                print(f"Native share failed: {e}")
                try:
                    from plyer import share
                    share.share_file(path)
                except: pass

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
                    btn = Button(text=f"{item['date']} - {item['name']} - Rs.{item['total']}", size_hint_y=None, height=60, font_name='Roboto')
                    self.hist_container.add_widget(btn)

if __name__ == '__main__':
    ReceiptApp().run()
