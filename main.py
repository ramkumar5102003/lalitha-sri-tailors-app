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

# --- కాన్ఫిగరేషన్ (Configuration) ---
SHOP_NAME = "లలిత శ్రీ టైలర్స్"
SHOP_ADDRESS = "షాప్ నెం:30, కరాచీ సెంటర్, మండపేట"
SHOP_MOBILE = "+91 95023 84443"
HISTORY_FILE = "receipt_history.json"

# --- ఫాంట్ సెట్టింగ్ (Font Configuration) ---
# తెలుగు అక్షరాలు సరిగ్గా కనిపించడానికి NotoSansTelugu-Regular.ttf తప్పనిసరి.
if os.path.exists('NotoSansTelugu-Regular.ttf'):
    APP_FONT = 'NotoSansTelugu-Regular.ttf'
else:
    APP_FONT = None  # ఫాంట్ లేకపోతే బాక్సులుగా కనిపిస్తుంది

class ReceiptApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # వైట్ బ్యాక్‌గ్రౌండ్
        Window.size = (1080, 1920)       # మొబైల్ స్క్రీన్ సైజు
        self.cart = {}
        
        # ఆండ్రాయిడ్ పర్మిషన్లు (Android Permissions)
        if platform.system() == 'Android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
            except Exception as e:
                print(f"Permission Error: {e}")

        # తెలుగు జాబితా (Items List)
        self.items = [
            "పెద్ద షర్ట్",
            "పెద్ద ఫ్యాంటు",
            "పెద్ద నిక్కర్",
            "కుర్తా",
            "స్కూల్ యూనిఫామ్",
            "చిన్న షర్టు",
            "చిన్న ఫ్యాంటు",
            "చిన్న నిక్కర్",
            "ఇతర ఆల్టరేషన్స్"
        ]

        self.sm = ScreenManager()
        self.home_screen = Screen(name='home')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 1. హెడర్ (Header)
        header = BoxLayout(size_hint_y=0.2, spacing=10)
        
        # లోగో (Logo)
        if os.path.exists('logo.png'):
            img = Image(source='logo.png', size_hint_x=0.3, allow_stretch=True)
            header.add_widget(img)
        
        shop_info = BoxLayout(orientation='vertical')
        
        # షాపు పేరు
        shop_name_lbl = Label(
            text=SHOP_NAME,
            font_name=APP_FONT,
            font_size='24sp',
            bold=True,
            color=(0.8, 0, 0, 1) # ఎరుపు రంగు
        )
        shop_info.add_widget(shop_name_lbl)
        
        # అడ్రస్
        shop_addr_lbl = Label(
            text=SHOP_ADDRESS,
            font_name=APP_FONT,
            font_size='14sp',
            color=(0, 0, 0, 1)
        )
        shop_info.add_widget(shop_addr_lbl)
        
        # ఫోన్ నెంబర్
        shop_phone_lbl = Label(
            text=f"ఫోన్: {SHOP_MOBILE}",
            font_name=APP_FONT,
            font_size='14sp',
            color=(0, 0, 0, 1)
        )
        shop_info.add_widget(shop_phone_lbl)
        header.add_widget(shop_info)
        
        # చరిత్ర బటన్ (History Button)
        btn_hist = Button(
            text="పాత బిల్లులు\n(History)",
            font_name=APP_FONT,
            size_hint_x=0.28,
            background_color=(0, 0.4, 0.8, 1),
            font_size='13sp'
        )
        btn_hist.bind(on_press=self.show_history)
        header.add_widget(btn_hist)
        
        layout.add_widget(header)

        # 2. కస్టమర్ వివరాలు (Customer Inputs)
        cust_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        self.cust_name = TextInput(
            hint_text="కస్టమర్ పేరు (Name)",
            font_name=APP_FONT,
            multiline=False,
            foreground_color=(0, 0, 0, 1)
        )
        self.cust_name.background_color = (0.95, 0.95, 0.95, 1)
        
        self.cust_mobile = TextInput(
            hint_text="మొబైల్ నం (Mobile)",
            font_name=APP_FONT,
            multiline=False,
            input_filter='int',
            foreground_color=(0, 0, 0, 1)
        )
        self.cust_mobile.background_color = (0.95, 0.95, 0.95, 1)

        cust_layout.add_widget(self.cust_name)
        cust_layout.add_widget(self.cust_mobile)
        layout.add_widget(cust_layout)

        # 3. పట్టిక హెడర్స్ (Table Headers)
        col_header = BoxLayout(size_hint_y=None, height=40)
        col_header.add_widget(Label(text="టిక్", font_name=APP_FONT, size_hint_x=0.15, color=(0, 0, 0, 1), bold=True))
        col_header.add_widget(Label(text="వస్తువు పేరు", font_name=APP_FONT, size_hint_x=0.45, color=(0, 0, 0, 1), bold=True))
        col_header.add_widget(Label(text="సంఖ్య", font_name=APP_FONT, size_hint_x=0.2, color=(0, 0, 0, 1), bold=True))
        col_header.add_widget(Label(text="ధర", font_name=APP_FONT, size_hint_x=0.2, color=(0, 0, 0, 1), bold=True))
        layout.add_widget(col_header)

        # 4. ఐటమ్స్ లిస్ట్ (Items List)
        scroll = ScrollView(size_hint_y=0.55)
        list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for item in self.items:
            row = BoxLayout(size_hint_y=None, height=55)
            
            chk = CheckBox(size_hint_x=0.15, color=(0, 0, 0, 1))
            chk.bind(active=self.on_checkbox_active)
            
            lbl = Label(
                text=item,
                font_name=APP_FONT,
                size_hint_x=0.45,
                halign='left',
                valign='middle',
                color=(0.2, 0.2, 0.2, 1),
                font_size='15sp'
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            qty = TextInput(
                text='1',
                input_filter='float',
                disabled=True,
                opacity=0.3,
                size_hint_x=0.2,
                font_size='14sp',
                halign='center'
            )
            rate = TextInput(
                hint_text='0',
                input_filter='float',
                disabled=True,
                opacity=0.3,
                size_hint_x=0.2,
                font_size='14sp',
                halign='center'
            )
            
            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(qty)
            row.add_widget(rate)
            list_layout.add_widget(row)
            
            self.cart[chk] = {'name': item, 'qty': qty, 'rate': rate}

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)

        # 5. జనరేట్ బటన్ (Generate Button)
        btn_gen = Button(
            text="బిల్లు తయారు చేయండి",
            font_name=APP_FONT,
            size_hint_y=0.12,
            background_color=(0, 0.6, 0, 1), # గ్రీన్ కలర్
            font_size='20sp',
            bold=True
        )
        btn_gen.bind(on_press=self.generate_receipt)
        layout.add_widget(btn_gen)

        self.home_screen.add_widget(layout)
        self.sm.add_widget(self.home_screen)

        # --- స్క్రీన్ 2: చరిత్ర (History Screen) ---
        self.hist_screen = Screen(name='history')
        hist_layout = BoxLayout(orientation='vertical')
        
        h_header = BoxLayout(size_hint_y=0.1, padding=5, spacing=10)
        btn_back = Button(text="< వెనుకకు", font_name=APP_FONT, size_hint_x=0.3, font_size='16sp', background_color=(0.5,0.5,0.5,1))
        btn_back.bind(on_press=self.go_home)
        h_header.add_widget(btn_back)
        
        hist_title = Label(text="పాత బిల్లుల చరిత్ర", font_name=APP_FONT, bold=True, color=(0, 0, 0, 1), font_size='20sp')
        h_header.add_widget(hist_title)
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

        # --- వాట్సాప్/షేరింగ్ కోసం టెక్స్ట్ (Plain Text) ---
        share_text = f"{SHOP_NAME}\n{SHOP_ADDRESS}\nఫోన్: {SHOP_MOBILE}\n"
        share_text += f"{'='*40}\n"
        share_text += f"తేదీ: {date_str}\nపేరు: {c_name}\nమొబైల్: {c_mob}\n"
        share_text += f"{'-'*40}\n"
        
        # --- పాప్అప్ కోసం డిజైన్ (Styled Markup) ---
        popup_text = f"[b][color=ff0000]{SHOP_NAME}[/color][/b]\n"
        popup_text += f"[size=14]{SHOP_ADDRESS}[/size]\n"
        popup_text += f"[size=14]ఫోన్: {SHOP_MOBILE}[/size]\n\n"
        popup_text += f"[b]తేదీ:[/b] {date_str}\n"
        popup_text += f"[b]పేరు:[/b] {c_name}\n"
        popup_text += f"[b]మొబైల్:[/b] {c_mob}\n"
        popup_text += f"{'='*35}\n"
        popup_text += f"[b]ఐటమ్           సంఖ్య   ధర[/b]\n"
        popup_text += f"{'-'*35}\n"

        total_bill = 0
        items_count = 0
        
        for chk, info in self.cart.items():
            if chk.active:
                try:
                    q = float(info['qty'].text) if info['qty'].text else 1.0
                    r = float(info['rate'].text) if info['rate'].text else 0.0
                    t = q * r
                    total_bill += t
                    items_count += 1
                    
                    share_text += f"{info['name']} x {int(q)} = రూ.{int(t)}\n"
                    popup_text += f"{info['name']:<18} {int(q):<3} {int(t):<3}\n"
                except ValueError:
                    pass

        if items_count == 0:
            return  # ఏమీ సెలెక్ట్ చేయకపోతే బిల్లు రాదు

        share_text += f"{'='*40}\nమొత్తం: రూ. {int(total_bill)}\n{'='*40}\n"
        share_text += f"ధన్యవాదాలు! మళ్ళీ రండి.\n"
        
        popup_text += f"{'-'*35}\n"
        popup_text += f"[b][size=22]మొత్తం: రూ. {int(total_bill)}[/size][/b]\n"
        popup_text += f"{'-'*35}\n"
        popup_text += f"[i]ధన్యవాదాలు! మళ్ళీ రండి.[/i]"

        self.save_to_history(c_name, date_str, total_bill, popup_text)

        # --- బిల్లు పాప్అప్ (Bill Popup) ---
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
            font_size='15sp'
        )
        receipt_lbl.bind(texture_size=receipt_lbl.setter('size'))
        receipt_scroll.add_widget(receipt_lbl)
        content.add_widget(receipt_scroll)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        btn_close = Button(text="మూసివేయు", font_name=APP_FONT, background_color=(0.8, 0, 0, 1), font_size='16sp')
        btn_share = Button(text="షేర్ చేయండి", font_name=APP_FONT, background_color=(0, 0.8, 0, 1), font_size='16sp')
        
        popup = Popup(title="బిల్లు ప్రివ్యూ", title_font=APP_FONT, content=content, size_hint=(0.95, 0.95))
        btn_close.bind(on_press=popup.dismiss)
        btn_share.bind(on_press=lambda x: self.share_file(share_text, c_name))
        
        btn_layout.add_widget(btn_close)
        btn_layout.add_widget(btn_share)
        content.add_widget(btn_layout)
        popup.open()
        
        # క్లియర్ చేయడం (Reset Inputs)
        self.cust_name.text = ""
        self.cust_mobile.text = ""
        for chk in self.cart:
            chk.active = False

    def save_to_history(self, name, date, total, full_text):
        entry = {'name': name, 'date': date, 'total': total, 'text': full_text}
        history_data = []
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except Exception as e:
                print(f"History Error: {e}")
        
        history_data.insert(0, entry)
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save Error: {e}")

    def show_history(self, instance):
        self.hist_grid.clear_widgets()
        self.sm.current = 'history'
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data:
                        # హిస్టరీ బటన్ టెక్స్ట్
                        btn_text = f"{entry['date']} | {entry['name']} | రూ.{int(entry['total'])}"
                        btn = Button(
                            text=btn_text,
                            font_name=APP_FONT,
                            size_hint_y=None,
                            height=65,
                            font_size='14sp'
                        )
                        btn.bind(on_press=lambda x, t=entry['text']: self.show_receipt_popup(t))
                        self.hist_grid.add_widget(btn)
            except Exception as e:
                print(f"Load Error: {e}")

    def show_receipt_popup(self, text):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        lbl = Label(
            text=text,
            font_name=APP_FONT,
            markup=True,
            color=(0, 0, 0, 1),
            font_size='14sp'
        )
        content.add_widget(lbl)
        
        btn = Button(text="మూసివేయు", font_name=APP_FONT, size_hint_y=0.15, font_size='16sp', background_color=(0.8,0,0,1))
        popup = Popup(title="పాత బిల్లు", title_font=APP_FONT, content=content, size_hint=(0.95, 0.95))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def share_file(self, text, cust_name):
        try:
            from plyer import share
            # ఫైల్ పేరు ఇంగ్లీష్ లోనే ఉంచడం మంచిది (Android Compatibility కోసం)
            filename = f"Bill_{cust_name}_{datetime.datetime.now().strftime('%H%M%S')}.txt"
            
            app_cache = self.user_data_dir
            path = os.path.join(app_cache, filename)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)

            share.share_file(path)
            
        except Exception as e:
            content = BoxLayout(orientation='vertical', padding=10)
            content.add_widget(Label(text=f"Share Error:\n{str(e)}", color=(0,0,0,1)))
            btn = Button(text="OK", size_hint_y=0.3)
            err_pop = Popup(title="Error", content=content, size_hint=(0.9, 0.4))
            btn.bind(on_press=err_pop.dismiss)
            content.add_widget(btn)
            err_pop.open()

if __name__ == '__main__':
    ReceiptApp().run()
