from app.schemas.ask import AskResponse
from app.services.operations_service import OperationsService
from app.services.rag_service import RagService


class DiagnosisService:
    def __init__(self, operations_service: OperationsService, rag_service: RagService) -> None:
        self._operations_service = operations_service
        self._rag_service = rag_service

    def diagnose(self, plot_id: str, question: str, top_k: int, include_context: bool) -> AskResponse:
        status = self._operations_service.get_plot_status(plot_id)
        operational_context = self._operations_service.format_operational_context(plot_id)

        search_parts = [question, status.plot.crop, status.plot.soil_type, status.plot.irrigation_system]
        search_parts.extend(alert.type for alert in status.alerts)
        search_parts.extend(incident.type for incident in status.incidents)
        search_query = " ".join(search_parts)

        response = self._rag_service.answer(
            question=question,
            top_k=top_k,
            include_context=include_context,
            operational_context=operational_context,
            search_query=search_query,
        )
        response.metadata["plot_id"] = plot_id
        return response

