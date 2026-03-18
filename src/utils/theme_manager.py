"""
Менеджер тем оформления для Ten Dem
"""


class ThemeManager:
    """Управление темами приложения."""
    
    # Тёмная тема (по умолчанию)
    DARK_THEME = {
        'background': '#0F0F12',
        'panel': '#1A1B1E',
        'input_bg': '#25262B',
        'input_border': '#3C3E44',
        'input_focus': '#6C5CE7',
        'text_primary': '#FFFFFF',
        'text_secondary': '#9A9CA5',
        'text_placeholder': '#5D5F67',
        'accent': '#6C5CE7',
        'accent_hover': '#5A4EC7',
        'error': '#FF4757',
        'success': '#2ED573',
        'message_own': '#6C5CE7',
        'message_other': '#25262B',
    }
    
    # Светлая тема
    LIGHT_THEME = {
        'background': '#F5F7FA',
        'panel': '#FFFFFF',
        'input_bg': '#F0F2F5',
        'input_border': '#D1D5DB',
        'input_focus': '#6C5CE7',
        'text_primary': '#1A1B1E',
        'text_secondary': '#6B7280',
        'text_placeholder': '#9CA3AF',
        'accent': '#6C5CE7',
        'accent_hover': '#5A4EC7',
        'error': '#DC3545',
        'success': '#10B981',
        'message_own': '#6C5CE7',
        'message_other': '#E5E7EB',
    }
    
    def __init__(self):
        self.current_theme = 'dark'
        self.colors = self.DARK_THEME.copy()
    
    def set_theme(self, theme_name):
        """Устанавливает тему."""
        if theme_name == 'light':
            self.current_theme = 'light'
            self.colors = self.LIGHT_THEME.copy()
        else:
            self.current_theme = 'dark'
            self.colors = self.DARK_THEME.copy()
    
    def get_color(self, name):
        """Получает цвет по имени."""
        return self.colors.get(name, '#000000')
    
    def get_stylesheet(self, widget_type):
        """Получает QSS для типа виджета."""
        c = self.colors
        
        if widget_type == 'input':
            return f"""
                QLineEdit {{
                    background-color: {c['input_bg']};
                    color: {c['text_primary']};
                    border: 1px solid {c['input_border']};
                    border-radius: 16px;
                    padding: 16px 20px;
                    font-size: 18px;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
                QLineEdit:focus {{
                    border: 2px solid {c['input_focus']};
                }}
                QLineEdit::placeholder {{
                    color: {c['text_placeholder']};
                }}
            """
        
        elif widget_type == 'button_primary':
            return f"""
                QPushButton {{
                    background-color: {c['accent']};
                    color: white;
                    border: none;
                    border-radius: 14px;
                    padding: 16px 32px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {c['accent_hover']};
                }}
                QPushButton:disabled {{
                    background-color: {c['text_placeholder']};
                    color: {c['text_secondary']};
                }}
            """
        
        elif widget_type == 'button_secondary':
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {c['text_secondary']};
                    border: 1px solid {c['input_border']};
                    border-radius: 14px;
                    padding: 14px 28px;
                    font-size: 14px;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {c['input_bg']};
                    color: {c['text_primary']};
                }}
            """
        
        elif widget_type == 'label_title':
            return f"""
                QLabel {{
                    color: {c['text_primary']};
                    font-size: 24px;
                    font-weight: bold;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
            """
        
        elif widget_type == 'label_subtitle':
            return f"""
                QLabel {{
                    color: {c['text_secondary']};
                    font-size: 14px;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
            """
        
        elif widget_type == 'label_error':
            return f"""
                QLabel {{
                    color: {c['error']};
                    font-size: 13px;
                    font-family: Segoe UI, Arial, sans-serif;
                }}
            """
        
        return ""


# Глобальный экземпляр
theme_manager = ThemeManager()