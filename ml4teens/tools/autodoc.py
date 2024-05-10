# -*- coding: utf-8 -*-

import pkgutil;
import inspect;

#===============================================================================
__AUTODOC__ = None;

def autodoc():

    from .. import core;
    from .. import blocks;
    
    global __AUTODOC__;

    if __AUTODOC__ is not None:
    
       return __AUTODOC__;
       
    else:

       def U(s):
           if s: return s;
           else: return "";

       def _doc(paquete):

           def _signals(cls):
               rt=[];
               for name, obj in inspect.getmembers(cls, predicate=lambda obj: inspect.isfunction(obj)):
                   if hasattr(obj, '_is_signal'):
                      _type="*" if obj._type is object else obj._type.__name__;
                      rt.append({"name":obj._signal_name, "doc":U(obj.__doc__), "type":_type, "sync":obj._is_sync});
               return rt;

           def _slots(cls):
               rt=[];
               for name, obj in inspect.getmembers(cls, predicate=lambda obj: inspect.isfunction(obj)):
                   if hasattr(obj, '_is_slot'):
                      _types=[("*" if _type is object else _type.__name__) for _type in obj._types];
                      rt.append({"name":obj._slot_name, "doc":U(obj.__doc__), "types":_types, "default":obj._default});
               return rt;

           def _parameters(cls):
               for name, obj in inspect.getmembers(cls, predicate=lambda obj: not inspect.isroutine(obj)):
                   if name=="parameters":
                      return obj;
               return [];

           def _classes(pkg):
               rt=[];
               for name, obj in inspect.getmembers(pkg, predicate=lambda obj: inspect.isclass(obj) and issubclass(obj, core.Block) and obj is not core.Block):
                   description=[];
                   details    =[];
                   if obj.__doc__:
                      s=0;
                      for line in [l.strip() for l in U(obj.__doc__.strip()).split('\n')]:
                          if s==0:
                             if line: description.append(line)
                             else:    s=1;
                          else:
                             if line: details.append(line);

                   if description: description='\n'.join(description);
                   else:           description="";

                   if details: details='\n'.join(details);
                   else:       details="";

                   rt.append({"name": name,
                              "fullpath": f"{obj.__module__}.{obj.__qualname__}",
                              "description": description,
                              "details": details,
                              "parameters": _parameters(obj),
                              "slots": _slots(obj),
                              "signals": _signals(obj),
                             });
               return rt;

           rt=[];
           for importer, modname, ispkg in pkgutil.walk_packages(paquete.__path__, paquete.__name__ + "."):
               if ispkg:
                  pkg = __import__(modname, fromlist="dummy");
                  blocks = _classes(pkg);
                  rt.append( {"package":modname, "blocks":blocks} );
           return rt;
       
       __AUTODOC__ = _doc(blocks);
       
       return __AUTODOC__;

