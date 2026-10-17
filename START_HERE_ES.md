# Primera versión del portafolio

Esta es una base de trabajo para revisar y aprender, no una afirmación de experiencia que todavía no puedas demostrar. El contenido público principal está en inglés para facilitar la revisión por equipos internacionales.

## Tres casos y su estado real

1. **Location Data Quality:** demostración nueva con datos sintéticos; código y resultados incluidos.
2. **Location Screening:** demostración nueva con cuatro ubicaciones ficticias, escenarios y dashboard; código y resultados incluidos.
3. **GEOTIP:** documentación de tu repositorio público existente y revisión técnica de sus limitaciones. No se modificó el repositorio original ni se verificó la aplicación en vivo.

Los dos ejercicios Python fueron preparados con asistencia de IA. Antes de presentarlos como parte de tu portafolio debes ejecutarlos, explicar sus decisiones y realizar cambios propios que puedas defender. No los describas como proyectos de clientes ni atribuyas ganancias comerciales o tiempos ahorrados que no se hayan medido.

## Empezar en tu computador

1. Descomprime esta carpeta.
2. Abre una terminal en la carpeta que contiene `README.md`.
3. Ejecuta `python src/portfolio.py` o `py src/portfolio.py` en Windows.
4. Ejecuta `python -m unittest discover -s tests -v`.
5. Abre `outputs/dashboard.html` en un navegador.
6. Revisa el CSV de cuarentena y el informe ejecutivo: cada descarte y cada recomendación deben tener una explicación.

Necesitas Python 3.10 o posterior. Estos ejemplos usan únicamente la biblioteca estándar. No requieren instalar ArcGIS ni bibliotecas externas.

## Publicación en GitHub

Repositorio sugerido: `geospatial-analytics-portfolio`, dentro de `sergiopreserva`. Es un repositorio nuevo; su URL no existe hasta crearlo.

Crear repositorio: https://github.com/new?name=geospatial-analytics-portfolio&owner=sergiopreserva&visibility=public

Tras revisar los archivos, crea el repositorio y sube **el contenido descomprimido**, no solamente el ZIP. El `README.md` principal debe quedar en la raíz. Conserva la estructura de carpetas. Alternativamente, usa GitHub Desktop para publicar esta carpeta.

Guía oficial: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository

El HTML no se ejecuta dentro del visor de archivos de GitHub: se puede descargar y abrir localmente. La figura incluida resume los resultados; no es una captura del dashboard. No hay un sitio web desplegado en esta versión.

## Para Placer.ai

Prioriza estas evidencias: integración y validación de datos; automatización con Python; análisis espacial; herramientas para clientes; explicación de una recomendación y sus límites.

Hay dos brechas que esta versión no resuelve: experiencia real con Power BI/Tableau y fluidez oral profesional en inglés. Un dashboard HTML no sustituye una implementación de BI. El análisis ponderado tampoco prueba dominio de estadística inferencial.

## Siguiente trabajo concreto

- Explicar los dos ejemplos en inglés durante dos minutos cada uno.
- Cambiar una regla de calidad y una hipótesis del modelo, y explicar cómo cambian los resultados.
- Incorporar una captura pública autorizada de GEOTIP y corregir su README y el alcance de sus indicadores en una revisión separada.
- Recrear un informe en Power BI/Tableau con un dataset apropiado si decides cubrir ese requisito.
- Incorporar otros proyectos profesionales únicamente con evidencia y autorización de publicación de sus datos y entregables.
