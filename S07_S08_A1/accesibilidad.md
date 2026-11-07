# Evaluación de accesibilidad

Robbie · 6 de noviembre de 2026

La evaluación inicial y las correcciones las hice con apoyo de un agente de IA (Claude Code). El agente evaluó `AppButton`, `TextField`, `InfoCard` y `Navbar` contra WCAG 2.1 nivel AA en la página `/componentes`, en escritorio y a 360 px, con y sin sesión, con el menú móvil abierto y con un campo en error. Usó `axe-core` con las reglas WCAG 2.0 y 2.1 A y AA más buenas prácticas, mediciones propias de color y foco en Chrome, y pruebas con teclado, y propuso los cambios que luego se aplicaron y se volvieron a medir.

Después validé el resultado con herramientas externas para comprobar que nada se escapara: WAVE (extensión de WebAIM, que corrí yo en el navegador) y Lighthouse. Los resultados están en la sección 5.

Resultado final: axe devuelve 0 violaciones en todos los estados, Lighthouse da 100 y WAVE no detecta errores.

## Cambios más importantes

Son dos, y los dos afectan a las personas que más usarían la aplicación.

- Contraste: el mensaje de error medía 3.28:1, el texto atenuado 3.32:1 y el texto de ayuda de los campos 2.07:1, todos por debajo del 4.5:1 que pide WCAG. Ahora miden 5.46:1, 6.09:1 y 6.09:1. Es un cambio en `src/theme.ts` que vale para todos los componentes futuros.
- Foco con teclado: un botón en carga se deshabilitaba y el foco caía al `<body>`, y lo mismo pasaba al cerrar sesión. Quien navega con teclado o lector de pantalla perdía su posición en la página. Ahora el botón en carga sigue enfocable y, al cerrar sesión, el foco pasa al contenido principal.

Los demás cambios están en la sección 4.

## 1. Contraste

Colores calculados en el navegador (no leídos del código) y razones calculadas con la fórmula de WCAG. El umbral es 4.5:1 para texto y 3:1 para elementos no textuales (1.4.11).

| Combinación | Color / fondo | Antes | Ahora | Umbral |
|---|---|---|---|---|
| Botón primario, etiqueta | `#ffffff` / `#1971c2` | 3.56 (con `#228be6`) | 5.02 | 4.5 |
| Botón secundario, etiqueta | `#1971c2` / `#ffffff` | 3.56 | 5.02 | 4.5 |
| Botón secundario, borde | `#1971c2` / `#ffffff` | 3.56 | 5.02 | 3 |
| Etiqueta y texto escrito del campo | `#000000` / `#ffffff` | 21.0 | 21.0 | 4.5 |
| Texto de ayuda (placeholder) | `#5c636a` / `#ffffff` | 2.07 (`#adb5bd`) | 6.09 | 4.5 |
| Borde del campo en reposo | `#868e96` / `#ffffff` | 1.49 (`#ced4da`) | 3.32 | 3 |
| Borde del campo con error | `#c92a2a` / `#ffffff` | 3.28 (`#fa5252`) | 5.46 | 3 |
| Mensaje de error | `#c92a2a` / `#ffffff` | 3.28 | 5.46 | 4.5 |
| Descripción y rol (atenuado) | `#5c636a` / `#ffffff` | 3.32 (`#868e96`) | 6.09 | 4.5 |
| Títulos, enlaces de la barra, nombre | `#000000` / `#ffffff` | 21.0 | 21.0 | 4.5 |
| Anillo de foco | `#1971c2` / `#ffffff` | 5.02 | 5.02 | 3 |
| Barras del botón de menú | `#000000` / `#ffffff` | 21.0 | 21.0 | 3 |
| Ícono de cerrar del menú | `#495057` / `#ffffff` | 8.18 | 8.18 | 3 |

El botón primario ya se había corregido en la actividad anterior (`primaryShade: 8`). El texto atenuado y el gris claro (`#f8f9fa`) también cumplen: 5.78:1 para `#5c636a`. Ningún texto es "grande" según WCAG, así que se aplica 4.5:1 en todos.

## 2. Elementos sin texto visible

| Elemento | Qué le falta a la vista | Atributos |
|---|---|---|
| Botón de menú (hamburguesa) | Solo tiene tres barras | `aria-label` que cambia entre "Abrir menú" y "Cerrar menú", y `aria-expanded` |
| Botón de cerrar del panel | Solo tiene una X | `aria-label="Cerrar menú"` |
| Indicador de carga del botón | Es un giro sin texto | `aria-hidden`; el estado lo da `aria-busy` y `aria-disabled` en el botón, cuya etiqueta sigue visible |
| Panel del menú | Es un diálogo | Nombre por `aria-labelledby` del título "Menú" (Mantine) |

No hay otros íconos decorativos en los componentes. Con el menú abierto, axe no reporta ningún botón ni diálogo sin nombre.

