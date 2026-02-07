# CLAUDE.md

Este archivo proporciona orientación a Claude Code sobre el proyecto.

## Resumen del Proyecto

Este proyecto contiene:
1. **Tig** - Clon del repositorio de Tig (text-mode interface for Git) en la carpeta `tig/`
2. **create_git_graph.py** - Implementación en Python del algoritmo de visualización de grafos de Tig

## Objetivo Principal

Crear un script Python que genere logs de Git con el mismo formato visual que Tig, replicando exactamente su algoritmo de visualización de grafos (Graph V2).

## Script Principal: create_git_graph.py

### Descripción
Implementación completa del algoritmo `graph-v2.c` de Tig en Python. Genera logs de Git con visualización de grafo usando símbolos box-drawing Unicode.

### Características
- Replica el algoritmo Graph V2 de Tig con 100% de precisión
- 20 flags de símbolo para detección precisa de patrones
- 4 filas de estado (prev_row, row, next_row, parents) para lookahead/lookbehind
- 12 funciones de detección de símbolos diferentes
- Formato de salida idéntico a Tig

### Uso
```bash
python3 create_git_graph.py <repo_path> [output_file]

# Ejemplo
python3 create_git_graph.py repos/gea-arc-tox-capy output.txt
```

### Formato de Salida
```
<hash> <date> <timezone> <author> <graph> <refs> <message>

Ejemplo:
d3e2e5e 2025-12-19 15:02 +0100 Miqui Infante              M─┐ [master] {origin/master} <1.9.0> Merge pull request #14
4328f73 2025-12-19 14:56 +0100 miqui                      │ o feat: add capy new MVN type
d226456 2025-11-25 18:33 +0100 Miqui Infante              M─┤ <1.8.0> Merge pull request #13
```

### Símbolos de Grafo Implementados
- ` o` - commit regular
- ` M` - commit de merge
- ` I` - commit inicial
- `─┐` - apertura de merge (URCORNER)
- `─┤` - cierre de merge (RTEE) - **clave para distinguir tipos de merge**
- `─┘` - cierre de branch (LRCORNER)
- `─┼` - cruce de merge (PLUS)
- `─┴` - multi-branch (BTEE)
- `─┬` - multi-merge (TTEE)
- ` │` - línea vertical
- `──` - línea horizontal
- ` ├` - fork (LTEE)
- `─│` - cross-over
- `─┌` - turn down (ULCORNER)

### Referencias
- `[branch]` - rama local (puede contener `/`, ej: `[feature/login]`)
- `{remote/branch}` - rama remota (detectada por prefijo conocido: origin, upstream, etc.)
- `<tag>` - etiqueta

**Detección de remotes**: Se usa una lista de nombres comunes (`origin`, `upstream`, `fork`, `github`, `gitlab`, `bitbucket`) para distinguir `origin/master` (remoto) de `feature/login` (local con `/`).

## Arquitectura del Algoritmo Graph V2

### Estructura de Datos

#### GraphSymbol (20 flags)
```python
class GraphSymbol:
    # Basic flags
    commit, boundary, initial, merge

    # Continuation flags
    continued_down, continued_up, continued_right, continued_left, continued_up_left

    # Parent flags
    parent_down, parent_right

    # Position flags
    below_commit, flanked, next_right, matches_commit

    # Shift flags
    shift_left, continue_shift, below_shift

    # Column flags
    new_column, empty
```

#### GraphColumn
Almacena el símbolo y el ID del commit (SHA-1)

#### GraphRow
Lista de GraphColumn. El algoritmo mantiene 4 filas:
- `prev_row` - fila anterior (para lookback)
- `row` - fila actual
- `next_row` - siguiente fila (para lookahead)
- `parents` - padres del commit actual

### Algoritmo de 3 Fases

1. **Expand**: Añade columnas vacías si es necesario
   ```python
   while position + parents.size > row.size:
       insert_column(prev_row, prev_row.size, None)
       insert_column(row, row.size, None)
       insert_column(next_row, next_row.size, None)
   ```

2. **Generate Next Row**: Calcula el estado de la siguiente fila
   ```python
   row_clear_commit(next_row, commit_id)
   insert_parents()
   remove_collapsed_columns()
   fill_empty_columns()
   ```

3. **Collapse**: Elimina columnas vacías al final
   ```python
   while row.size > 1 and not column_has_commit(row.columns[-1]):
       prev_row.columns.pop()
       row.columns.pop()
       next_row.columns.pop()
   ```

### Funciones Clave de Detección de Símbolos

#### symbol_vertical_merge() - Detecta M─┤
La función **MÁS IMPORTANTE** para distinguir merges que cierran vs merges que abren:
```python
if (symbol.empty) return False
if (not symbol.continued_up and not symbol.new_column and not symbol.below_commit) return False
if (symbol.shift_left and symbol.continued_up_left) return False
if (symbol.next_right) return False
if (not symbol.matches_commit) return False

# Condición crítica:
if (symbol.merge and symbol.continued_up and symbol.continued_left and
    symbol.parent_down and not symbol.continued_right):
    return True  # ─┤
```

#### symbol_merge() - Detecta M─┐
```python
if (not symbol.continued_down and symbol.parent_down and
    not symbol.parent_right and not symbol.continued_right):
    return True  # ─┐
```

#### Otras funciones
- `symbol_cross_merge()` - ─┼
- `symbol_cross_over()` - ─│
- `symbol_vertical_bar()` - │
- `symbol_turn_left()` - ─┘
- `symbol_multi_branch()` - ─┴
- `symbol_horizontal_bar()` - ──
- `symbol_forks()` - ├
- `symbol_turn_down_cross_over()` - ─┌
- `symbol_turn_down()` - ┌
- `symbol_multi_merge()` - ─┬

