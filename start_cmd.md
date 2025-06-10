For deployment server, here are the recommended start commands depending on your deployment environment:

## 🚀 **Production Start Commands:**

### **1. Basic Production Command:**
```bash
uvicorn app:app --host 0.0.0.0 --port 5055 --log-level info
```

### **2. Recommended Production Command (with workers):**
```bash
uvicorn app:app --host 0.0.0.0 --port 5055 --workers 4 --log-level info
```

### **3. High-Performance Production Command:**
```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5055 --log-level info --access-logfile - --error-logfile -
```

## 🐳 **For Different Deployment Platforms:**

### **Docker:**
```dockerfile
# In your Dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5055", "--workers", "4"]
```

### **Railway/Render/Heroku:**
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT --log-level info
```

### **AWS/GCP/Azure:**
```bash
uvicorn app:app --host 0.0.0.0 --port 5055 --workers 4 --log-level info --access-log
```

## ⚙️ **Environment-Specific Considerations:**

### **If you need to specify the port dynamically:**
```bash
uvicorn app:app --host 0.0.0.0 --port ${PORT:-5055} --log-level info
```

### **For PM2 (Process Manager):**
```json
{
  "name": "influencer-api",
  "script": "uvicorn",
  "args": "app:app --host 0.0.0.0 --port 5055 --log-level info",
  "instances": 4,
  "exec_mode": "cluster"
}
```

## 🔧 **Important Notes:**

1. **Remove `--reload`** - Only use in development, never in production
2. **Set workers** - Use 2-4 workers for better performance
3. **Use environment variables** - For sensitive configs like API keys
4. **Log level** - Use `info` or `warning` in production
5. **Health checks** - Ensure your deployment platform can hit `/health`

## 🎯 **Recommended Production Command:**
```bash
uvicorn app:app --host 0.0.0.0 --port 5055 --workers 4 --log-level info --access-log
```

This command will:
- ✅ Bind to all interfaces (`0.0.0.0`)
- ✅ Use port 5055 (or whatever your deployment needs)
- ✅ Run 4 worker processes for better performance
- ✅ Show info-level logs
- ✅ Log HTTP access requests
- ✅ Work in production environment

The exact command might vary slightly depending on your deployment platform's requirements, but this should work for most scenarios! 🚀