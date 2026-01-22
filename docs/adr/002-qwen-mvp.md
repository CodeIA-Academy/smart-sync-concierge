# ADR 002 - Qwen como LLM por Defecto en MVP

## Estado
✅ Aceptado

## Contexto

Smart-Sync Concierge requiere un modelo de lenguaje para:

- Extracción de entidades desde lenguaje natural
- Resolución de referencias temporales ("mañana", "la próxima semana")
- Validación de coherencia de solicitudes
- Generación de respuestas explicativas

### Requisitos del Modelo

- **Funcionamiento**: JSON mode o function calling para extracción estructurada
- **Rendimiento**: <2 segundos latencia promedio
- **Coste**: Económico para MVP con presupuesto limitado
- **Calidad**: Suficiente para extracción y razonamiento básico
- **Disponibilidad**: API estable con buen uptime

### Alternativas Evaluadas

| Modelo | Coste/1K tokens | Latencia avg | Razonamiento | JSON Mode |
|--------|-----------------|--------------|--------------|-----------|
| **Qwen 2.5** | $0.0001 | ~1s | Bueno | ✅ |
| Claude 3.5 Sonnet | $0.003 | ~1.5s | Excelente | ❌ (prompts) |
| GPT-4o | $0.005 | ~2s | Excelente | ✅ |
| GPT-4o-mini | $0.00015 | ~0.8s | Bueno | ✅ |
| Llama 3 (local) | $0 (infra) | ~0.5s | Bueno | ✅ |

## Decisión

**Usar Qwen 2.5 como LLM por defecto en MVP.**

### Justificación

1. **Coste-efectividad**: 30x más barato que Claude, 50x más barato que GPT-4
2. **Rendimiento suficiente**: Para extracción de entidades no necesita razonamiento avanzado
3. **JSON mode nativo**: Soporta respuestas estructuradas sin prompts complejos
4. **Código abierto**: Menor riesgo de vendor lock-in
5. **API estable**: Buen uptime y latencia consistente

### Abstracción

**Importante**: Implementar interfaz `BaseLLM` que permita swap sin modificar código de agentes.

```python
# Configuración
AI_DEFAULT_PROVIDER = "qwen"  # Fácil cambio a "claude" o "openai"
```

## Consecuencias

### Positivas

- ✅ **Coste bajo**: ~$10 por 100M tokens (suficiente para MVP)
- ✅ **Vendor lock-in reducido**: Código abierto, múltiples proveedores
- ✅ **JSON mode**: Respuestas estructuradas sin prompts complejos
- ✅ **Latencia aceptable**: ~1s promedio
- ✅ **Comunidad creciente**: Ecosistema en expansión

### Negativas

- ❌ **Razonamiento inferior**: Para tareas complejas, Claude/GPT-4 son mejores
- ❌ **Ecosistema smaller**: Menos herramientas/ejemplos que OpenAI
- ❌ **Soporte**: Comunidad más pequeña que OpenAI/Anthropic
- ❌ **Incógnita**: Comportamiento en edge cases menos documentado

### Riesgos

- **Calidad insuficiente**: Qwen puede no extrapolar bien en casos raros
- **Cambios de API**: Proyecto relativamente nuevo, breaking changes posibles
- **Escalabilidad**: Si el producto crece, coste de reentrenamiento si cambiamos

### Mitigaciones

- **Abstracción de LLM**: Interfaz `BaseLLM` permite swap en minutos
- **A/B testing framework**: Preparado para probar modelos alternativos
- **Prompt optimization**: Prompts robustos que funcionen en múltiples modelos
- **Fallback a Claude/GPT**: Para casos donde Qwen falla

## Alternativas Consideradas

### 1. Claude 3.5 Sonnet

**Descripción**: Usar Claude como modelo principal.

**Por qué NO para MVP**:
- ❌ Coste 30x mayor ($300 vs $10 por 100M tokens)
- ❌ Sin JSON mode nativo (requiere prompts complejos)
- ✅ Mejor razonamiento (no necesario para MVP)

**Nota**: Considerar para v0.3.0+ si se necesita mejor razonamiento.

### 2. GPT-4o

**Descripción**: Usar GPT-4o como modelo principal.

