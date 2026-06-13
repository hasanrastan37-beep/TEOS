from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.analytics.service import analytics_service
from src.modules.analytics.funnels import FunnelAnalyzer
from src.modules.analytics.pdf_reports import pdf_generator
from typing import Optional
from datetime import date, timedelta

router = APIRouter(prefix="/owner/reports", tags=["Owner Reports"])

@router.get("/daily_active_users")
async def daily_active_users(days: int = 30):
    async with async_session() as db:
        data = await analytics_service.get_daily_active_users(db, days)
        return data

@router.get("/purchase_funnel")
async def purchase_funnel():
    async with async_session() as db:
        analyzer = FunnelAnalyzer()
        funnel = await analyzer.purchase_funnel(db)
        return funnel

@router.get("/sales_pdf")
async def sales_report_pdf(from_date: Optional[str] = None, to_date: Optional[str] = None):
    # تولید PDF ساده
    data = {"total_sales": 1250000, "transactions": 42}
    pdf_bytes = pdf_generator.generate_sales_report(data)
    from fastapi.responses import Response
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})
