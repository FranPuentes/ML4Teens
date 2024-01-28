import openai;

from openai import OpenAI;

from ...core import Context;
from ...core import Block;

################################################################################
class OAIChat(Block):
      """
      Recibe una 'question' y responde con un 'answer'.
      Acumula la iteracción hasta que recibe un nuevo "context".
      """

      class OAI_QUERY:

            def __init__(self, client, messages:list):
                self.client=client;
                self.prompt=messages;
                self.aoigen=None;
                self.reason=None;

            def __iter__(self):
                return self;

            def __next__(self):
                if self.reason=="stop":   raise StopIteration();
                if self.reason=="length": raise StopIteration();
                if self.aoigen==None:
                   try:
                     self.aoigen=self.client.chat.completions.create(model="gpt-3.5-turbo", messages=self.prompt, stream=True);
                       
                   except openai.APIConnectionError as e:
                     raise e;
                       
                   except openai.RateLimitError as e:
                     raise e;
                       
                   except openai.APIStatusError as e:
                     raise e;
                       
                   except Exception as e:
                     raise StopIteration();

                for chunk in self.aoigen:
                    return (chunk.choices[0].delta.content or "");

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          context=Context.instance;
          self._client =OpenAI(api_key=self.params.api_key or context["OPENAI_KEY"],
                               max_retries=self.params.max_retries or 2,
                               timeout=self.params.timeout or 10.0,
                               base_url=self.params.base_url);
          self._context=self.params.context or "";
          self._history=[];

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("context",{str})
      def slot_context(self, slot, data):
          self._context=data or self.params.context or self._context;
          self._history=[];

      #-------------------------------------------------------------------------
      @Block.slot("question",{object})
      def slot_question(self, slot, data):
         
          if data is not None and isinstance(data,(str,)):
             self._history.append(data);
             messages=[];
    
             for i,h in enumerate(self._history):
                 if    i==0   : messages.append({"role":"system",    "content":h});
                 elif (i%2)==1: messages.append({"role":"user",      "content":h});
                 elif (i%2)==0: messages.append({"role":"assistant", "content":h});
    
             try:
               response="";
               for token in self.OAI_QUERY(self._client, messages):
                   if token is not None: response += token;
                   else:                 break;
    
             except Exception as e:
               print(e, flush=True);  
               if not response:
                  response="Me temo que se ha producido un error. Vuelve a intentarlo otra vez por favor.";
    
             finally:
               self._history.append(response);
               self.signal_answer  (response);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("answer",str)
      def signal_answer(self, data):
          return data;