#===============================================================================
__long_html_str_template="""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Interfaz de Bloque</title>
<style>

body {
    font-family: Arial, sans-serif;
}

.clase-caja {
    border: 2px solid #333;
    width: 600px;
    padding: 10px;
    background-color: {{box_dark_bgcolor}};
    margin: 20px auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-radius: 10px; /* Esquina redondeada */
}

.nombre-módulo {
    font-family: Times new roman;
    text-align: left;
    font-weight: normal;
    margin-bottom: 20px;
    font-size: 15px;
    color: #777777;
}

.nombre-clase {
    text-align: center;
    font-weight: bold;
    margin-bottom: 20px;
    font-size: 30px;
    color: white;          /* Establece el color del texto a blanco */
    font-weight: bold;     /* Aplica negrita al texto */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); /* Añade sombra negra */
}

hr {
    border-top: 1px dashed #000; /* Define el borde superior como discontinuo */
    border-width: 1px; /* Ajusta el grosor del borde */
    border-color: black; /* Color del borde */
    border-style: dashed; /* Estilo discontinuo */
    border-bottom: none; /* Elimina el borde inferior para evitar doble línea */
    margin: 20px 0; /* Espacio antes y después del hr */
}

.dashed-line {
    border-top: 1px dashed #000; /* Línea discontinua */
    border-bottom: none; /* Asegura que no haya borde inferior */
}

.solid-line {
    border-top: 2px solid #333; /* Línea sólida más gruesa */
    border-bottom: none; /* Asegura que no haya borde inferior */
}

.texto-antes, .texto-despues {
    text-align: left; /* Alineación del texto */
    margin: 10px 0; /* Espacio antes y después del texto */
    padding-left: 10px; /* Alineación con el contenido de los parámetros */
    padding-right: 10px; /* Alineación con el contenido de los parámetros */
}

.parametros {
    text-align: left; /* Alinea el texto del encabezado y los elementos de la lista a la izquierda */
    margin-bottom: 20px;
    padding-left: 0px; /* Añade un poco de padding para no pegar el texto al borde */
}

.parametros h4 {
    font-size: 16px;
    color: white;          /* Establece el color del texto a blanco */
    font-weight: bold;     /* Aplica negrita al texto */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); /* Añade sombra negra */
}

.parametros ul {
    list-style-type: none;
    padding: 0;
    margin-top: 5px;
    padding-left: 0; /* Asegura que la lista no tenga padding extra a la izquierda */
}

.parametros li {
    background-color: {{box_light_bgcolor}};
    margin: 5px 0;
    padding: 5px;
    text-align: left;
}

.contenidos {
    display: flex;
    justify-content: space-between;
}

.slots, .senales {
    width: 45%;
}

.slots h4, .senales h4 {
    font-size: 16px;
    text-align: center;
    color: white;          /* Establece el color del texto a blanco */
    font-weight: bold;     /* Aplica negrita al texto */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); /* Añade sombra negra */
}

ul {
    list-style-type: none;
    padding: 0;
}

ul li {
    background-color: {{box_light_bgcolor}};
    margin: 5px 0;
    padding: 5px;
    text-align: left;
    position: relative;
    border-radius: 10px; /* Esquina redondeada */
}

.slots li::before {
    content: '→';
    position: absolute;
    left: -33px;
    color: red;
    font-size: 40px;  /* Tamaño ajustado para visibilidad */
}

.senales li::after {
    content: '→';
    position: absolute;
    right: -33px;
    color: red;
    font-size: 40px;  /* Tamaño ajustado para visibilidad */
}

.slots li::before, .senales li::after {
    top: 25%; /* Asegura que el inicio del elemento esté a la mitad de la altura del li */
    transform: translateY(-50%); /* Desplaza el elemento hacia arriba la mitad de su propia altura */
}

</style>
</head>
<body>
<div class="clase-caja">
    <div class="nombre-módulo">{{module}}</div>
    <hr class="solid-line"/>
    <div class="nombre-clase">{{class.name}}</div>
    <hr class="solid-line"/>
    {% if class.description %}
       <div class="texto-antes"><b>Breve descripción</b><br>{{class.description|replace('\n', '<br/>')}}</div>
       <hr class="dashed-line"/>
    {% endif %}
    {% if class.parameters %}
       <div class="parametros">
           <h4>Parámetros</h4>
           <ul>
               {% for parameter in class.parameters %}
                  <li><b>{{parameter.name}}</b>:{{parameter.type}} ("{{parameter.default}}" por defecto) {{parameter.doc}}</li>
               {% endfor %}
           </ul>
       </div>
       <hr class="dashed-line"/>
    {% endif %}
    {% if class.details %}
       <div class="texto-despues"><b>Detalles</b><br>{{class.details|replace('\n', '<br/>')}}</div>
       <hr class="dashed-line"/>
    {% endif %}
    <div class="contenidos">
        <div class="slots">
            <h4>Slots</h4>
            <ul>
                {% for slot in class.slots %}
                <li><b>{{slot.name}}</b>: {{slot.types | join(' | ')}} {{slot.doc}}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="senales">
            <h4>Señales</h4>
            <ul>
                {% for signal in class.signals %}
                <li><b>{{signal.name}}</b>: {{signal.type}} {%if signal.sync%}🔥&nbsp;{%endif%} {{signal.doc}}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
</body>
</html>
"""

