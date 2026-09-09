import uvicorn

if __name__ == "__main__":
    print("Starting SahakarConnect Ghaziabad Server on http://0.0.0.0:8000 ...")
    print("Local access: http://localhost:8000")
    print("LAN / Wi-Fi access: http://<your-local-ip>:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
