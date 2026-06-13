import os
import uuid
import subprocess
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.modules.service_vpn.server_models import VPNServer, WireGuardConfig
from src.modules.service_vpn.models import Order
import logging

logger = logging.getLogger(__name__)

class WireGuardService:
    async def generate_config(self, db: AsyncSession, order: Order, server_id: int = None):
        # انتخاب سرور با کمترین استفاده
        if not server_id:
            stmt = select(VPNServer).where(VPNServer.is_active == True).order_by(VPNServer.used_slots / VPNServer.total_slots)
            result = await db.execute(stmt)
            servers = result.scalars().all()
            if not servers:
                raise Exception("No available VPN server")
            # انتخاب اولین سرور با ظرفیت
            server = None
            for s in servers:
                if s.used_slots < s.total_slots:
                    server = s
                    break
            if not server:
                raise Exception("All servers full")
        else:
            server = await db.get(VPNServer, server_id)
            if not server or not server.is_active or server.used_slots >= server.total_slots:
                raise Exception("Server unavailable")

        # تولید کلیدها (شبیه‌سازی)
        private_key = f"wg_private_{uuid.uuid4().hex[:12]}"
        public_key = f"wg_public_{uuid.uuid4().hex[:12]}"
        assigned_ip = f"10.10.{server.id}.{server.used_slots + 2}"
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {assigned_ip}/32
DNS = 8.8.8.8

[Peer]
PublicKey = {server.public_key if hasattr(server, 'public_key') else 'SERVER_PUBLIC_KEY'}
Endpoint = {server.ip_address}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25"""
        expires = datetime.utcnow() + timedelta(days=order.plan.duration_days * order.quantity)

        config_record = WireGuardConfig(
            order_id=order.id,
            server_id=server.id,
            private_key=private_key,
            public_key=public_key,
            assigned_ip=assigned_ip,
            config_text=config,
            expires_at=expires
        )
        db.add(config_record)
        server.used_slots += 1
        order.delivery_info = config
        order.status = "delivered"
        await db.commit()
        return config_record

    async def revoke_config(self, db: AsyncSession, config_id: int):
        config = await db.get(WireGuardConfig, config_id)
        if config and config.is_active:
            config.is_active = False
            server = await db.get(VPNServer, config.server_id)
            if server and server.used_slots > 0:
                server.used_slots -= 1
            await db.commit()
            logger.info(f"Revoked config {config_id}")

wireguard_service = WireGuardService()
