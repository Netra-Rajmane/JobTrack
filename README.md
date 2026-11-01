# JobTrack – Job Application Tracker

A Flask + SQLite web application for tracking job applications. Includes a dashboard, status analytics, search, filtering, and create/read/update/delete operations.

## 1. Run locally on Windows

Open a terminal in this folder:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run this in the same terminal, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Open http://127.0.0.1:5000

For CMD, activate with:

```cmd
venv\Scripts\activate.bat
```

## 2. Docker

Build:

```bash
docker build -t jobtrack:1.0 .
```

Run:

```bash
docker run --name jobtrack -p 5000:5000 -v jobtrack-data:/app/instance jobtrack:1.0
```

Open http://127.0.0.1:5000

## 3. Kubernetes (Docker Desktop Kubernetes or Minikube)

Build the image in the same Docker environment used by your Kubernetes cluster:

```bash
docker build -t jobtrack:1.0 .
```

Apply the manifests:

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl get pods
kubectl get services
```

For a NodePort service, open http://localhost:30080 when using Docker Desktop Kubernetes. With Minikube, use:

```bash
minikube service jobtrack-service
```

Check logs:

```bash
kubectl logs deployment/jobtrack
```

## Notes

- SQLite data is stored in `instance/jobtracker.db`.
- The Docker run command uses a named volume so data survives container replacement.
- The Kubernetes Deployment uses a PersistentVolumeClaim for the SQLite database.
- This is a classroom demonstration project. Before production use, add authentication, CSRF protection, secure secret management, and a production WSGI server.
