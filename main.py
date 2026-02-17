from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
import datetime
import os
import json
import platform

# --- CONFIGURATION ---
SHOP_NAME = "లలిత శ్రీ టైలర్స్"
SHOP_ADDRESS = "షాప్ నెం:30, కరాచీ సెంటర్, మండపేట"
SHOP_MOBILE = "+91 95023 84443"
HISTORY_FILE = "receipt_history.json"

# --- FONT CONFIGURATION (CRITICAL FIX) ---
# Use Noto Sans Telugu which supports ALL Telugu characters
# Download: https://github.com/google/fonts/blob/main/ofl/notosanstelugu/NotoSansTelugu-Regular.ttf
if os.path.exists('NotoSansTelugu-Regular.ttf'):
    APP_FONT = 'NotoSansTelugu-Regular.ttf'
else:
    # If font missing, still works but Telugu shows as boxes
    # This prevents app crash but font support requires the TTF file
    APP_FONT = None

class ReceiptApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # White Background
        Window.size = (1080, 1920)  # Better mobile size
        self.cart = {}
        
        # REQUEST ANDROID PERMISSIONS (Android 6+)
        if platform.system() == 'Android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
            except Exception as e:
                print(f"Permission request failed: {e}")

        # TELUGU ITEMS
        self.items = [
            "పెద్ద షర్ట్",
            "పెద్ద ఫ్యాంటు",
            "పెద్ద నిక్కర్",
            "కుర్తా",
            "స్కూల్ యూనిఫామ్",
            "చిన్న షర్టు",
            "చిన్న ఫ్యాంటు",
            "చిన్న నిక్కర్",
            "ఇతర ఆల్ట్రేషన్స్"
        ]

        self.sm = ScreenManager()
        self.home_screen = Screen(name='home')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 1. HEADER (Logo + Title)
        header = BoxLayout(size_hint_y=0.2, spacing=10)
        
        # Safe Logo Loading
        if os.path.exists('logo.png'):
            img = Image(source='logo.png', size_hint_x=0.3, allow_stretch=True)
            header.add_widget(img)
        
        shop_info = BoxLayout(orientation='vertical')
        # SHOP NAME (Stylish Red)
        shop_name_lbl = Label(
            text=SHOP_NAME,
            font_name=APP_FONT,
            font_size='22sp',
            bold=True,
            color=(0.8, 0, 0, 1)
        )
        shop_info.add_widget(shop_name_lbl)
        
        shop_addr_lbl = Label(
            text=SHOP_ADDRESS,
            font_name=APP_FONT,
            font_size='14sp',
            color=(0, 0, 0, 1)
        )
        shop_info.add_widget(shop_addr_lbl)
        
        shop_phone_lbl = Label(
            text=f"Ph: {SHOP_MOBILE}",
            font_name=APP_FONT,
            font_size='14sp',
            color=(0, 0, 0, 1)
        )
        shop_info.add_widget(shop_phone_lbl)
        header.add_widget(shop_info)
        
        # History Button
        btn_hist = Button(
            text="చరిత్ర\nHistory",
            font_name=APP_FONT,
            size_hint_x=0.25,
            background_color=(0, 0.4, 0.8, 1)
        )
        btn_hist.bind(on_press=self.show_history)
        header.add_widget(btn_hist)
        
        layout.add_widget(header)

        # 2. CUSTOMER INPUTS
        cust_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        self.cust_name = TextInput(
            hint_text="కస్టమర్ పేరు (Name)",
            font_name=APP_FONT,
            multiline=False,
            foreground_color=(0, 0, 0, 1)
        )
        self.cust_name.background_color = (0.95, 0.95, 0.95, 1)
        
        self.cust_mobile = TextInput(
            hint_text="మొబైల్ (Mobile)",
            font_name=APP_FONT,
            multiline=False,
            input_filter='int',
            foreground_color=(0, 0, 0, 1)
        )
        self.cust_mobile.background_color = (0.95, 0.95, 0.95, 1)

        cust_layout.add_widget(self.cust_name)
        cust_layout.add_widget(self.cust_mobile)
        layout.add_widget(cust_layout)

        # 3. LIST HEADERS
        col_header = BoxLayout(size_hint_y=None, height=35)
        col_header.add_widget(Label(text="Select", size_hint_x=0.15, color=(0, 0, 0, 1), bold=True, font_size='12sp'))
        col_header.add_widget(Label(text="వస్తువు (Item)", font_name=APP_FONT, size_hint_x=0.45, color=(0, 0, 0, 1), bold=True, font_size='12sp'))
        col_header.add_widget(Label(text="Qty", size_hint_x=0.2, color=(0, 0, 0, 1), bold=True, font_size='12sp'))
        col_header.add_widget(Label(text="Rate", size_hint_x=0.2, color=(0, 0, 0, 1), bold=True, font_size='12sp'))
        layout.add_widget(col_header)

        # 4. ITEMS LIST (Scrollable)
        scroll = ScrollView(size_hint_y=0.55)
        list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for item in self.items:
            row = BoxLayout(size_hint_y=None, height=50)
            
            chk = CheckBox(size_hint_x=0.15, color=(0, 0, 0, 1))
            chk.bind(active=self.on_checkbox_active)
            
            lbl = Label(
                text=item,
                font_name=APP_FONT,
                size_hint_x=0.45,
                halign='left',
                valign='middle',
                color=(0.2, 0.2, 0.2, 1),
                font_size='14sp'
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            qty = TextInput(
                text='1',
                input_filter='float',
                disabled=True,
                opacity=0.3,
                size_hint_x=0.2,
                font_size='14sp'
            )
            rate = TextInput(
                hint_text='0',
                input_filter='float',
                disabled=True,
                opacity=0.3,
                size_hint_x=0.2,
                font_size='14sp'
            )
            
            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(qty)
            row.add_widget(rate)
            list_layout.add_widget(row)
            
            self.cart[chk] = {'name': item, 'qty': qty, 'rate': rate}

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)

        # 5. GENERATE BUTTON
        btn_gen = Button(
            text="బిల్లు తయారు చేయండి (Generate Bill)",
            font_name=APP_FONT,
            size_hint_y=0.12,
            background_color=(0, 0.8, 0, 1),
            font_size='18sp',
            bold=True
        )
        btn_gen.bind(on_press=self.generate_receipt)
        layout.add_widget(btn_gen)

        self.home_screen.add_widget(layout)
        self.sm.add_widget(self.home_screen)

        # --- SCREEN 2: HISTORY ---
        self.hist_screen = Screen(name='history')
        hist_layout = BoxLayout(orientation='vertical')
        
        h_header = BoxLayout(size_hint_y=0.1, padding=5, spacing=10)
        btn_back = Button(text="< Back", font_name=APP_FONT, size_hint_x=0.25, font_size='16sp')
        btn_back.bind(on_press=self.go_home)
        h_header.add_widget(btn_back)
        h_header.add_widget(Label(text="History", font_name=APP_FONT, bold=True, color=(0, 0, 0, 1), font_size='18sp'))
        hist_layout.add_widget(h_header)
        
        self.hist_scroll = ScrollView()
        self.hist_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.hist_grid.bind(minimum_height=self.hist_grid.setter('height'))
        self.hist_scroll.add_widget(self.hist_grid)
        hist_layout.add_widget(self.hist_scroll)
        
        self.hist_screen.add_widget(hist_layout)
        self.sm.add_widget(self.hist_screen)

        return self.sm

    def go_home(self, instance):
        self.sm.current = 'home'

    def on_checkbox_active(self, checkbox, value):
        widgets = self.cart[checkbox]
        widgets['qty'].disabled = not value
        widgets['rate'].disabled = not value
        widgets['qty'].opacity = 1.0 if value else 0.3
        widgets['rate'].opacity = 1.0 if value else 0.3

    def generate_receipt(self, instance):
        date_str = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        c_name = self.cust_name.text if self.cust_name.text else "-"
        c_mob = self.cust_mobile.text if self.cust_mobile.text else "-"

        # --- PLAIN TEXT (For File Sharing) ---
        share_text = f"{SHOP_NAME}\n{SHOP_ADDRESS}\nPh: {SHOP_MOBILE}\n"
        share_text += f"{'='*40}\n"
        share_text += f"Date: {date_str}\nName: {c_name}\nPh: {c_mob}\n"
        share_text += f"{'-'*40}\n"
        
        # --- STYLED MARKUP (For Popup Display) ---
        popup_text = f"[b][color=ff0000]{SHOP_NAME}[/color][/b]\n"
        popup_text += f"[size=14]{SHOP_ADDRESS}[/size]\n"
        popup_text += f"[size=14]Ph: {SHOP_MOBILE}[/size]\n\n"
        popup_text += f"[b]Date:[/b] {date_str}\n"
        popup_text += f"[b]Name:[/b] {c_name}\n"
        popup_text += f"[b]Mobile:[/b] {c_mob}\n"
        popup_text += f"{'='*40}\n"
        popup_text += f"[b]Item             Qty  Price[/b]\n"
        popup_text += f"{'-'*40}\n"

        total_bill = 0
        for chk, info in self.cart.items():
            if chk.active:
                try:
                    q = float(info['qty'].text) if info['qty'].text else 1.0
                    r = float(info['rate'].text) if info['rate'].text else 0.0
                    t = q * r
                    total_bill += t
                    
                    share_text += f"{info['name']} x {int(q)} = Rs.{int(t)}\n"
                    popup_text += f"{info['name']:<20} {int(q):<3} {int(t):<3}\n"
                except ValueError:
                    pass

        share_text += f"{'='*40}\nTOTAL: Rs. {int(total_bill)}\n{'='*40}\n"
        share_text += f"Thank You! Come Again\n"
        
        popup_text += f"{'-'*40}\n"
        popup_text += f"[b][size=20]TOTAL: Rs. {int(total_bill)}[/size][/b]\n"
        popup_text += f"{'-'*40}\n"
        popup_text += f"[i]Thank You! Come Again[/i]"

        self.save_to_history(c_name, date_str, total_bill, popup_text)

        # --- DISPLAY POPUP ---
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Logo in Popup
        if os.path.exists('logo.png'):
            logo = Image(source='logo.png', size_hint_y=None, height=80, allow_stretch=True)
            content.add_widget(logo)
        
        # Scrollable Receipt Text
        receipt_scroll = ScrollView()
        receipt_lbl = Label(
            text=popup_text,
            font_name=APP_FONT,
            markup=True,
            size_hint_y=None,
            color=(0, 0, 0, 1),
            font_size='14sp'
        )
        receipt_lbl.bind(texture_size=receipt_lbl.setter('size'))
        receipt_scroll.add_widget(receipt_lbl)
        content.add_widget(receipt_scroll)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        btn_close = Button(text="Close", font_name=APP_FONT, background_color=(0.8, 0, 0, 1), font_size='16sp')
        btn_share = Button(text="SHARE", font_name=APP_FONT, background_color=(0, 0.8, 0, 1), font_size='16sp')
        
        popup = Popup(title="Bill Preview", content=content, size_hint=(0.95, 0.95))
        btn_close.bind(on_press=popup.dismiss)
        btn_share.bind(on_press=lambda x: self.share_file(share_text, c_name))
        
        btn_layout.add_widget(btn_close)
        btn_layout.add_widget(btn_share)
        content.add_widget(btn_layout)
        popup.open()
        
        # Clear inputs after generating bill
        self.cust_name.text = ""
        self.cust_mobile.text = ""

    def save_to_history(self, name, date, total, full_text):
        """Save receipt to JSON history file"""
        entry = {'name': name, 'date': date, 'total': total, 'text': full_text}
        history_data = []
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except Exception as e:
                print(f"Error reading history: {e}")
        
        history_data.insert(0, entry)
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def show_history(self, instance):
        """Display history screen"""
        self.hist_grid.clear_widgets()
        self.sm.current = 'history'
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data:
                        btn_text = f"{entry['date']} | {entry['name']} | Rs.{int(entry['total'])}"
                        btn = Button(
                            text=btn_text,
                            font_name=APP_FONT,
                            size_hint_y=None,
                            height=60,
                            font_size='14sp'
                        )
                        btn.bind(on_press=lambda x, t=entry['text']: self.show_receipt_popup(t))
                        self.hist_grid.add_widget(btn)
            except Exception as e:
                print(f"Error loading history: {e}")

    def show_receipt_popup(self, text):
        """Show receipt from history"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        lbl = Label(
            text=text,
            font_name=APP_FONT,
            markup=True,
            color=(0, 0, 0, 1),
            font_size='14sp'
        )
        content.add_widget(lbl)
        
        btn = Button(text="Close", font_name=APP_FONT, size_hint_y=0.15, font_size='16sp')
        popup = Popup(title="Receipt", content=content, size_hint=(0.95, 0.95))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def share_file(self, text, cust_name):
        """Share receipt via Android share menu"""
        try:
            from plyer import share
            
            # Create filename with customer name and timestamp
            filename = f"Bill_{cust_name}_{datetime.datetime.now().strftime('%H%M%S')}.txt"
            
            # Save to app's cache directory (works on Android 10+)
            app_cache = self.user_data_dir
            path = os.path.join(app_cache, filename)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)

            # Android will handle permissions automatically
            share.share_file(path)
            
        except Exception as e:
            content = BoxLayout(orientation='vertical', padding=10)
            content.add_widget(Label(text=f"Share Error:\n{str(e)}", font_name=APP_FONT, color=(0,0,0,1)))
            btn = Button(text="OK", size_hint_y=0.3)
            err_pop = Popup(title="Error", content=content, size_hint=(0.9, 0.4))
            btn.bind(on_press=err_pop.dismiss)
            content.add_widget(btn)
            err_pop.open()


if __name__ == '__main__':
    ReceiptApp().run()
