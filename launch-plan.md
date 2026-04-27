# Plan de Lanzamiento Open Source — portctl

## Estado actual

`portctl` es un script Python de un solo archivo con un instalador Bash. No tiene repositorio git, licencia, documentación, tests, ni empaquetado formal.

---

## Fase 1: Fundamentos del proyecto

### 1.1 Inicializar repositorio Git
- [ ] `git init`
- [ ] Crear `.gitignore` (Python, macOS, IDEs)
- [ ] Primer commit con el código actual

### 1.2 Elegir y agregar licencia
- [ ] Decidir licencia (MIT recomendada por simplicidad)
- [ ] Crear archivo `LICENSE`

### 1.3 Crear README.md
- [ ] Descripción del proyecto (bilingue o en inglés para mayor alcance)
- [ ] Badges (licencia, versión, CI)
- [ ] Instalación
- [ ] Uso con ejemplos de cada comando (`list`, `kill`, `interactive`)
- [ ] Requisitos (macOS, Python 3)
- [ ] Sección de contribución

### 1.4 Agregar archivo de metadatos
- [ ] Definir versión inicial (`0.1.0`)
- [ ] Agregar `__version__` en `portctl.py`

---

## Fase 2: Empaquetado y dependencias

### 2.1 Crear `pyproject.toml`
- [ ] Definir metadata del proyecto (nombre, versión, autor, descripción, URLs)
- [ ] Declarar dependencias: `psutil`, `typer`, `rich`
- [ ] Configurar entry point: `portctl = portctl:app` (o equivalente)
- [ ] Definir `requires-python >= 3.9`

### 2.2 Crear `requirements.txt` (opcional, para desarrollo)
- [ ] Pinear versiones mínimas de dependencias

### 2.3 Reestructurar el proyecto (opcional pero recomendado)
- [ ] Mover `portctl.py` a `src/portctl/__init__.py` o `src/portctl/cli.py`
- [ ] Esto permite instalación con `pip install .` y distribución en PyPI

---

## Fase 3: Calidad de código

### 3.1 Linting y formateo
- [ ] Agregar configuración de `ruff` en `pyproject.toml`
- [ ] Formatear código existente
- [ ] Resolver cualquier warning

### 3.2 Type hints
- [ ] Revisar y completar type hints en funciones públicas

### 3.3 Tests
- [ ] Agregar `pytest` como dependencia de desarrollo
- [ ] Escribir tests unitarios básicos (parsing de puertos, lógica de filtrado)
- [ ] Agregar tests de integración del CLI (usando `typer.testing.CliRunner`)

---

## Fase 4: Documentación de comunidad

### 4.1 CONTRIBUTING.md
- [ ] Cómo configurar el entorno de desarrollo
- [ ] Guía de estilo de código
- [ ] Proceso para abrir issues y PRs

### 4.2 CODE_OF_CONDUCT.md
- [ ] Adoptar Contributor Covenant u otro código de conducta estándar

### 4.3 CHANGELOG.md
- [ ] Inicializar con la versión `0.1.0`
- [ ] Definir formato (Keep a Changelog recomendado)

### 4.4 Issue y PR templates
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`

---

## Fase 5: CI/CD

### 5.1 GitHub Actions
- [ ] Workflow de lint (`ruff check`)
- [ ] Workflow de tests (`pytest`)
- [ ] Matrix de versiones de Python (3.9, 3.10, 3.11, 3.12)
- [ ] Ejecutar en macOS runner (ya que es macOS-only)

### 5.2 Release automation (futuro)
- [ ] Workflow para publicar en PyPI al crear un tag/release

---

## Fase 6: Publicación

### 6.1 Crear repositorio en GitHub
- [ ] Crear repo público (ej. `estebaner/portctl` o una org dedicada)
- [ ] Agregar descripción y topics (`cli`, `macos`, `ports`, `python`, `developer-tools`)
- [ ] Configurar rama principal (`main`)

### 6.2 Push inicial
- [ ] Agregar remote: `git remote add origin <url>`
- [ ] Push: `git push -u origin main`

### 6.3 Crear primer release
- [ ] Tag `v0.1.0`
- [ ] Release en GitHub con notas del changelog

### 6.4 Publicar en PyPI (opcional)
- [ ] Registrar cuenta en pypi.org
- [ ] `python -m build && twine upload dist/*`
- [ ] Verificar instalación: `pip install portctl`

---

## Fase 7: Difusión (opcional)

- [ ] Compartir en redes (Twitter/X, Reddit r/commandline, Hacker News)
- [ ] Registrar en awesome-lists relevantes
- [ ] Considerar soporte para Linux (expandir audiencia)

---

## Orden de ejecución sugerido

```
Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6 → Fase 7
```

Las fases 1 y 2 son bloqueantes. Las fases 3, 4 y 5 pueden trabajarse en paralelo. La fase 6 requiere que todo lo anterior esté listo.

---

## Decisiones pendientes

| Decisión | Opciones |
|----------|----------|
| Idioma del proyecto | Solo inglés / Bilingue / Solo español |
| Licencia | MIT / Apache 2.0 / GPL v3 |
| Reestructura de carpetas | Mantener single-file / src layout |
| Soporte multiplataforma | Solo macOS / Agregar Linux |
| Publicar en PyPI | Sí / No (solo GitHub) |