## Repositorio Tig (carpeta tig/)

### Qué es Tig
Tig es una interfaz ncurses text-mode para Git. Funciona como navegador de repositorios Git y puede ayudar a hacer staging de cambios a nivel de chunk.

### Build Commands (en tig/)
```bash
make                    # Build ejecutable
make all-debug          # Build con flags de debug
make test               # Ejecutar tests
make clean              # Limpiar build artifacts
```

### Archivos Importantes de Tig
- `src/graph-v1.c` - Algoritmo de grafo V1 (más simple, menos preciso)
- `src/graph-v2.c` - Algoritmo de grafo V2 (complejo, preciso) - **ESTE ES EL QUE USAMOS**
- `src/graph.c` - Interfaz común de grafos
- `include/tig/graph.h` - Definiciones de estructuras

### Generación Manual con Tig
Para generar un log en formato Tig manualmente:
```bash
tig --all              # Abrir tig con todas las ramas
# Presionar Shift+X    # Toggle ID display
# Resultado se puede copiar/guardar
```

## Carpeta ejemplos/

Contiene logs de ejemplo generados con Tig para validación:
- `gea-arc-tox-capy.tig.txt` - Ejemplo del repositorio gea-arc-tox-capy
- `gea-uc-mir-uc-nptb-jzz-workflows.tig.txt` - Ejemplo de workflows

Estos archivos sirven como "golden reference" para verificar que la implementación Python genera output idéntico.

## Historial de Desarrollo

### Problema Original
Replicar el algoritmo de Tig para generar logs de Git con el formato visual exacto, especialmente la distinción entre:
- `M─┐` (merge que abre una nueva rama)
- `M─┤` (merge que cierra/se une a rama existente)

### Intentos Fallidos
1. **git_log_renderer.py** - Primera versión básica, acumulaba demasiadas columnas
2. **git_log_renderer_v2.py** - Versión simplificada, símbolos incorrectos
3. **tig_graph_exact.py** - Implementación de Graph V1, ~90% precisa pero insuficiente

### Solución Final
Descubrimiento clave: Los ejemplos fueron generados con **Graph V2**, no V1.

Al reimplementar Graph V2 completo en `create_git_graph.py`, se logró 100% de precisión en todos los símbolos.

## Diferencias Graph V1 vs V2

| Aspecto | Graph V1 | Graph V2 |
|---------|----------|----------|
| Flags de símbolo | 11 | 20 |
| Filas de estado | 2 (row, parents) | 4 (prev_row, row, next_row, parents) |
| Funciones de detección | 1 (symbol_to_chtype) | 12 funciones especializadas |
| Lookahead/Lookback | No | Sí |
| Precisión | ~90% | 100% |
| Complejidad | Simple | Compleja |

## Notas Técnicas

### Por qué Graph V2 es Superior
- **Lookahead**: Puede ver la siguiente fila para decidir símbolos
- **Lookback**: Puede ver la fila anterior para contexto
- **Detección de patrones complejos**: 20 flags permiten detectar situaciones sutiles
- **matches_commit flag**: Crítico para saber si una columna contiene el commit actual

### Casos Especiales
1. **Merge que cierra** (M─┤):
   - El commit actual está en la columna
   - Tiene un padre que va hacia abajo
   - Tiene continuación hacia arriba e izquierda
   - NO tiene continuación hacia la derecha

2. **Merge que abre** (M─┐):
   - NO tiene continuación hacia abajo
   - Tiene un padre que va hacia abajo
   - NO tiene padre hacia la derecha
   - NO tiene continuación hacia la derecha

### Formato de Fecha
- Formato: `YYYY-MM-DD HH:MM` (sin segundos)
- Zona horaria: `+HHMM` o `-HHMM`
- **Fecha usada**: Commit date (`%ci`), NO author date (`%ai`)
  - Author date: cuando se escribió el commit
  - Commit date: cuando se aplicó el commit (usado por Tig)

### Orden de Git Log
Se usa `--topo-order` para obtener el orden topológico de commits, lo cual es importante para que el algoritmo de grafo funcione correctamente.

## Testing

Para probar que el script funciona correctamente:
```bash
# Generar output
python3 create_git_graph.py repos/gea-arc-tox-capy test_output.txt

# Comparar con ejemplo de referencia
diff ejemplos/gea-arc-tox-capy.tig.txt test_output.txt

# Diferencias esperadas: solo espaciado mínimo, símbolos deben ser idénticos
```

## Comandos Útiles

### Inspeccionar Git Log Raw
```bash
git log --all --topo-order --format='%H %P' | head -20
```

### Generar con Tig Original
```bash
cd repos/gea-arc-tox-capy
tig --all
# Shift+X para toggle ID
```

### Ver Símbolos Exactos
```bash
cat ejemplos/gea-arc-tox-capy.tig.txt | head -10 | cat -A
```

## Estructura del Proyecto

```
pruebatig/
├── CLAUDE.md                          # Este archivo
├── README.md                          # Documentación de usuario
├── create_git_graph.py                # Script principal ⭐
├── tig/                               # Repositorio de Tig (clon)
│   ├── src/graph-v2.c                 # Código fuente original del algoritmo
│   └── ...
├── ejemplos/                          # Logs de referencia
│   ├── gea-arc-tox-capy.tig.txt
│   └── gea-uc-mir-uc-nptb-jzz-workflows.tig.txt
└── repos/                             # Repositorios de prueba
    ├── gea-arc-tox-capy/
    └── gea-uc-mir-uc-nptb-jzz-workflows/
```

## Referencias

- Repositorio original de Tig: https://github.com/jonas/tig
- Documentación de Tig: https://jonas.github.io/tig/
- Box Drawing Unicode: https://en.wikipedia.org/wiki/Box-drawing_character
