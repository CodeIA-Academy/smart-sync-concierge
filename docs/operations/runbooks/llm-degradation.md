# Runbook: Degradación de LLM

## Versión
1.0.0

## Propósito

Guía para identificar, mitigar y recuperarse de problemas de degradación del servicio de LLM (Qwen, Claude, GPT-4).

---

## 🚨 Tipos de Degradación

### 1. Latencia Alta

**Síntomas**:
```
- agent_execution_duration_seconds p95 > 10s (normal: <3s)
- Timeouts en requests (>30s)
- Usuario espera mucho tiempo
```

**Métricas de Alerta**:
```yaml
alerts:
  - llm_request_duration_seconds p95 > 10s
  - llm_timeout_rate > 5%
  - agent_execution_duration_seconds p95 > 15s
```

### 2. Baja Calidad de Respuestas

**Síntomas**:
```
- confidence_avg < 0.7 (normal: >0.8)
- Aumento en ambiguities detectadas
- JSON inválido frecuente
- Extracción incorrecta de entidades
```

**Métricas de Alerta**:
```yaml
alerts:
  - parsing_confidence_avg < 0.7
  - parsing_json_error_rate > 10%
  - validation_false_positive_rate > 15%
```

### 3. Rate Limiting

**Síntomas**:
```
- 429 Too Many Requests
- llm_rate_limit_errors_total > 0
- Requests rechazados por proveedor
```

**Métricas de Alerta**:
```yaml
alerts:
  - llm_rate_limit_errors_total > 10 en 5min
  - llm_429_errors_rate > 1%
```

### 4. Servicio Down

**Síntomas**:
```
- Connection refused
- 500 Service Unavailable
- Todos los requests fallan
```

**Métricas de Alerta**:
```yaml
critical:
  - llm_connection_errors_total > 50 en 1min
  - llm_500_errors_rate > 50%
```

---

## 🔍 Diagnóstico

### Paso 1: Verificar Estado del Proveedor

```bash
# Qwen status
curl -I https://api.qwen.example.com/health

# Ver status page
# https://status.qwen.example.com

# Verificar nuestro dashboard
# http://localhost:9090 (Prometheus)
# Query: rate(llm_request_duration_seconds[5m])
```

### Paso 2: Medir Latencia Actual

```python
# core/ai/monitoring.py
import time
import asyncio

async def test_llm_latency():
    """Mide latencia real del LLM"""
    start = time.time()

    try:
        llm = LLMFactory.create(provider="qwen")
        response = await llm.complete(LLMRequest(
            prompt="Test prompt",
            max_tokens=10
        ))

        latency = time.time() - start
        print(f"✅ Latency: {latency:.2f}s")
        print(f"Tokens: {response.usage.total_tokens}")

        return latency

    except Exception as e:
        latency = time.time() - start
        print(f"❌ Error after {latency:.2f}s: {e}")
        return None

# Ejecutar 10 veces para promedio
latencies = []
for _ in range(10):
    lat = asyncio.run(test_llm_latency())
    if lat:
        latencies.append(lat)
    await asyncio.sleep(1)

print(f"Average: {sum(latencies)/len(latencies):.2f}s")
```

### Paso 3: Verificar Calidad de Respuestas

```python
# Test con prompts conocidos
test_cases = [
    ("cita mañana 10am con Dr. Pérez", {
        "expected_contacto": "Dr. Pérez",
        "expected_fecha": "mañana",
        "expected_hora": "10am"
    }),
    ("cita el próximo lunes a las 3pm", {
        "expected_contacto": None,
        "expected_fecha": "próximo lunes",
        "expected_hora": "3pm"
    })
]

for prompt, expected in test_cases:
    response = await parsing_agent.process(prompt)
    print(f"Prompt: {prompt}")
    print(f"Confidence: {response.confidence}")

    # Verificar que extrajo correctamente
    if response.entities.contacto == expected["expected_contacto"]:
        print("✅ Contacto correcto")
    else:
        print(f"❌ Contacto incorrecto: {response.entities.contacto}")
```

