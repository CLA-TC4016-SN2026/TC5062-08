# Revisión de componentes

Robbie · 6 de noviembre de 2026

Revisé los cuatro componentes de `frontend/src/components/` contra tres criterios: props bien definidas, estilos responsivos básicos y qué cambió respecto a la propuesta inicial del agente. Además de leer el código, los ejercité en Chrome con un script de Puppeteer a 1000, 360 y 320 px de ancho: estado de carga, validación, cambio de sesión en la barra, desbordamiento horizontal y errores de consola. El script vive fuera del proyecto y no se versiona.

## Botón (`AppButton.tsx`)

Props:

| Prop | Tipo | Notas |
|---|---|---|
| `variant` | `'primary' \| 'secondary'` | Por defecto `primary`. Primaria es relleno; secundaria es contorno. |
| `children` | `ReactNode` | Obligatoria. La etiqueta va en palabras (RNF-11). |
| `loading` | `boolean` | Muestra un indicador junto a la etiqueta y anuncia `aria-busy`. El botón sigue enfocable y ignora los clics. |
| `to` | `string` | Si se indica, navega y se renderiza como enlace. |
| `fullWidthOnMobile` | `boolean` | Ancho completo bajo 48em y ancho natural en adelante. |
| `size`, `disabled`, `type`, `onClick` | | `size` por defecto `lg`. El resto, como en Mantine. |

Responsivo: con `fullWidthOnMobile`, a 360 px el botón mide 254 px dentro de una tarjeta de 296 (el ancho útil), y a 1000 px mide 122 px. Sin la prop conserva su ancho natural.

Cambios:
- El tamaño por defecto pasó de `md` a `lg`. En `md` el botón mide 36 px de alto, poco para dedos de adultos mayores en un celular. En `lg` mide 50 px, medido en el navegador. Además acerca el texto al tamaño grande que pide RNF-11.
- Añadí `fullWidthOnMobile`. En formularios de celular el botón principal a todo el ancho es más fácil de tocar, y la propuesta inicial no daba forma de lograrlo.
- Reimplementé `loading` (revisión de accesibilidad, ver `accesibilidad.md`): la prop de Mantine deshabilita el botón y el foco del teclado cae al `<body>`.
- Añadí `to`. La propuesta usaba la prop `component` de Mantine para convertir el botón en enlace, y eso no compila con TypeScript porque el tipo del evento `onClick` choca entre botón y ancla. `to` resuelve el caso sin esa fricción.

## Campo de entrada (`TextField.tsx`)

Props:

| Prop | Tipo | Notas |
|---|---|---|
| `label` | `string` | Obligatoria. Queda enlazada al campo con `for`/`id`. |
| `validate` | `(value: string) => string \| null` | Se ejecuta al salir del campo. Devuelve el mensaje o `null`. |
| `error` | `ReactNode` | Tiene prioridad sobre el error de `validate`, para formularios con validación propia. |
| `size` | | Por defecto `lg`. |
| Resto | | Las de `TextInput` de Mantine: `placeholder`, `required`, `type`, `value`, `onChange`, `autoComplete`, etc. |

Responsivo: el campo ocupa el 100 % del ancho de su contenedor, así que se adapta solo. No hay desbordamiento a 320 px.

Cambios:
- Tamaño por defecto `lg`, por las mismas razones que el botón.
- Reescribí el manejo de `onChange`. La propuesta lo anulaba con un truco al propagar `props`, que era difícil de leer y fácil de romper. Ahora se extrae y se llama de forma explícita.
- El borde en reposo pasó de `#ced4da` (1.49:1) a `#868e96` (3.32:1), para cumplir el 3:1 de WCAG 1.4.11. Los bordes de foco y de error conservan sus colores.
- Verifiqué el comportamiento: un correo mal escrito muestra el error al salir del campo, y al corregirlo el error desaparece.

## Tarjeta (`InfoCard.tsx`)

Props:

