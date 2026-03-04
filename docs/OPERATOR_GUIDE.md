# Sonos CLI - Guia de Operador (Turno Diario)

Last updated: 2026-03-04

## Objetivo
Operar musica en bocinas Sonos durante todo el dia con comandos simples y un procedimiento consistente.

## 1) Checklist de inicio de turno (2-3 minutos)

1. Verifica que la laptop/PC este en la misma red local que Sonos.
2. Asegura que NO haya VPN activa.
3. Abre terminal.
4. Verifica bocinas:

```bash
sonosctl devices
```

5. Prueba rapida de busqueda:

```bash
sonosctl search "test" --speaker "Coffee Room"
```

Si ambos comandos responden, el sistema esta listo.

## 2) Comandos base del turno

Reproducir cancion (con seleccion):

```bash
sonosctl play "nombre de cancion" --speaker "Coffee Room" --pick
```

Buscar sin reproducir:

```bash
sonosctl search "nombre de cancion" --speaker "Coffee Room"
```

Controles:

```bash
sonosctl pause --speaker "Coffee Room"
sonosctl resume --speaker "Coffee Room"
sonosctl next --speaker "Coffee Room"
sonosctl prev --speaker "Coffee Room"
sonosctl volume 35 --speaker "Coffee Room"
```

Ver playlists:

```bash
sonosctl playlists --speaker "Coffee Room"
sonosctl playlists chill --speaker "Coffee Room"
```

## 3) Operacion multi-bocina

Agrupar `Dining Room` en `Coffee Room`:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

Luego reproducir en coordinator (suena en ambas):

```bash
sonosctl play "nombre de cancion" --speaker "Coffee Room" --pick
```

Separar bocina:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 4) Checklist de cierre de turno

1. Deja volumen en nivel acordado (ej. 25-35):

```bash
sonosctl volume 30 --speaker "Coffee Room"
```

2. Pausa o deja playlist de cierre segun operacion:

```bash
sonosctl pause --speaker "Coffee Room"
```

3. Si hubo multi-bocina temporal, desagrupar:

```bash
sonosctl ungroup --speaker "Dining Room"
```

## 5) Incidentes comunes y solucion rapida

### A) Error `AuthTokenExpired`

Reautoriza:

```bash
sonosctl auth-spotify --speaker "Coffee Room"
```

Luego prueba:

```bash
sonosctl search "test" --speaker "Coffee Room"
```

### B) No aparecen bocinas

1. Confirmar misma LAN.
2. Confirmar VPN apagada.
3. Reintentar con timeout alto:

```bash
sonosctl devices --timeout 15
```

### C) No suena en ambas bocinas

Recrear grupo:

```bash
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
```

## 6) Reglas operativas

1. Un solo operador activo por turno.
2. Siempre usar nombres exactos de bocina como salen en `sonosctl devices`.
3. Para multiroom, usar `Coffee Room` como coordinator estandar.
4. Si algo falla, capturar comando + error completo y escalar.

## 7) Comandos de referencia rapida

```bash
sonosctl devices
sonosctl play "daft punk one more time" --speaker "Coffee Room" --pick
sonosctl group --coordinator "Coffee Room" --members "Dining Room"
sonosctl ungroup --speaker "Dining Room"
sonosctl auth-spotify --speaker "Coffee Room"
```