## 3. Foco

Con el teclado en `/componentes` (todo medido con `:focus-visible` activo):

- Botones y enlaces: contorno sólido de 2 px `#1971c2` con separación de 2 px, 5.02:1.
- Campos: el mismo contorno, añadido en `src/accessibility.css` (Mantine solo cambia el borde de 1 px).
- Enlace del logo: contorno `auto` del navegador (`#005fcc`, 1 px).
- Menú móvil: al abrirlo, el foco pasa a "Cerrar menú". El Tab recorre "Cerrar menú", "Iniciar sesión", "Crear cuenta" y vuelve a "Cerrar menú", sin salir del panel (probé 8 pulsaciones: 0 salidas). Escape lo cierra y el foco vuelve al botón "Abrir menú".
- Botón en carga: conserva el foco.
- Cerrar sesión (escritorio): el foco pasa al contenido principal. Desde el menú móvil vuelve al botón de menú.

## 4. Problemas encontrados y correcciones

Los ordené por impacto. Los 1, 4 y 5 son los más críticos.

### 1. Mensaje de error con 3.28:1 · `TextField` · 1.4.3 · crítica
El error es la información que el usuario necesita para corregir (RNF-13).
```ts
// antes: color de error de Mantine (#fa5252)
// ahora, src/theme.ts
export const cssVariablesResolver: CSSVariablesResolver = () => ({
  variables: {},
  light: { '--mantine-color-error': '#c92a2a' }, // 5.46:1
  dark: {},
})
```
`#e03131` daba 4.51:1 sobre blanco pero 4.28:1 sobre gris claro, así que lo descarté.

### 2. Texto atenuado con 3.32:1 · `InfoCard`, `Navbar` · 1.4.3 · crítica
```ts
// antes: --mantine-color-dimmed = #868e96
// ahora, en el mismo resolver
'--mantine-color-dimmed': '#5c636a', // 6.09:1
```

### 3. Texto de ayuda con 2.07:1 · `TextField` · 1.4.3 · alta
axe no revisa el placeholder; lo medí aparte.
```ts
// antes: --mantine-color-placeholder = #adb5bd
// ahora, en el mismo resolver
'--mantine-color-placeholder': '#5c636a', // 6.09:1
```

### 4. Botón en carga pierde el foco · `AppButton` · 2.4.3 · crítica
La prop `loading` de Mantine deshabilita el botón. Al pulsar Enter, `document.activeElement` pasaba a `<body>`.
```tsx
// antes
<Button variant={...} size={size} loading={loading} {...props}>{children}</Button>

// ahora
const shared = {
  leftSection: loading ? <Loader size="sm" color="currentColor" aria-hidden /> : leftSection,
  'aria-busy': loading || undefined,
  'aria-disabled': loading || undefined,
  onClick: (event) => { if (loading) { event.preventDefault(); return } onClick?.(event) },
  ...
}
<Button {...shared}>{children}</Button>
```
No pasé `data-loading` porque Mantine lo usa para ocultar la etiqueta.

### 5. Foco perdido al cerrar sesión · `Navbar`, `AppLayout` · 2.4.3 · crítica
El botón "Cerrar sesión" desaparece y el foco caía al `<body>`.
```tsx
// antes
<AppButton onClick={logout}>Cerrar sesión</AppButton>

// ahora, AppLayout.tsx
const handleLogout = () => {
  document.getElementById('contenido')?.focus()
  logout()
}
<AppShell.Main id="contenido" tabIndex={-1}>
```
```css
/* accessibility.css: main no es interactivo, no necesita anillo */
main:focus { outline: none; }
```

### 6. Borde del campo con 1.49:1 · `TextField` · 1.4.11 · alta
Sin un borde visible, el campo blanco sobre fondo blanco no se distingue.
```css
/* antes: --input-bd = #ced4da */
[data-mantine-color-scheme='light'] .mantine-Input-input[data-variant='default']:not([data-error]):not(:focus) {
  --input-bd: #868e96; /* 3.32:1 */
}
```
Excluye foco y error para conservar sus colores. Medí los tres estados: gris `#868e96`, azul `#1971c2` y rojo `#c92a2a`.

### 7. Campo enfocado con solo 1 px de borde · `TextField` · 2.4.7 · media
```css
/* antes: Mantine solo cambia el color del borde */
input.mantine-Input-input:focus-visible {
  outline: 2px solid var(--mantine-color-blue-8);
  outline-offset: 2px;
}
```
Mi primera versión (`input:focus-visible`) no funcionaba: la regla `.mantine-Input-input:focus` de Mantine tiene mayor especificidad y anulaba el contorno. La medición en el navegador lo detectó.

### 8. Sin encabezado `h1` · páginas · 1.3.1, 2.4.6 · media
```tsx
// antes
<Title order={2}>Bienvenido a RepoSalud</Title>   // y el logo era <Title order={3}>
// ahora
<Title order={1} size="h2">Bienvenido a RepoSalud</Title>   // logo: <Text component="span" fw={700}>
// InfoCard: titleOrder por defecto 2
```

