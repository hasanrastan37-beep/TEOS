from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
import os
import uuid
import importlib.util
from src.core.plugins import plugin_manager
import shutil

router = APIRouter(prefix="/plugins", tags=["Plugins"])

PLUGIN_UPLOAD_DIR = "./plugins_uploaded"

@router.post("/upload")
async def upload_plugin(file: UploadFile = File(...)):
    if not file.filename.endswith(".py"):
        raise HTTPException(400, "Only .py files allowed")
    os.makedirs(PLUGIN_UPLOAD_DIR, exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(PLUGIN_UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    # سعی در بارگذاری و اعتبارسنجی
    try:
        spec = importlib.util.spec_from_file_location("uploaded_plugin", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # جستجوی کلاس پلاگین
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "name") and attr.__name__ != "PluginInterface":
                plugin_class = attr
                break
        if not plugin_class:
            os.remove(file_path)
            raise HTTPException(400, "No valid plugin class found")
        # انتقال به پوشه plugins اصلی
        dest_path = os.path.join("./plugins", file.filename)
        shutil.copy(file_path, dest_path)
        plugin_manager.discover()  # کشف مجدد
        await plugin_manager.enable_plugin(plugin_class.name)
        return {"message": "Plugin uploaded and enabled", "plugin_name": plugin_class.name}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Plugin invalid: {str(e)}")
