# RepoSalud

*Nombre tentativo del sistema*

## Problema que resuelve

El historial médico de un paciente está fragmentado. Prescripciones, resultados de laboratorio, imágenes diagnósticas y mediciones de signos vitales quedan dispersos entre portales de distintas clínicas, PDFs sueltos, fotos en el celular y papel físico. Este problema se agrava en las enfermedades catastróficas, cuyo tratamiento se extiende durante meses o años y genera un gran volumen de documentos.

Como resultado, encontrar un examen específico o revisar la evolución del paciente es lento y propenso a errores, y compartir la información con un médico (por ejemplo, para una segunda opinión) depende de enviar archivos manualmente por correo o WhatsApp, sin ningún control sobre quién los ve ni por cuánto tiempo.

## A quién va dirigido

- **Pacientes con enfermedades catastróficas o crónicas** que necesitan organizar y conservar su historial médico a largo plazo.
- **Familiares y cuidadores** que gestionan la información de salud del paciente y coordinan citas, tratamientos y consultas.
- **Médicos tratantes** que necesitan revisar la información del paciente de primera mano y de forma ordenada.
- **Especialistas invitados** que requieren acceso temporal para emitir una segunda opinión.

## Valor principal que entrega

RepoSalud centraliza en un solo lugar todo el historial médico del paciente —fotos, PDFs y documentos de texto— en un repositorio digital seguro, y permite recuperarlo mediante un buscador conversacional: basta con describir lo que se busca (por fecha, palabra clave o significado) para encontrar el documento correcto, sin tener que revisarlos uno por uno. La interfaz está pensada para ser simple de usar, considerando que gran parte de los usuarios son personas mayores.

Compartir el historial es igual de sencillo: el paciente genera un acceso temporal (un link) para su médico, cuidador o quien lo necesite, sin procesos complicados. En esta primera versión todos los accesos compartidos tienen el mismo nivel de permisos; la evolución natural del producto es permitir que el paciente configure niveles de acceso diferenciados, por ejemplo distinto para el médico tratante que para un especialista invitado por una segunda opinión.

Como evolución posterior al MVP, el sistema podrá no solo *encontrar* documentos sino *leer* su contenido para responder preguntas médicas puntuales (por ejemplo, "¿cuándo fue mi último estudio de glucosa?"), siempre señalando de qué documento obtuvo la respuesta — evitando así que el sistema invente información.

Al ser una solución propia, los datos médicos sensibles permanecen bajo control del paciente y no dependen de plataformas de terceros.