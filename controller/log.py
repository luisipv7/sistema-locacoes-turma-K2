from schemas.log_schema import LogFilter
from services.log import get_logs_service


async def get_logs(filters: LogFilter):
    return await get_logs_service(filters)