### Paso 4: Verificar Cuotas y Rate Limits

```bash
# Verificar límites actuales
curl https://api.qwen.example.com/v1/limits \
  -H "Authorization: Bearer $QWEN_API_KEY"

# Output esperado:
# {
#   "rate_limit": {
#     "requests_per_minute": 100,
#     "tokens_per_minute": 60000,
#     "requests_remaining": 95
#   },
#   "usage": {
#     "requests_today": 1234,
#     "tokens_today": 123456
#   }
# }
```

---

## 🛠️ Mitigación Inmediata

### Estrategia 1: Reducir Uso (Conservation Mode)

**Objetivo**: Reducir llamadas al LLM en 50%

```python
# config/settings/ai.py
CONSERVATION_MODE = True  # Activar manualmente

if CONSERVATION_MODE:
    # 1. Cachear más agresivamente
    LLM_CACHE_TTL = 3600  # 1 hora (normal: 300)

    # 2. Usar prompts más cortos
    PROMPT_TEMPLATE = "versión_corta"

    # 3. Recortar tokens
    MAX_TOKENS_DEFAULT = 100  # (normal: 500)

    # 4. Aumentar retries con backoff
    MAX_RETRIES = 5  # (normal: 3)
```

### Estrategia 2: Failover a Backup LLM

**Objetivo**: Cambiar a proveedor alternativo

```python
# core/ai/llm_factory.py
class LLMFactory:
    @staticmethod
    def create(provider: str = None) -> BaseLLM:
        if provider is None:
            # Auto-seleccionar basado en salud
            provider = LLMFactory.select_healthy_provider()

        if provider == "qwen":
            return QwenLLM()
        elif provider == "claude":
            return ClaudeLLM()
        elif provider == "openai":
            return OpenAILLM()

    @staticmethod
    def select_healthy_provider() -> str:
        """Selecciona proveedor más saludable"""
        health = LLMFactory.check_all_providers()

        # Ordenar por latencia y errores
        sorted_providers = sorted(
            health.items(),
            key=lambda x: (x[1]["error_rate"], x[1]["latency"])
        )

        return sorted_providers[0][0]

    @staticmethod
    def check_all_providers() -> dict:
        """Verifica salud de todos los proveedores"""
        results = {}

        for provider in ["qwen", "claude", "openai"]:
            try:
                llm = LLMFactory.create(provider=provider)
                start = time.time()
                llm.complete(LLMRequest(prompt="test", max_tokens=5))
                latency = time.time() - start

                results[provider] = {
                    "error_rate": 0,
                    "latency": latency,
                    "healthy": True
                }
            except Exception as e:
                results[provider] = {
                    "error_rate": 1.0,
                    "latency": float('inf'),
                    "healthy": False
                }

        return results
```

**Activación Manual**:

```bash
# Cambiar provider por environment variable
export LLM_PROVIDER=claude
python manage.py runserver

# O via admin
# http://localhost:8000/admin/config/ai/
# Cambiar: default_provider = "claude"
```

### Estrategia 3: Simplificar Pipeline

**Objetivo**: Saltar agentes no críticos

```python
# core/agents/coordinator_agent.py
class CoordinatorAgent:
    def get_agent_sequence(self, context: SharedContext) -> list:
        """Retorna secuencia de agentes basado en contexto"""

        # Modo degradación
        if self.is_degraded_mode():
            # Pipeline mínimo: parsing → temporal → validation
            return [
                ParsingAgent,
                TemporalAgent,
                ValidationAgent
                # Saltar: GeoAgent, AvailabilityAgent, NegotiationAgent
            ]

        # Pipeline normal
        return [
            ParsingAgent,
            TemporalAgent,
            GeoAgent,
            ValidationAgent,
            AvailabilityAgent,
            NegotiationAgent
        ]
```

### Estrategia 4: Timeout y Circuit Breaker

**Objetivo**: No esperar respuestas lentas

