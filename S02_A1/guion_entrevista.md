# Guion de entrevista — RepoSalud

## Objetivo
Validar el problema (historial médico fragmentado) y la propuesta de valor de RepoSalud (repositorio centralizado, búsqueda conversacional, compartición temporal) con un usuario real antes de congelar la SRS.

## Perfil objetivo del entrevistado
Paciente con enfermedad crónica o catastrófica, o su cuidador principal (rol "Dueño" o "Cuidador" del sistema). Si la persona entrevistada es un médico tratante o especialista invitado, ajustar las preguntas 1, 2 y 5 a su perspectiva (ej. "¿cómo recibe hoy el historial de sus pacientes?" en vez de "¿dónde guarda su documentación?").

## Cómo usar este guion
Basado en la guía de Bridging the Gap sobre preguntas de elicitación: no se lee en orden ni se hacen todas literalmente. Se usan las preguntas abiertas para arrancar la conversación; muchas de las preguntas de seguimiento se contestan solas conforme la persona habla. El objetivo es una conversación natural, no un cuestionario.

Cada pregunta principal indica su **tipo** (Abierta / Seguimiento / Validación) y el **aspecto** que cubre (Funcional / No funcional / Dominio).

---

## 1. Situación actual de la documentación
**[Abierta · Funcional]**
Cuénteme cómo maneja hoy toda su documentación médica: ¿dónde la guarda —papel, fotos en el celular, portales de distintas clínicas— y qué hace cuando un médico se la pide?

**Seguimiento:**
- La última vez que tuvo que compartirla, ¿qué método usó (correo, WhatsApp, imprimir, llevarla en persona)? ¿Qué tan fácil o tardado fue ese proceso?

## 2. Recuperar información del historial
**[Abierta · Funcional]**
Piense en la última vez que necesitó encontrar un dato médico específico —una fecha de estudio, un resultado, una dosis. ¿Qué hizo para buscarlo y lo logró encontrar?

**Seguimiento:**
- ¿Qué le resultaría más cómodo para buscar: navegar una página web con carpetas, usar una app con filtros, o simplemente preguntar en un chat con sus propias palabras ("busca mi última radiografía de tórax")?

## 3. Memoria y dependencia de información olvidada
**[Abierta · Dominio]**
¿Qué tan seguido le pasa que no recuerda cuándo se hizo cierto estudio o cuál fue el resultado, y tiene que volver a buscarlo o preguntarle a su médico?

**Seguimiento:**
- Cuando eso pasa, ¿a quién o a qué recurre primero (memoria, familiar, llamar a la clínica, revisar papeles)?

## 4. Compartir con más de un médico
**[Abierta · Funcional / Dominio]**
Si hoy quisiera buscar una segunda opinión médica o cambiar de doctor, ¿podría reunir su historial clínico fácilmente? ¿Alguna vez esto ha sido un obstáculo real para cambiar de médico o pedir una segunda opinión?

**Seguimiento (sondea RD de roles/permisos):**
- ¿Ha tenido que compartir su documentación con alguien más que su médico tratante —un familiar, un especialista, una aseguradora? ¿Con quién, qué le compartió y para qué?
- Si pudiera darle acceso *temporal* a un especialista (que se le quite automáticamente después de un tiempo, sin que se quede con copias), ¿le parecería importante tener ese control?

## 5. Tolerancia a la incertidumbre en la búsqueda
**[Abierta con opciones · No funcional]**
Cuando busca un documento y el sistema no está completamente seguro de cuál es el correcto, ¿preferiría que le muestre varias opciones parecidas para elegir usted, o prefiere una sola respuesta aunque a veces se equivoque?

## 6. Urgencia y frecuencia de uso
**[Seguimiento con escala · No funcional]**
¿Qué tan seguido necesita consultar sus documentos médicos, y qué tan urgente suele ser cuando lo hace: lo necesita al momento, puede esperar unos minutos, o normalmente lo busca con uno o varios días de anticipación (por ejemplo antes de una cita)?

## 7. Confianza en respuestas automáticas (chat con IA)
**[Abierta · Dominio / Confianza]**
Imagine que le pregunta al sistema algo como "¿cuándo fue mi último estudio de glucosa?" y el sistema le responde directamente, señalando de qué documento sacó esa respuesta. ¿Confiaría en esa respuesta, o preferiría siempre revisar usted mismo el documento original?

---

## 8. Cierre — Validación de lo entendido
**[Validación]**
Para asegurarme de que entendí bien: usted necesita un lugar donde guardar todos sus documentos médicos sin importar el formato, poder encontrarlos fácilmente aunque no recuerde fechas exactas, y poder compartir accesos temporales y revocables con quien usted decida —¿es así, o hay algo que deba ajustar, quitar o que me esté faltando?

---

## Notas para el entrevistador
- No leer las preguntas literalmente ni en orden fijo; usarlas como referencia y dejar que la conversación fluya.
- Evitar preguntas que ya sugieran la respuesta esperada (ej. no decir "¿le gustaría un chat con IA?" antes de sondear cómo prefiere buscar hoy).
- Anotar literalmente frases del entrevistado que revelen vocabulario de dominio (términos que usa para nombrar estudios, documentos, roles) — sirven para la sección de Glosario de la SRS.
- Cerrar siempre con la pregunta de validación (#8), incluso si se cambió el orden o se omitieron preguntas por falta de tiempo.
