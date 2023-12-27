# ML4Teens

Machine Learning for *Teens* (Aprendizaje Automático para *adolescentes*)

Librería Python (ml4teens) para permitir crear "bloques" que lleven a cabo un proceso de ML.

Cad bloque hace algo concreto, posiblemente *matizado* por los parámetros
del usuario. Cada uno de ellos genera *signal*s y posee *slot*s.

Un objeto (*singleton*) se encarga de unos signals con slots (con control
de tipos).

