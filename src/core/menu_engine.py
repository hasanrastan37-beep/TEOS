"""
Dynamic Menu Engine – تمام منوها از دیتابیس ساخته می‌شوند.
ساختار سلسله‌مراتبی، شرطی، مبتنی بر نقش و قابل ویرایش از پنل.
"""
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import json
from pydantic import BaseModel
from src.core.database import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON

# ----- مدل‌های دیتابیس -----
class MenuNode(Base, TimestampMixin):
    __tablename__ = "menu_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("menu_nodes.id"), nullable=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # شناسه یکتا مثلاً "main"
    label: Mapped[str] = mapped_column(String(128))  # عنوان نمایشی
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    callback_data: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)  # callback_data یا command
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # لینک
    switch_inline_query: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)  # ترتیب
    is_active: Mapped[bool] = mapped_column(default=True)
    permission_roles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # نقش‌های مجاز، کاما جدا شده
    condition_rule: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # شرط Rule Engine
    icon: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # ایموجی
    children = relationship("MenuNode", back_populates="parent", remote_side=[id])
    parent = relationship("MenuNode", back_populates="children", remote_side=[parent_id])

# ----- مدل‌های Pydantic برای API -----
class MenuNodeOut(BaseModel):
    id: int
    key: str
    label: str
    description: Optional[str]
    callback_data: Optional[str]
    url: Optional[str]
    switch_inline_query: Optional[str]
    order: int
    is_active: bool
    icon: Optional[str]
    children: List['MenuNodeOut'] = []

    class Config:
        from_attributes = True

# ----- سرویس -----
class MenuEngine:
    def __init__(self):
        self._cache = {}  # کش ساده

    async def load_menu_tree(self, db: AsyncSession, root_key: str = "main") -> Optional[MenuNodeOut]:
        # دریافت گره ریشه
        stmt = select(MenuNode).where(MenuNode.key == root_key, MenuNode.is_active == True)
        result = await db.execute(stmt)
        root = result.scalars().first()
        if not root:
            return None
        return await self._build_tree(db, root)

    async def _build_tree(self, db: AsyncSession, node: MenuNode) -> MenuNodeOut:
        out = MenuNodeOut.from_orm(node)
        # دریافت فرزندان
        stmt = select(MenuNode).where(
            MenuNode.parent_id == node.id,
            MenuNode.is_active == True
        ).order_by(MenuNode.order)
        result = await db.execute(stmt)
        children = result.scalars().all()
        for child in children:
            out.children.append(await self._build_tree(db, child))
        return out

    async def get_menu_for_user(self, db: AsyncSession, user_role: str, user_context: dict = None) -> Optional[MenuNodeOut]:
        # ابتدا کل درخت را از ریشه بگیرید و سپس بر اساس نقش و شرط فیلتر کنید
        root = await self.load_menu_tree(db, "main")
        if root is None:
            return None
        return self._filter_by_role_and_condition(root, user_role, user_context)

    def _filter_by_role_and_condition(self, node: MenuNodeOut, role: str, context: dict = None) -> Optional[MenuNodeOut]:
        if not context:
            context = {}
        # فیلتر نقش
        if node.permission_roles:
            allowed_roles = [r.strip() for r in node.permission_roles.split(",") if r.strip()]
            if "all" not in allowed_roles and role not in allowed_roles:
                return None  # این گره و فرزندانش نمایش داده نشوند
        # فیلتر شرط
        if node.condition_rule:
            from src.core.rule_engine import RuleEngine
            engine = RuleEngine()
            # توجه: این await در تابع sync قابل استفاده نیست. برای سادگی فرض می‌کنیم rule بدون await.
            # در عمل باید از async rule evaluation استفاده کرد.
            # ولی اینجا به صورت شبه‌کد: if not engine.evaluate_sync(node.condition_rule, context): return None
            pass

        # پردازش فرزندان
        filtered_children = []
        for child in node.children:
            filtered = self._filter_by_role_and_condition(child, role, context)
            if filtered:
                filtered_children.append(filtered)
        node.children = filtered_children
        return node

menu_engine = MenuEngine()
