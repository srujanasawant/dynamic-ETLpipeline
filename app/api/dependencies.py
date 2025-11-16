# app/api/dependencies.py
"""Shared dependencies for API routes"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db, get_mongo, get_redis


async def get_current_user():
    """Get current authenticated user (placeholder)"""
    # TODO: Implement authentication
    return {"user_id": "anonymous"}
