from app.llm.base import LLMMessage, LLMResponse


class MockLLMProvider:
    """Deterministic provider for local development and tests."""

    provider_name = "mock"
    model_name = "mock-agronomy-advisor"

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        user_content = messages[-1].content if messages else ""
        context_hint = "No se recupero contexto documental suficiente."
        if "CONTEXTO DOCUMENTAL" in user_content:
            context_hint = "He usado el contexto documental recuperado y los datos operativos disponibles."

        answer = (
            f"{context_hint}\n\n"
            "Lectura operativa: revisa primero el estado hidrico de la parcela, la uniformidad del riego "
            "y la severidad de incidencias abiertas. Si hay baja humedad de suelo junto con sintomas en hoja, "
            "prioriza comprobar goteros, presion de linea, programacion de riego y evolucion reciente de sensores. "
            "Si los sintomas persisten tras corregir agua, escala a una inspeccion de nutricion, plagas o "
            "enfermedad.\n\n"
            "Limitacion: esta respuesta es una ayuda de decision y debe validarse con observacion de campo."
        )
        return LLMResponse(content=answer, model=self.model_name, provider=self.provider_name)