**Por qué NO para MVP**:
- ❌ Coste 50x mayor ($500 vs $10 por 100M tokens)
- ❌ Latencia mayor (~2s vs ~1s)
- ✅ Excelente razonamiento (no necesario para MVP)

**Nota**: Considerar para tareas complejas en futuros.

### 3. GPT-4o-mini

**Descripción**: Usar GPT-4o-mini como modelo principal.

**Por qué NO**:
- ❌ Aún 1.5x más caro que Qwen
- ✅ Latencia ligeramente mejor
- ✅ Mejor ecosistema

**Decisión cercana**: Si OpenAI ofrece créditos, reconsiderar.

### 4. Llama 3 Local

**Descripción**: Desplegar Llama 3 en infraestructura propia.

**Por qué NO**:
- ❌ Overhead operacional (GPU, mantenimiento)
- ❌ Coste de infraestructura significativo
- ❌ Complejidad de monitoreo y escalado

**Nota**: Considerar para v0.5.0+ si volumen justifica infra.

## Comparativa de Costes

### Escenario: 100K requests/mes

| Modelo | Tokens/request | Coste mensual |
|--------|----------------|---------------|
| **Qwen 2.5** | 500 | **$5** |
| GPT-4o-mini | 500 | $7.50 |
| Claude 3.5 Sonnet | 500 | $150 |
| GPT-4o | 500 | $250 |

### Escenario: 1M requests/mes (escalado)

| Modelo | Coste mensual |
|--------|---------------|
| **Qwen 2.5** | **$50** |
| GPT-4o-mini | $75 |
| Claude 3.5 Sonnet | $1,500 |
| GPT-4o | $2,500 |

**Conclusión**: Qwen permite escalar 10-30x con mismo presupuesto.

## Estrategia de Migración

### Roadmap de Modelos

```
v0.1.0 (MVP)
└── Qwen 2.5 (principal)
    └── Claude fallback para edge cases

v0.3.0
├── Qwen 2.5 (tareas simples)
└── Claude 3.5 Sonnet (tareas complejas)
    └── Router inteligente por complejidad

v0.5.0
├── Qwen 2.5 (extracción básica)
├── Claude 3.5 Sonnet (razonamiento)
└── GPT-4o (planificación compleja)

v1.0.0
└── Multi-modelo con optimización de costes
```

### Indicadores para Cambiar de Modelo

Monitorear métricas mes a mes:

- **Precisión de extracción**: <95% → considerar mejor modelo
- **Tasa de fallback a Claude**: >15% → hacer Claude principal
- **Coste mensual**: >$100 → evaluar balance coste/precisión
- **Latencia p95**: >3s → optimizar o cambiar modelo

## Implementación

### Estado
- ✅ Propuesto: 2026-01-22
- ✅ Aceptado: 2026-01-22
- ⏳ En Progreso: [PR-50](https://github.com/...)

### Componentes

| Componente | Estado |
|------------|--------|
| BaseLLM interface | ✅ Completado |
| QwenLLM implementation | ✅ Completado |
| ClaudeLLM (fallback) | ⏳ En Progreso |
| LLMFactory | ⏳ En Progreso |
| LLMRouter (futuro) | ⏸ Pendiente |

### Configuración

```python
# config/settings/ai.py
AI_PROVIDERS = {
    "qwen": {
        "class": "QwenLLM",
        "default_model": "qwen-2.5",
        "api_key": env("QWEN_API_KEY"),
        "cost_per_1k_tokens": 0.0001,
    },
    "claude": {
        "class": "ClaudeLLM",
        "default_model": "claude-3-5-sonnet-20241022",
        "api_key": env("ANTHROPIC_API_KEY"),
        "cost_per_1k_tokens": 0.003,
    },
}

AI_DEFAULT_PROVIDER = "qwen"  # Cambiar acá para swap
AI_FALLBACK_PROVIDER = "claude"  # Si Qwen falla
```

### Referencias

- [Abstracción de IA](../architecture/ai-abstraction.md)
- [Contratos de LLM](../contracts/llm-contract.md)
- [Qwen Documentation](https://qwen.readthedocs.io/)

## Supersedes

Supersede: Ninguno

## Superseded By

Ninguno (activo)

---

**Autor**: Architecture Team
**Fecha**: Enero 22, 2026
**Revisado por**: Tech Lead, Finance (coste approval)