```python
# core/ai/providers/base_llm.py
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def complete_with_timeout(request: LLMRequest) -> LLMResponse:
    """Ejecuta con circuit breaker y timeout"""
    try:
        async with asyncio.timeout(10):  # 10s max
            return await self.client.chat.completions.create(...)
    except asyncio.TimeoutError:
        raise LLMTimeoutError("Request timeout after 10s")
```

### Estrategia 5: Fallback a No-LLM

**Objetivo**: Funcionar sin LLM para casos simples

```python
# apps/appointments/agents/parsing_agent.py
class ParsingAgent(BaseAgent):
    async def process(self, context: SharedContext):
        try:
            # Intentar con LLM
            return await self.parse_with_llm(context)
        except LLMError:
            # Fallback a regex
            logger.warning("LLM failed, using regex fallback")
            return await self.parse_with_regex(context)

    async def parse_with_regex(self, context: SharedContext):
        """Parse básico con regex (sin LLM)"""
        import re

        prompt = context.get("user_prompt")["prompt"]

        # Extraer contacto
        contacto_match = re.search(r'(?:con|dr\.?|dra\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', prompt)
        contacto = contacto_match.group(1) if contacto_match else None

        # Extraer hora
        hora_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', prompt)
        hora = hora_match.group(0) if hora_match else None

        # Extraer fecha relativa
        fecha = None
        if "mañana" in prompt.lower():
            fecha = "mañana"
        elif "hoy" in prompt.lower():
            fecha = "hoy"

        return ParsingOutput(
            entities=EntityExtraction(
                contacto=contacto,
                hora=hora,
                fecha=DateExpression(original=fecha, type="relative") if fecha else None
            ),
            confidence=0.6,  # Menor confianza
            ambiguities=[] if fecha and contacto else [
                Ambiguity(field="fecha", issue="missing", message="No se pudo extraer fecha")
            ]
        )
```

---

## 📊 Monitoreo Durante Degradación

### Dashboard Clave

```yaml
# Grafana dashboard
panels:
  - Latencia LLM p50, p95, p99
  - Error rate por proveedor
  - Requests por minuto
  - Confidence promedio
  - Timeout rate
  - Cache hit rate
```

### Alertas Adjustadas

```python
# Durante degradación, ajustar umbrales
if DEGRADATION_MODE:
    ALERT_THRESHOLDS = {
        "latency_p95": 20,  # (normal: 10)
        "error_rate": 0.10,  # (normal: 0.05)
        "timeout_rate": 0.10,  # (normal: 0.02)
    }
```

---

## 🔄 Recuperación

### Paso 1: Identificar Causa Raíz

```markdown
## Preguntas Clave

1. ¿Es problema del proveedor?
   - Ver status page
   - Verificar otros clientes

2. ¿Es problema nuestro?
   - Cambios recientes en código?
   - Cambios en prompts?
   - Aumento de tráfico?

3. ¿Es transitorio?
   - Picos de tráfico habituales?
   - Maintenancement programado?

4. ¿Es permanente?
   - Cambio de pricing?
   - Límites de cuenta?
```

### Paso 2: Implementar Fix Permanente

| Causa | Solución |
|-------|----------|
| Latencia alta del proveedor | Implementar multi-LLM con load balancing |
| Rate limiting | Caching más agresivo, queue system |
| Calidad baja | Reentrenar prompts, few-shot examples |
| Servidor down | Failover automático a backup |

### Paso 3: Verificar Recuperación

```python
# Test suite post-recuperación
async def test_llm_recovery():
    """Verifica que LLM volvió a normalidad"""

    # 1. Latencia normal
    latency = await measure_llm_latency()
    assert latency < 5, f"Latencia aún alta: {latency}s"

    # 2. Calidad normal
    confidence = await test_parsing_quality()
    assert confidence > 0.8, f"Confidence aún bajo: {confidence}"

    # 3. Sin rate limits
    limits = await check_rate_limits()
    assert limits["requests_remaining"] > 50, "Poco quota disponible"

    print("✅ LLM recuperado exitosamente")
```

