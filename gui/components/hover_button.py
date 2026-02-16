"""Hover button component with visual feedback"""

import tkinter as tk


class HoverButton(tk.Button):
    """
    Custom button with hover effects
    
    Highlights on mouse enter, returns to normal on mouse leave
    """
    
    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        """Handle mouse enter - highlight button"""
        self['background'] = self['activebackground']
    
    def on_leave(self, e):
        """Handle mouse leave - restore original color"""
        self['background'] = self.defaultBackground
