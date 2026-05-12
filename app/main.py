import io
import re

import segno
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="qrforge",
    description="QR code generator — contacts, WiFi, email, SMS, phone, location, events, and more",
    version="2.1.0",
)

templates = Jinja2Templates(directory="app/templates")

_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3,5})?$|^[a-z]+$')


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/qr")
async def generate_qr(
    data: str = Query(..., description="Data to encode"),
    scale: int = Query(default=6, ge=1, le=50, description="Scale factor"),
    border: int = Query(default=4, ge=0, le=20, description="Border size"),
    ec: str = Query(default="M", description="Error correction level: L M Q H"),
    dark: str = Query(default="#000000", description="Module color (hex or name)"),
    light: str = Query(default="#ffffff", description="Background color (hex or name)"),
    fmt: str = Query(default="png", description="Output format: png or svg"),
):
    if not data:
        raise HTTPException(status_code=400, detail="'data' is required")

    ec_val = ec.upper()
    if ec_val not in ("L", "M", "Q", "H"):
        raise HTTPException(status_code=400, detail=f"Invalid error correction level '{ec}' — use L, M, Q, or H")

    if not _COLOR_RE.match(dark):
        raise HTTPException(status_code=400, detail=f"Invalid dark color: {dark}")
    if not _COLOR_RE.match(light):
        raise HTTPException(status_code=400, detail=f"Invalid light color: {light}")

    if fmt not in ("png", "svg"):
        raise HTTPException(status_code=400, detail=f"Invalid format '{fmt}' — use png or svg")

    try:
        qr = segno.make(data, micro=False, error=ec_val)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    buf = io.BytesIO()
    if fmt == "svg":
        qr.save(buf, kind="svg", scale=10, border=border, dark=dark, light=light)
        return Response(content=buf.getvalue(), media_type="image/svg+xml")
    else:
        qr.save(buf, kind="png", scale=scale, border=border, dark=dark, light=light)
        return Response(content=buf.getvalue(), media_type="image/png")
