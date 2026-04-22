# 🚗 Precios Arriendo Autos Chile — Guía de instalación

## ¿Qué hace este proyecto?
- Muestra una tabla de precios de arriendo de autos en Chile, ordenados por región y categoría
- Intenta extraer precios automáticamente de rentalcars.cl una vez al día
- Te manda un mensaje a Telegram cada vez que se actualizan los precios
- Guarda los datos en tu navegador (no se pierden al cerrar)

---

## PASO 1 — Crear repositorio en GitHub (5 minutos)

1. Ve a **github.com** y entra a tu cuenta
2. Haz clic en el botón verde **"New"** (arriba a la izquierda)
3. En **"Repository name"** escribe: `precios-arriendo-cl`
4. Deja todo lo demás como está y haz clic en **"Create repository"**
5. En la página que aparece, haz clic en **"uploading an existing file"**
6. Arrastra los 3 archivos de esta carpeta (`index.html`, `vercel.json`, `README.md`)
7. Haz clic en **"Commit changes"** (botón verde al final)

✅ ¡Tu código ya está en GitHub!

---

## PASO 2 — Publicar en Vercel (5 minutos)

1. Ve a **vercel.com** y entra con tu cuenta GitHub (botón "Continue with GitHub")
2. Haz clic en **"Add New → Project"**
3. Busca tu repositorio `precios-arriendo-cl` y haz clic en **"Import"**
4. No cambies nada — haz clic directo en **"Deploy"**
5. Espera 1-2 minutos. Vercel te da una URL como `precios-arriendo-cl.vercel.app`

✅ ¡Tu página está publicada y accesible desde cualquier lugar!

---

## PASO 3 — Configurar Telegram (10 minutos)

### 3a. Crear tu bot
1. Abre Telegram y busca **@BotFather**
2. Escríbele: `/newbot`
3. Elige un nombre para tu bot (ej: "Arriendo CL Bot")
4. Elige un username que termine en `bot` (ej: `arriendocl_bot`)
5. BotFather te dará un **Token** — cópialo, se ve así: `1234567890:ABCdef...`

### 3b. Obtener tu Chat ID
1. Busca **@userinfobot** en Telegram
2. Escríbele cualquier mensaje
3. Te responderá con tu **Id** (número de 8-9 dígitos) — ese es tu Chat ID

### 3c. Conectar con la página
1. Abre tu página en Vercel
2. Al cargar por primera vez, aparecerá un cuadro preguntando si configurar Telegram
3. Pega tu **Token** de BotFather
4. Pega tu **Chat ID** de @userinfobot
5. ¡Listo! Cada vez que se actualicen los precios te llegará un mensaje

---

## PASO 4 — Usar la página

### Para extraer precios automáticamente:
- Haz clic en **"↻ Actualizar ahora"**
- El sistema intentará extraer precios de 6 ciudades de Chile
- ⚠️ Importante: rentalcars.cl puede bloquear robots. Si falla, usa el método manual.

### Si el scraping automático falla:
- Haz clic en **"+ Agregar manual"**
- Llena el formulario con los precios que ves en rentalcars.cl
- Los datos se guardan automáticamente en tu navegador

### Filtros disponibles:
- **Región**: filtra por región de Chile
- **Categoría**: Económico, Compacto, SUV, etc.
- **Buscar modelo**: busca un auto específico

### Actualización automática:
- La página recuerda cuándo fue la última actualización
- Si han pasado más de 24 horas, intenta actualizar sola al abrir

---

## ⚠️ Advertencia importante sobre el scraping

rentalcars.cl (powered by Booking.com) usa protecciones anti-robot. El scraping automático:
- Puede funcionar algunos días y fallar otros
- No está garantizado a largo plazo
- Usar sus datos sin permiso puede ir contra sus términos de uso

**Alternativa recomendada**: Ingresar los precios manualmente desde el formulario, consultando el sitio directamente. Los datos persisten en tu navegador.

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| "No se pudo extraer" | Usa "+ Agregar manual" |
| No llega mensaje Telegram | Verifica el Token y Chat ID en la configuración |
| Los datos desaparecieron | Revisa que no hayas borrado datos del navegador |
| La página no carga | Verifica el deploy en vercel.com |

---

## Actualizar el código en el futuro

Si quieres modificar algo:
1. Ve a tu repositorio en GitHub
2. Haz clic en `index.html`
3. Haz clic en el ícono del lápiz (editar)
4. Haz tus cambios y haz clic en **"Commit changes"**
5. Vercel re-desplegará automáticamente en 1-2 minutos