| Prop | Tipo | Notas |
|---|---|---|
| `title` | `string` | Obligatoria. |
| `titleOrder` | `2 \| 3 \| 4 \| 5 \| 6` | Nivel del encabezado. Por defecto 2. |
| `description` | `string` | Opcional, en gris. |
| `children` | `ReactNode` | Contenido principal. |
| `footer` | `ReactNode` | Opcional. Va al pie, en una fila que pasa a varias líneas si no cabe. |

Responsivo: la tarjeta es fluida. En la página de muestra, dos columnas desde 48em y una en celular.

Cambios:
- El título era un `h4` fijo, lo que se salta niveles de encabezado y confunde a los lectores de pantalla. Ahora el nivel es configurable, con 2 por defecto (debajo del `h1` de la página), y el tamaño visual se mantiene con `size="h4"`.
- El pie ahora va dentro de un `Group`, de modo que varios botones se acomoden en filas en vez de desbordar.

## Barra de navegación (`Navbar.tsx`)

Props:

| Prop | Tipo | Notas |
|---|---|---|
| `isAuthenticated` | `boolean` | Obligatoria. Decide qué acciones se muestran. |
| `userName` | `string \| null` | Obligatoria. Se muestra con la sesión iniciada. |
| `userRole` | `'paciente' \| 'cuidador' \| 'medico' \| null` | Obligatoria. Se muestra en español bajo el nombre. |
| `onLogout` | `() => void` | Obligatoria. La barra no sabe cómo se cierra la sesión. |
| `links` | `{ label: string; to: string; public?: boolean }[]` | Opcional. Van dentro de un `nav` con `aria-label`. Los marcados `public` se ven siempre; el resto, solo con la sesión iniciada. |

La barra es solo presentación. `AppLayout` lee la sesión de `useAuth()` y se la pasa por props, y también decide a dónde va el foco al cerrar sesión.

Responsivo: desde 48em muestra los enlaces y las acciones en la barra. Por debajo, muestra el logo y un botón de menú (hamburguesa) que abre un panel lateral con el nombre, el rol, los enlaces y las acciones. El panel es un `Drawer` de Mantine: abre como diálogo, atrapa el foco, se cierra con Escape y devuelve el foco al botón. No hay desbordamiento a 360 ni 320 px.

Cambios:
- Pasó de leer el contexto a recibir props, como pide el ejemplo de prompts de la actividad. Es más fácil de probar y mantiene los componentes sin lógica de sesión.
- Añadí el menú hamburguesa. Antes "Crear cuenta" se ocultaba en celular y un usuario nuevo no podía registrarse desde la barra. Ahora ambas acciones están en el menú.
- Muestra el rol del usuario.
- Los enlaces pueden marcarse `public`. Sin eso, un usuario sin sesión veía una barra sin navegación. `AppLayout` incluye un enlace temporal a `/componentes`, la página de muestra de los cuatro componentes, que se quita cuando existan las pantallas reales.
- El logo era un `Title` con la prop `component` de Mantine, que no admite `to` en TypeScript. Ahora es un enlace con texto, sin ser un encabezado.
- Los botones de la barra usan `to` en lugar de `component`, por lo mismo que el botón.
- El menú se arma con las piezas del `Drawer` por separado: su encabezado automático contaba como un segundo landmark `banner` (ver `accesibilidad.md`).
- El botón de cerrar del menú pasó a 44 × 44 px; por defecto medía 28 × 28.
- Comprobé los dos estados en escritorio y celular, que la sesión sobrevive a una recarga y se borra al cerrar sesión, y que el foco no cae al `<body>`.

## Pendiente

- Los botones "Iniciar sesión" y "Crear cuenta" llevan a `/ingresar` y `/registro`, que aún no existen.
- La validación del campo es solo al salir de él. Los formularios reales usarán React Hook Form y pasarán el resultado por `error`.
- Falta la lectura de los "16 puntos" de RNF-11, de la que depende la escala de texto global.
- No probé en un Android 8 ni en un emulador (RNF-15, RNF-18). Las pruebas automáticas con Vitest quedan para la fase 2.
