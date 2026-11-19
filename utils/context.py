# utils/context.py
import discord
from discord.ext import commands

class EmbedContext(commands.Context):
    async def send(self, content=None, **kwargs):
        # إلا كان المستخدم باغي يصيفط Embed بيدو، ولا ملف (File)، خليه يفوت عادي
        if kwargs.get("embed") is not None or kwargs.get("files"):
            return await super().send(content=content, **kwargs)

        # إلا كان النص عبارة عن string عادي
        if isinstance(content, str):
            # نظام الألوان الذكي: كيقلب على الإيموجي فـ النص ويلون الـ Embed
            color = discord.Color.from_rgb(88, 101, 242) # اللون الأزرق الافتراضي
            if any(e in content for e in ["❌", "🚫", "⛔", "💥", "😢"]):
                color = discord.Color.red() # أحمر للأخطاء
            elif any(e in content for e in ["✅", "🎉", "🟢", "👍", "✨"]):
                color = discord.Color.green() # أخضر للنجاح
            elif any(e in content for e in ["⚠️", "⏰", "🔒", "🤔"]):
                color = discord.Color.orange() # برتقالي للتحذيرات

            # كنصايبو الـ Embed ونحطو فيه النص
            embed = discord.Embed(description=content, color=color)
            
            # كنخويو النص العادي باش مايتصيفطش مرتين
            content = None
            kwargs["embed"] = embed

        # كنصيفطو الرسالة (اللي ولات Embed)
        return await super().send(content=content, **kwargs)