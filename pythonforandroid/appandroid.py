# catalogue_android_simple.py - APPLICATION ANDROID SIMPLE
import os
import json
import shutil
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger

# Détecter si on est sur Android
IS_ANDROID = platform == 'android'

# Configuration
Window.clearcolor = (0.97, 0.97, 0.97, 1)
SAVE_FILE = "catalogue_data.json"
PHOTOS_DIR = "photos_catalogue"

# Créer les dossiers
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

class Article:
    def __init__(self, nom, prix, photo_path=None, description=""):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.nom = nom
        self.prix = float(prix) if prix else 0.0
        self.photo_path = photo_path
        self.description = description
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M")

class CatalogueAndroidSimple(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "📱 Catalogue Tunisien"
        self.articles = []
        self.load_articles()
    
    def build(self):
        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Header rouge tunisien
        header = BoxLayout(size_hint=(1, 0.12))
        with header.canvas.before:
            Color(0.85, 0.1, 0.1, 1)  # Rouge
            Rectangle(pos=header.pos, size=header.size)
        
        title = Label(
            text="CATALOGUE TUNISIEN",
            font_size='28sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        self.main_layout.add_widget(header)
        
        # Boutons principaux
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.15), padding=[20, 10])
        
        btn_add = Button(
            text="➕ AJOUTER",
            background_color=(0.2, 0.7, 0.3, 1),
            font_size='18sp',
            bold=True
        )
        btn_add.bind(on_press=self.show_add_menu)
        
        btn_view = Button(
            text="📋 LISTE",
            background_color=(0.2, 0.5, 0.8, 1),
            font_size='18sp'
        )
        btn_view.bind(on_press=self.view_all)
        
        btn_layout.add_widget(btn_add)
        btn_layout.add_widget(btn_view)
        self.main_layout.add_widget(btn_layout)
        
        # Stats
        self.stats_label = Label(
            text="Chargement...",
            font_size='16sp',
            color=(0.3, 0.5, 0.7, 1),
            size_hint=(1, 0.08),
            padding=[20, 0]
        )
        self.main_layout.add_widget(self.stats_label)
        
        # Zone des articles
        scroll = ScrollView(size_hint=(1, 0.65))
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10, 10])
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        self.main_layout.add_widget(scroll)
        
        # Mettre à jour l'affichage
        Clock.schedule_once(self.update_display, 0.1)
        
        return self.main_layout
    
    def load_articles(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.articles = []
                    for item in data:
                        article = Article(
                            item['nom'],
                            item['prix'],
                            item.get('photo_path'),
                            item.get('description', '')
                        )
                        article.id = item['id']
                        article.date = item.get('date', article.date)
                        self.articles.append(article)
        except Exception as e:
            Logger.error(f"Erreur chargement: {e}")
            self.articles = []
    
    def save_articles(self):
        try:
            data = []
            for article in self.articles:
                data.append({
                    'id': article.id,
                    'nom': article.nom,
                    'prix': article.prix,
                    'photo_path': article.photo_path,
                    'description': article.description,
                    'date': article.date
                })
            
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Logger.error(f"Erreur sauvegarde: {e}")
    
    def update_display(self, dt=None):
        self.grid.clear_widgets()
        
        if not self.articles:
            empty = Label(
                text="📭 Aucun article\n\nCliquez sur ➕ AJOUTER",
                font_size='20sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                size_hint_y=None,
                height=200
            )
            empty.bind(size=empty.setter('text_size'))
            self.grid.add_widget(empty)
            self.grid.height = 220
        else:
            for article in self.articles:
                # Créer une carte d'article
                card = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=120,
                    padding=10,
                    spacing=10
                )
                
                # Fond de la carte
                with card.canvas.before:
                    Color(1, 1, 1, 1)
                    Rectangle(pos=card.pos, size=card.size)
                    Color(0.9, 0.9, 0.9, 1)
                    Rectangle(pos=(card.pos[0], card.pos[1]), size=(card.width, 2))
                
                # Image
                img_source = article.photo_path if article.photo_path and os.path.exists(article.photo_path) else ""
                
                img = Image(
                    source=img_source,
                    size_hint=(None, 1),
                    width=100,
                    allow_stretch=True,
                    keep_ratio=True
                )
                
                # Informations
                info = BoxLayout(orientation='vertical', spacing=2)
                
                nom = Label(
                    text=article.nom[:25] + "..." if len(article.nom) > 25 else article.nom,
                    font_size='16sp',
                    bold=True,
                    color=(0.2, 0.2, 0.2, 1),
                    halign='left',
                    size_hint_y=0.4
                )
                nom.bind(size=nom.setter('text_size'))
                
                prix = Label(
                    text=f"{article.prix:,.3f} TND",
                    font_size='20sp',
                    bold=True,
                    color=(0.85, 0.1, 0.1, 1),
                    size_hint_y=0.4
                )
                
                date = Label(
                    text=article.date.split()[0],
                    font_size='12sp',
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=0.2
                )
                
                info.add_widget(nom)
                info.add_widget(prix)
                info.add_widget(date)
                
                # Bouton modifier
                edit_btn = Button(
                    text="✏",
                    size_hint=(None, 1),
                    width=60,
                    background_color=(0.2, 0.6, 0.8, 1),
                    font_size='18sp'
                )
                edit_btn.bind(on_press=lambda instance, a=article: self.edit_article(a))
                
                card.add_widget(img)
                card.add_widget(info)
                card.add_widget(edit_btn)
                
                self.grid.add_widget(card)
            
            self.grid.height = len(self.articles) * 130
        
        # Mettre à jour les stats
        total = sum(a.prix for a in self.articles)
        self.stats_label.text = f"📊 {len(self.articles)} Articles | Total: {total:,.3f} TND"
    
    def show_add_menu(self, instance):
        """Menu pour ajouter un article"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=30)
        
        layout.add_widget(Label(
            text="CHOISIR UNE OPTION",
            font_size='24sp',
            bold=True,
            color=(0.2, 0.5, 0.8, 1)
        ))
        
        btn_with_photo = Button(
            text="📁 IMPORTER UNE PHOTO",
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, 0.3),
            font_size='18sp'
        )
        btn_with_photo.bind(on_press=self.import_photo)
        
        btn_without_photo = Button(
            text="➕ SANS PHOTO",
            background_color=(0.4, 0.7, 0.4, 1),
            size_hint=(1, 0.3),
            font_size='18sp'
        )
        btn_without_photo.bind(on_press=self.add_without_photo)
        
        btn_cancel = Button(
            text="ANNULER",
            background_color=(0.8, 0.3, 0.3, 1),
            size_hint=(1, 0.2)
        )
        
        layout.add_widget(btn_with_photo)
        layout.add_widget(btn_without_photo)
        layout.add_widget(btn_cancel)
        
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.8, 0.6)
        )
        
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()
    
    def import_photo(self, instance):
        """Importer une photo depuis la galerie"""
        layout = BoxLayout(orientation='vertical')
        
        # FileChooser pour Android/PC
        self.filechooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg'],
            size_hint=(1, 0.8)
        )
        
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        
        btn_select = Button(
            text="SÉLECTIONNER",
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_select.bind(on_press=self.on_photo_selected)
        
        btn_cancel = Button(
            text="ANNULER",
            background_color=(0.8, 0.3, 0.3, 1)
        )
        
        btn_layout.add_widget(btn_select)
        btn_layout.add_widget(btn_cancel)
        
        layout.add_widget(self.filechooser)
        layout.add_widget(btn_layout)
        
        self.photo_popup = Popup(
            title="Choisir une photo",
            content=layout,
            size_hint=(0.9, 0.9)
        )
        
        btn_cancel.bind(on_press=self.photo_popup.dismiss)
        self.photo_popup.open()
    
    def on_photo_selected(self, instance):
        """Quand une photo est sélectionnée"""
        if self.filechooser.selection:
            photo_path = self.filechooser.selection[0]
            self.photo_popup.dismiss()
            self.show_article_form(photo_path)
        else:
            self.show_message("Veuillez sélectionner une photo")
    
    def add_without_photo(self, instance):
        """Ajouter sans photo"""
        self.show_article_form(None)
    
    def show_article_form(self, photo_path):
        """Afficher le formulaire d'article"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=25)
        
        layout.add_widget(Label(
            text="NOUVEL ARTICLE",
            font_size='22sp',
            bold=True,
            color=(0.2, 0.5, 0.8, 1)
        ))
        
        # Aperçu photo si disponible
        if photo_path and os.path.exists(photo_path):
            img = Image(
                source=photo_path,
                size_hint=(1, 0.3),
                allow_stretch=True,
                keep_ratio=True
            )
            layout.add_widget(img)
        
        self.nom_input = TextInput(
            hint_text="Nom de l'article",
            size_hint=(1, 0.2),
            font_size='18sp'
        )
        
        self.prix_input = TextInput(
            hint_text="Prix en TND",
            size_hint=(1, 0.2),
            font_size='18sp',
            input_filter='float'
        )
        
        self.desc_input = TextInput(
            hint_text="Description (optionnel)",
            size_hint=(1, 0.3),
            font_size='16sp',
            multiline=True
        )
        
        layout.add_widget(self.nom_input)
        layout.add_widget(self.prix_input)
        layout.add_widget(self.desc_input)
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.2))
        
        btn_save = Button(
            text="💾 SAUVEGARDER",
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_save.bind(on_press=lambda x: self.save_article_form(photo_path))
        
        btn_cancel = Button(
            text="ANNULER",
            background_color=(0.8, 0.3, 0.3, 1)
        )
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        layout.add_widget(btn_layout)
        
        self.form_popup = Popup(
            title='',
            content=layout,
            size_hint=(0.9, 0.8)
        )
        
        btn_cancel.bind(on_press=self.form_popup.dismiss)
        self.form_popup.open()
        
        Clock.schedule_once(lambda dt: setattr(self.nom_input, 'focus', True), 0.1)
    
    def save_article_form(self, photo_path):
        """Sauvegarder l'article"""
        nom = self.nom_input.text.strip()
        prix = self.prix_input.text.strip()
        desc = self.desc_input.text.strip()
        
        if nom and prix:
            try:
                # Copier la photo dans le dossier de l'app si elle existe
                final_photo_path = None
                if photo_path and os.path.exists(photo_path):
                    # Créer un nom unique
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ext = os.path.splitext(photo_path)[1]
                    dest_filename = f"article_{timestamp}{ext}"
                    dest_path = os.path.join(PHOTOS_DIR, dest_filename)
                    
                    # Copier le fichier
                    shutil.copy2(photo_path, dest_path)
                    final_photo_path = dest_path
                
                # Créer l'article
                article = Article(nom, prix, final_photo_path, desc)
                self.articles.append(article)
                self.save_articles()
                self.update_display()
                
                self.form_popup.dismiss()
                self.show_message(f"✅ Article '{nom}' ajouté !\n{float(prix):,.3f} TND")
                
            except ValueError:
                self.show_message("❌ Prix invalide !")
            except Exception as e:
                Logger.error(f"Erreur sauvegarde: {e}")
                self.show_message("❌ Erreur de sauvegarde")
        else:
            self.show_message("❌ Nom et prix requis !")
    
    def edit_article(self, article):
        """Modifier un article"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=25)
        
        layout.add_widget(Label(
            text="✏ MODIFIER L'ARTICLE",
            font_size='22sp',
            bold=True,
            color=(0.2, 0.5, 0.8, 1)
        ))
        
        # Afficher photo si existe
        if article.photo_path and os.path.exists(article.photo_path):
            img = Image(
                source=article.photo_path,
                size_hint=(1, 0.3),
                allow_stretch=True,
                keep_ratio=True
            )
            layout.add_widget(img)
        
        nom_input = TextInput(
            text=article.nom,
            size_hint=(1, 0.2),
            font_size='18sp'
        )
        
        prix_input = TextInput(
            text=str(article.prix),
            size_hint=(1, 0.2),
            font_size='18sp',
            input_filter='float'
        )
        
        desc_input = TextInput(
            text=article.description,
            size_hint=(1, 0.3),
            font_size='16sp',
            multiline=True
        )
        
        layout.add_widget(nom_input)
        layout.add_widget(prix_input)
        layout.add_widget(desc_input)
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.2))
        
        btn_update = Button(
            text="💾 METTRE À JOUR",
            background_color=(0.2, 0.6, 0.8, 1)
        )
        
        btn_delete = Button(
            text="🗑 SUPPRIMER",
            background_color=(0.9, 0.3, 0.3, 1)
        )
        
        btn_close = Button(
            text="FERMER",
            background_color=(0.6, 0.6, 0.6, 1)
        )
        
        btn_layout.add_widget(btn_update)
        btn_layout.add_widget(btn_delete)
        btn_layout.add_widget(btn_close)
        layout.add_widget(btn_layout)
        
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.9, 0.8)
        )
        
        def update_action(b):
            article.nom = nom_input.text
            try:
                article.prix = float(prix_input.text)
                article.description = desc_input.text
                article.date = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.save_articles()
                self.update_display()
                popup.dismiss()
                self.show_message("✅ Article modifié !")
            except ValueError:
                self.show_message("❌ Prix invalide !")
        
        def delete_action(b):
            popup.dismiss()
            self.confirm_delete(article)
        
        btn_update.bind(on_press=update_action)
        btn_delete.bind(on_press=delete_action)
        btn_close.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def confirm_delete(self, article):
        """Confirmer suppression"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=30)
        
        layout.add_widget(Label(
            text="SUPPRIMER L'ARTICLE ?",
            font_size='22sp',
            bold=True,
            color=(0.9, 0.2, 0.2, 1)
        ))
        
        layout.add_widget(Label(
            text=f"'{article.nom}'\n{article.prix:,.3f} TND",
            font_size='18sp',
            halign='center'
        ))
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.3))
        
        btn_yes = Button(
            text="OUI, SUPPRIMER",
            background_color=(0.9, 0.3, 0.3, 1)
        )
        
        btn_no = Button(
            text="ANNULER",
            background_color=(0.6, 0.6, 0.6, 1)
        )
        
        btn_yes.bind(on_press=lambda x: (self.delete_popup.dismiss(), self.delete_article(article)))
        btn_no.bind(on_press=self.delete_popup.dismiss)
        
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        layout.add_widget(btn_layout)
        
        self.delete_popup = Popup(
            title='Confirmation',
            content=layout,
            size_hint=(0.7, 0.4)
        )
        self.delete_popup.open()
    
    def delete_article(self, article):
        """Supprimer l'article"""
        # Supprimer la photo si elle existe
        if article.photo_path and os.path.exists(article.photo_path):
            try:
                os.remove(article.photo_path)
            except:
                pass
        
        self.articles = [a for a in self.articles if a.id != article.id]
        self.save_articles()
        self.update_display()
        self.show_message("✅ Article supprimé !")
    
    def view_all(self, instance):
        """Voir tous les articles"""
        if not self.articles:
            self.show_message("📭 Aucun article à afficher")
            return
        
        layout = BoxLayout(orientation='vertical', padding=10)
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for i, article in enumerate(self.articles, 1):
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            
            item.add_widget(Label(
                text=f"{i}. {article.nom}",
                font_size='16sp',
                halign='left'
            ))
            
            item.add_widget(Label(
                text=f"{article.prix:,.3f} TND",
                font_size='16sp',
                color=(0.9, 0.2, 0.2, 1)
            ))
            
            list_layout.add_widget(item)
        
        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        
        btn_close = Button(
            text="FERMER",
            size_hint=(1, 0.1),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        layout.add_widget(btn_close)
        
        popup = Popup(
            title=f'📋 Liste ({len(self.articles)} articles)',
            content=layout,
            size_hint=(0.9, 0.8)
        )
        
        btn_close.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_message(self, message):
        """Afficher un message"""
        Popup(
            title='',
            content=Label(text=message, font_size='18sp'),
            size_hint=(0.7, 0.4)
        ).open()

# Lancement de l'application
if __name__ == '__main__':
    print("="*60)
    print("📱 CATALOGUE TUNISIEN - VERSION ANDROID")
    print("Importez des photos depuis votre galerie !")
    print("="*60)
    
    if IS_ANDROID:
        print("✅ Mode Android détecté")
        print("📁 Import de photos depuis la galerie activé")
    else:
        print("💻 Mode PC détecté")
        print("📁 Import de photos depuis le dossier 'photos_catalogue'")
    
    CatalogueAndroidSimple().run()
