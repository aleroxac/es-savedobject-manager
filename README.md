# es-savedobject-manager
Automação para coletar os savedobjects do Kibana e salvar no serviço de Object Store ou da AWS(s3) ou GCP(gcs).


## Modo de uso - Kubernetes
``` sh
gcloud secrets versions access latest --secret gcp-serviceaccount-token > /tmp/gcp-token.json
kubectl create namespace elk
kubectl apply -f <(kubectl create secret generic gcp-serviceaccount-token --from-env-file /tmp/gcp-token.json -o yaml --dry-run=client -n elk) -n elk
kubectl appy -f k8s/configmap.yml

## Horário em UTC --> Considere acrescentar 3 horas com base no horário em America/Sao_Paulo
NEW_SCHEDULE="15 20 * * *"; yq -r ".spec.schedule = \"${NEW_SCHEDULE}\"" k8s/cronjob.yml | kubectl apply -f-
```


## Modo de uso - Local
```
yq -r '.data."config.json"' k8s/configmap.yml >> config.json
for env_var in $(cat src/.env.example | sed "s/=//g"); do echo -ne "${env_var}="; read -r input; export "${input}" ;done
python3 app.py
```