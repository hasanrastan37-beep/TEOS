# استقرار TEOS در Kubernetes

## پیش‌نیازها
- کلاستر Kubernetes (می‌تواند minikube، GKE، EKS و... باشد)
- Helm 3
- kubectl

## استقرار با Helm
1. افزودن مخزن (در صورت وجود):
   ```bash
   helm repo add teos https://charts.teos.io
   helm repo update
