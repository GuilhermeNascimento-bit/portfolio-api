from fastapi import APIRouter, HTTPException

from app.services.github import fetch_github_data

router = APIRouter()


@router.get("/github")
async def get_github():
    try:
        return await fetch_github_data()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")