### 9. Sin elemento `nav` · `Navbar` · 1.3.1 · media
```tsx
// antes
<Group>{links.map(...)}</Group>
// ahora
<Group component="nav" aria-label="Principal">{links.map(...)}</Group>
```

### 10. `aria-controls` apuntaba a un elemento inexistente · `Navbar` · 4.1.2 · media
Lo introduje yo con el menú móvil y lo detectó axe. El `id` del `Drawer` de Mantine es solo un prefijo (`menu-movil-title`, `menu-movil-body`); ningún elemento se llama `menu-movil`.
```tsx
// antes
<Burger aria-expanded={opened} aria-controls="menu-movil" ... />
// ahora: se quita aria-controls; en un diálogo modal no aporta
<Burger aria-expanded={opened} aria-label={opened ? 'Cerrar menú' : 'Abrir menú'} />
```

### 11. Segundo landmark `banner` · `Navbar` · 1.3.1 · media
El encabezado del `Drawer` de Mantine es un `<header>` y axe lo contaba como un segundo `banner` junto a la barra.
```tsx
// antes
<Drawer opened={opened} onClose={close} title="Menú" ...>

// ahora
<Drawer.Root opened={opened} onClose={close} position="right" hiddenFrom="sm">
  <Drawer.Overlay />
  <Drawer.Content>
    <Drawer.Header role="presentation">
      <Drawer.Title>Menú</Drawer.Title>
      <Drawer.CloseButton size="xl" aria-label="Cerrar menú" />
    </Drawer.Header>
    <Drawer.Body>...</Drawer.Body>
  </Drawer.Content>
</Drawer.Root>
```

### 12. Botón de cerrar del menú de 28 × 28 px · `Navbar` · 2.5.5 (AAA) · baja
No incumple AA, pero es pequeño para un público de adultos mayores. Con `size="xl"` mide 44 × 44 px.

## 5. Validación con WAVE y Lighthouse

WAVE sobre `/componentes`: 0 errores, 0 errores de contraste, 1 alerta, 2 características (etiqueta de formulario e idioma), 8 elementos estructurales y 6 atributos ARIA. AIM Score: 10 de 10. WAVE advierte, como todas las herramientas automáticas, que las pruebas manuales siguen siendo necesarias.

La alerta es un enlace redundante: el logo "RepoSalud" y el enlace "Inicio" son adyacentes y llevan a la misma ruta (`/`). Decidí dejarlo. Es una advertencia para revisar con criterio, no un fallo. El logo como enlace al inicio es una convención, pero muchas personas con baja alfabetización digital (RNF-12) no saben que es pulsable, y "Inicio" con texto lo hace explícito.

Lighthouse 13.5.0, con la categoría de accesibilidad, en `/` y `/componentes`, en modo celular y escritorio: 100 en las cuatro corridas, sin fallos. Usa el mismo motor que axe, así que confirma ese resultado más que añadir uno nuevo. Solo evalúa la página recién cargada, con el menú cerrado y sin sesión, por eso los demás estados se cubrieron con axe y con las pruebas de teclado.

De las 10 revisiones que Lighthouse deja como manuales, cubrí seis con las pruebas de la sección 3: controles alcanzables con teclado, orden de tabulación lógico, sin trampas de foco (el menú atrapa el foco a propósito y Escape lo libera), foco gestionado al cargar y cerrar sesión, regiones `header`, `nav` y `main`, y controles con nombre. Quedan sin verificar que el orden visual siga el del código, que el contenido fuera de pantalla esté oculto para tecnologías de apoyo, y el foco al cambiar de ruta.

## Pendiente

- El título del documento es "RepoSalud" en todas las rutas, y no describe la página (2.4.2).
- No hay enlace para saltar al contenido. Hoy cumple por los puntos de referencia, pero con más enlaces en la barra convendrá añadirlo.
- El foco no se mueve al cambiar de ruta. Con una sola ruta real no se nota.
- El mensaje de error aparece al salir del campo pero no se anuncia en ese momento: Mantine no le pone `role="alert"`. El lector de pantalla lo lee al volver al campo, por `aria-describedby`. Lo mismo ocurre con el estado de carga, porque `aria-busy` no lo anuncian todos los lectores.
- Solo medí el modo claro; no hay modo oscuro.
- La escala de texto de RNF-11 sigue sin definirse (pendiente la lectura de "16 puntos").

## Mejoras a futuro

- Probar con un lector de pantalla real: VoiceOver en macOS y TalkBack en Android (RNF-18). Comprobar cómo se anuncian el botón del menú, el error de un campo y el botón en carga, y cómo se lee el menú móvil abierto. axe, Lighthouse y WAVE cubren una parte de WCAG, no todo, y esta prueba es la que más puede destapar.