---

## 📈 Prevención

### Arquitectura Multi-LLM

```python
# core/ai/multi_llm.py
class MultiLLMRouter:
    """Balancea carga entre múltiples proveedores"""

    def __init__(self):
        self.providers = [
            QwenLLM(weight=0.7),      # 70% de tráfico
            ClaudeLLM(weight=0.2),    # 20% de tráfico
            OpenAILLM(weight=0.1)     # 10% de tráfico
        ]

    async def route(self, request: LLMRequest):
        """Rutea request al mejor proveedor disponible"""

        # Filtrar proveedores saludables
        healthy = [p for p in self.providers if p.is_healthy()]

        if not healthy:
            # Emergency: todos enfermos, reintentar con todos
            healthy = self.providers

        # Seleccionar basado en peso
        provider = weighted_choice(healthy)

        try:
            return await provider.complete(request)
        except Exception:
            # Marcar como no saludable y reintentar
            provider.mark_unhealthy()
            return await self.route(request)
```

### Caching Inteligente

```python
# core/ai/cache.py
from functools import lru_cache
import hashlib

class LLMCache:
    """Caché basado en similitud de prompts"""

    async def get(self, prompt: str) -> Optional[LLMResponse]:
        # Hash del prompt
        key = hashlib.md5(prompt.encode()).hexdigest()

        # Buscar en Redis
        cached = await redis.get(f"llm_cache:{key}")
        if cached:
            return LLMResponse.from_json(cached)

        # Buscar prompts similares (fuzzy match)
        similar = await self.find_similar(prompt)
        if similar and similar["similarity"] > 0.9:
            return similar["response"]

        return None

    async def set(self, prompt: str, response: LLMResponse):
        key = hashlib.md5(prompt.encode()).hexdigest()
        await redis.setex(
            f"llm_cache:{key}",
            3600,  # 1 hora
            response.to_json()
        )
```

### Queue System

```python
# core/ai/queue.py
from asyncio import Queue

class LLMRequestQueue:
    """Cola de requests con rate limiting"""

    def __init__(self, max_requests_per_minute=100):
        self.queue = Queue()
        self.max_rpm = max_requests_per_minute
        self.request_count = 0
        self.reset_time = time.time() + 60

    async def submit(self, request: LLMRequest) -> LLMResponse:
        """Envía request respentando rate limit"""

        # Esperar si estamos en límite
        while self.request_count >= self.max_rpm:
            await asyncio.sleep(1)

            # Reset contador cada minuto
            if time.time() > self.reset_time:
                self.request_count = 0
                self.reset_time = time.time() + 60

        self.request_count += 1
        return await self.execute(request)
```

---

## 📞 Escalation

### Niveles de Severidad

| Severidad | Condición | Acción |
|-----------|-----------|--------|
| P1 - Critical | 100% downtime | Page on-call inmediato |
| P2 - High | >50% error rate | Page on-call + Tech Lead |
| P3 - Medium | >20% error rate | Slack #incidents |
| P4 - Low | Latencia alta, funcional | Crear ticket |

### Comunicación

```markdown
## Template de Anuncio

**Incidente: Degradación de LLM**

**Inicio**: 2026-01-22 10:30 UTC
**Severidad**: P2 - High
**Estado**: Investigando

**Impacto**:
- Latencia alta en creación de citas
- Algunos requests fallando

**Mitigación**:
- Cambiado a Claude como provider primario
- Modo conservación activado

**Próxima actualización**: 30 min
```

---

## ✅ Checklist de Recuperación

- [ ] Identificar tipo de degradación
- [ ] Medir impacto real
- [ ] Activar mitigación inmediata
- [ ] Verificar que mitigación funciona
- [ ] Investigar causa raíz
- [ ] Implementar fix permanente
- [ ] Verificar recuperación completa
- [ ] Documentar incidente
- [ ] Actualizar runbook si aplica
- [ ] Revisar alertas y umbrales

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: DevOps Team
