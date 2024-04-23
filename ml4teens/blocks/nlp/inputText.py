import ipywidgets as widgets;
from   IPython.display import display;

from ...core import Block;

################################################################################
class InputText(Block):
      """
      Pide al usuario que introduzca un texto.
      Espera a que pulse el botón de enviar.
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("ask",{object})
      def slot_ask(self, slot, data):

          caption = widgets.Label(value=self.params.caption or '?: ',layout=widgets.Layout(width='auto'));
          text    = widgets.Text(value=self.params.value or '',layout=widgets.Layout(flex='1 1 auto'));
          button  = widgets.Button(description=self.params.submit or "Submit");
          hbox    = widgets.HBox([caption, text, button]);

          pressed = False;
          def on_button_event(b):
              nonlocal pressed;
              self.signal_stdout(text.value);
              pressed=True;              
          button.on_click(on_button_event);
        
          display(hbox);
          Block.waitUntil(lambda:pressed);
          text.  disabled=True;
          button.disabled=True;

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("out",str)
      def signal_stdout(self, data):
          return data;
          
          