__short_html_str_template="""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Interfaz de Bloque (short)</title>
<style>

body {
    font-family: Arial, sans-serif;
}

.clase-caja {
    border: 2px solid #333;
    width: {{box_width}};
    padding: 10px;
    background-color: {{box_dark_bgcolor}};
    margin: 20px auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    /*border-radius: 10px; */
}

.nombre-módulo {
    font-family: Times new roman;
    text-align: left;
    font-weight: normal;
    /*margin-bottom: 10px;*/
    font-size: 15px;
    color: #777777;
}

.nombre-clase {
    text-align: center;
    font-weight: bold;
    /*margin-bottom: 5px;*/
    font-size: 20px;
    color: #F74747;
    font-weight: bold;
    /*text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);*/
}

hr {
    border-top: 1px dashed #000; /* Define el borde superior como discontinuo */
    border-width: 1px; /* Ajusta el grosor del borde */
    border-color: black; /* Color del borde */
    border-style: dashed; /* Estilo discontinuo */
    border-bottom: none; /* Elimina el borde inferior para evitar doble línea */
    /*margin: 20px 0; */
}

.dashed-line {
    border-top: 1px dashed #000; /* Línea discontinua */
    border-bottom: none; /* Asegura que no haya borde inferior */
}

.solid-line {
    border-top: 2px solid #333; /* Línea sólida más gruesa */
    border-bottom: none; /* Asegura que no haya borde inferior */
}

.texto-antes, .texto-despues {
    text-align: left; /* Alineación del texto */
    margin: 10px 0; /* Espacio antes y después del texto */
    padding-left: 10px; /* Alineación con el contenido de los parámetros */
    padding-right: 10px; /* Alineación con el contenido de los parámetros */
}

.contenidos {
    display: flex;
    justify-content: space-between;
}

.slots, .senales {
    width: 45%;
}

.slots h4, .senales h4 {
    font-size: 14px;
    text-align: center;
    color: black;
    font-weight: bold;
    /*text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); */
}

.slots h4 {
    text-align: left;
}

.senales h4 {
    text-align: right;
}

.slots li {
    text-align: left;
}

.senales li {
    text-align: right;
}

ul {
    list-style-type: none;
    padding: 0;
}

ul li {
    font-size: 12px;
    background-color: {{box_light_bgcolor}};
    margin: 5px 0;
    padding: 5px;
    text-align: left;
    position: relative;
    /*border-radius: 10px; */
}

.slots li::before {
    content: '→';
    position: absolute;
    left: -33px;
    color: red;
    font-size: 40px;  /* Tamaño ajustado para visibilidad */
}

.senales li::after {
    content: '→';
    position: absolute;
    right: -33px;
    color: red;
    font-size: 40px;  /* Tamaño ajustado para visibilidad */
}

.slots li::before, .senales li::after {
    top: 25%; /* Asegura que el inicio del elemento esté a la mitad de la altura del li */
    transform: translateY(-50%); /* Desplaza el elemento hacia arriba la mitad de su propia altura */
}

</style>
</head>
<body>
<div class="clase-caja">
    <div class="nombre-módulo">{{module|e}}</div>
    <hr class="solid-line"/>
    <div class="nombre-clase">{{class.name|e}}</div>
    {% if class.parameters %}
       <div class="parametros">
           <h4>Parámetros</h4>
           <ul>
               {% for parameter in class.parameters %}
                  <li><b>{{parameter.name|e}}</b>:{{parameter.type|e}} ("{{parameter.default|e}}" por defecto) {{parameter.doc|e}}</li>
               {% endfor %}
           </ul>
       </div>
       <hr class="dashed-line"/>
    {% endif %}
    <div class="contenidos">
        <div class="slots">
            <h4>Slots</h4>
            <ul>
                {% for slot in class.slots %}
                <li><b>{{slot.name|e}}</b></li>
                {% endfor %}
            </ul>
        </div>
        <div class="senales">
            <h4>Señales</h4>
            <ul>
                {% for signal in class.signals %}
                <li>{%if signal.sync%}🔥{%endif%} <b>{{signal.name|e}}</b></li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
</body>
</html>
"""

# TODO parámetros S/N.
# TODO señales S/N.
# TODO parámetros/señales desplegables.
# TODO parametrizar colores.
# TODO documentación inline o pushup.

def class_html(full_class_name, short=True):

    from jinja2 import Template;
    
    if short: template = Template(__short_html_str_template);
    else:     template = Template(__long_html_str_template);

    def boxdoc_class(pkg_name, classes, full_class_name):
        for cls in classes:
            if cls["fullpath"]==full_class_name:
               module_name, _ = full_class_name.rsplit('.',1);
               unit={};
               unit["module"]=pkg_name;
               unit["class"]=cls;
               return unit;

    def boxdoc_module(docs, full_class_name):
        for doc in docs:
            r = boxdoc_class(doc["package"], doc["blocks"], full_class_name);
            if r is not None: return r;
        raise RuntimeError(f"Clase no encontrada: '{full_class_name}'");

    gvars={ "box_dark_bgcolor" :"PaleGoldenRod",
            "box_light_bgcolor":"PapayaWhip",
            "box_width":"300px",
          };

    if full_class_name.startswith("."):
       full_class_name=f"ml4teens.{full_class_name[1:]}";
        
    if full_class_name.startswith("ml."):
       full_class_name=f"ml4teens.{full_class_name[3:]}";
        
    rawdoc=boxdoc_module(autodoc(), full_class_name);
    return template.render(rawdoc, **gvars);
    