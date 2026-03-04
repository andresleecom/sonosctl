# Sonos + Spotify CLI

CLI en Python para controlar bocinas Sonos y contenido de Spotify dentro de la misma red local.

Documentos relacionados:
- Contexto técnico de esta implementación: `docs/SONOS_CLI_CONTEXT.md`
- Runbook de despliegue/operación: `docs/DEPLOYMENT_RUNBOOK.md`

## 1) Qué resuelve

- Descubre bocinas Sonos en LAN
- Busca canciones en Spotify desde Sonos
- Reproduce en una o varias bocinas
- Controla transporte (`pause`, `resume`, `next`, `prev`)
- Controla volumen
- Lista playlists de Spotify
- Soporta salida JSON para automatización

## 2) Requisitos

- Python `3.10+`
- Sonos y computadora en la misma red (misma LAN/VLAN)
- Spotify agregado en Sonos app
- Acceso local a las bocinas (puerto Sonos en red interna)

## 3) Instalación

### Opción A: instalación local (equipo de desarrollo)

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### Opción B: instalación para usuarios (recomendada)

Con `pipx` (aislado y fácil de actualizar):

```bash
pipx install .
```

Si publicas a PyPI:

```bash
pipx install sonos-spotify-cli
```

## 4) Primer uso (onboarding)

1. Verifica bocinas:

```bash
sonosctl devices
```

2. Autoriza Spotify para este CLI (una sola vez por entorno/household):

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

3. Busca una canción:

```bash
sonosctl search "daft punk one more time" --speaker "Coffee Room"
```

4. Reproduce:

```bash
sonosctl play "daft punk one more time" --speaker "Coffee Room" --pick
```

## 5) Comandos principales

### Descubrimiento

```bash
sonosctl devices
sonosctl devices --json
```

### Búsqueda/reproducción

```bash
sonosctl search "nujabes feather" --speaker "Coffee Room"
sonosctl search "nujabes feather" --json --speaker "Coffee Room"
sonosctl play "nujabes feather" --speaker "Coffee Room"
sonosctl play "nujabes feather" --speaker "Coffee Room" --pick --limit 10
```

### Playlists

```bash
sonosctl playlists --speaker "Coffee Room"
sonosctl playlists chill --speaker "Coffee Room"
sonosctl playlists --speaker "Coffee Room" --json
```

### Controles de reproducción

```bash
sonosctl pause --speaker "Coffee Room"
sonosctl resume --speaker "Coffee Room"
sonosctl next --speaker "Coffee Room"
sonosctl prev --speaker "Coffee Room"
sonosctl volume --speaker "Coffee Room"
sonosctl volume 35 --speaker "Coffee Room"
```

### Multi-bocina (grupos)

Agrupar:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

Reproducir en grupo (desde coordinator):

```bash
sonosctl play "daft punk one more time" --speaker "Coffee Room" --pick
```

Separar:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 6) Configuración por defecto

Archivo por defecto: `~/.sonosctl/config.toml`

Ejemplo:

```toml
[defaults]
speaker = "Coffee Room"
timeout = 5
search_limit = 8
replace_queue = false
json = false
```

Con esto puedes ejecutar sin `--speaker` en la mayoría de comandos:

```bash
sonosctl play "nujabes feather" --pick
```

También puedes usar otro archivo:

```bash
sonosctl --config C:\ruta\config.toml devices
```

## 7) Troubleshooting

### Error `AuthTokenExpired`

1. Ejecuta de nuevo:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

2. Completa URL + código inmediatamente.
3. Reintenta `search`/`play` con `--speaker` explícito.

### "No Sonos speakers found"

- Verifica misma LAN/VLAN
- Desactiva VPN en la laptop
- Revisa aislamiento de clientes en AP/router
- Incrementa timeout:

```bash
sonosctl devices --timeout 15
```

### Código de link inválido en auth

- Genera uno nuevo con `auth-spotify`
- Úsalo de inmediato (expira rápido)
- Evita modo incógnito si bloquea sesión

## 8) Uso por múltiples personas

Recomendado en entorno compartido:

- 1 host "control" por red local
- Instalar con `pipx`
- Definir bocina default en config por usuario
- Compartir runbook (`docs/DEPLOYMENT_RUNBOOK.md`)
- Usar JSON para integraciones internas/scripting

## 9) Publicación para comunidad

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

Luego usuarios:

```bash
pipx install sonos-spotify-cli
```

## 10) Comando de ayuda

```bash
sonosctl --help
sonosctl play --help
sonosctl playlists --help
```

Guia diaria de operador: `docs/OPERATOR_GUIDE.md`
