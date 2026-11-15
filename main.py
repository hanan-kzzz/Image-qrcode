import os, json, secrets
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2, numpy as np
from supabase import create_client

app = FastAPI(title="ScanLink API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST","DELETE"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
def db():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(503, "Database is not configured yet.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
def admin(token):
    if not ADMIN_TOKEN or not secrets.compare_digest(token or "", ADMIN_TOKEN):
        raise HTTPException(401, "Admin authentication required.")
def descriptors(data):
    arr=np.frombuffer(data,np.uint8); img=cv2.imdecode(arr,cv2.IMREAD_GRAYSCALE)
    if img is None: raise HTTPException(400,"Invalid image.")
    if max(img.shape)>1600:
        scale=1600/max(img.shape); img=cv2.resize(img,None,fx=scale,fy=scale)
    orb=cv2.ORB_create(nfeatures=1200)
    kp, des=orb.detectAndCompute(img,None)
    if des is None or len(kp)<20: raise HTTPException(400,"This image has too few distinctive visual features. Try a clearer image.")
    return {"keypoints":[[float(k.pt[0]),float(k.pt[1]),float(k.size),float(k.angle),float(k.response),int(k.octave),int(k.class_id)] for k in kp],"descriptors":des.tolist()}
@app.get("/api/health")
def health():
    return {"ok":True,"database_configured":bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)}
@app.post("/api/register")
async def register(image: UploadFile=File(...), url: str=Form(...), title: str=Form(""), x_admin_token: str=Header(default="")):
    admin(x_admin_token)
    if not url.startswith(("https://","http://")): raise HTTPException(400,"URL must begin with http:// or https://")
    data=await image.read()
    if len(data)>8*1024*1024: raise HTTPException(413,"Maximum image size is 8 MB.")
    feat=descriptors(data)
    row={"title":title[:100],"target_url":url,"features":feat,"active":True}
    result=db().table("scanlink_images").insert(row).execute()
    item=result.data[0]
    return {"id":item["id"],"title":item["title"],"target_url":item["target_url"]}
@app.get("/api/images")
def images(x_admin_token: str=Header(default="")):
    admin(x_admin_token)
    rows=db().table("scanlink_images").select("id,title,target_url,active,created_at").order("created_at",desc=True).execute()
    return rows.data
@app.delete("/api/images/{image_id}")
def delete_image(image_id: str, x_admin_token: str=Header(default="")):
    admin(x_admin_token)
    db().table("scanlink_images").delete().eq("id",image_id).execute()
    return {"ok":True}
@app.post("/api/recognize")
async def recognize(image: UploadFile=File(...)):
    data=await image.read()
    if len(data)>8*1024*1024: raise HTTPException(413,"Image too large.")
    query=descriptors(data)
    qdes=np.asarray(query["descriptors"],dtype=np.uint8)
    rows=db().table("scanlink_images").select("id,title,target_url,features").eq("active",True).execute().data
    orb=cv2.ORB_create(nfeatures=1200); matcher=cv2.BFMatcher(cv2.NORM_HAMMING)
    best=None; best_score=0
    for row in rows:
        feat=row["features"]; train=np.asarray(feat["descriptors"],dtype=np.uint8)
        if len(train)<2: continue
        pairs=matcher.knnMatch(qdes,train,k=2)
        good=[m for pair in pairs if len(pair)==2 for m,n in [pair] if m.distance<0.72*n.distance]
        score=len(good)
        if score>best_score: best_score=score; best=row
    if best and best_score>=18:
        return {"matched":True,"id":best["id"],"title":best["title"],"url":best["target_url"],"confidence":"likely","matches":best_score}
    return {"matched":False,"message":"No registered image matched. Try moving closer, improving light, or using the original image."}
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html",encoding="utf-8") as f: return f.read()
