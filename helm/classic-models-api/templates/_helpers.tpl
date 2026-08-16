{{/*
Expand the name of the chart.
*/}}
{{- define "classic-models-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "classic-models-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "classic-models-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "classic-models-api.labels" -}}
helm.sh/chart: {{ include "classic-models-api.chart" . }}
{{ include "classic-models-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "classic-models-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "classic-models-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "classic-models-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "classic-models-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host (externalDB.host — required).
*/}}
{{- define "classic-models-api.mysql.servicename" -}}
{{- required "externalDB.host is required" .Values.externalDB.host }}
{{- end }}

{{/*
Database port (externalDB.port, default 3306).
*/}}
{{- define "classic-models-api.mysql.port" -}}
{{- default 3306 .Values.externalDB.port }}
{{- end }}

{{/*
Database name (externalDB.database, default "classicmodels").
*/}}
{{- define "classic-models-api.mysql.database" -}}
{{- default "classicmodels" .Values.externalDB.database }}
{{- end }}

{{/*
Database username (externalDB.username, default "classicuser").
*/}}
{{- define "classic-models-api.mysql.username" -}}
{{- default "classicuser" .Values.externalDB.username }}
{{- end }}

{{/*
Image name
*/}}
{{- define "classic-models-api.image" -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" .Values.image.repository $tag }}
{{- end }}

{{/*
Secret name that holds the Django SECRET_KEY.
Returns the external secret name when configured, otherwise the chart-managed secret.
*/}}
{{- define "classic-models-api.secretKeySecretName" -}}
{{- if .Values.externalSecrets.djangoSecretKey.name -}}
{{- .Values.externalSecrets.djangoSecretKey.name -}}
{{- else -}}
{{- include "classic-models-api.fullname" . -}}
{{- end -}}
{{- end }}

{{/*
Key inside the secret that holds the Django SECRET_KEY.
*/}}
{{- define "classic-models-api.secretKeySecretKey" -}}
{{- if .Values.externalSecrets.djangoSecretKey.key -}}
{{- .Values.externalSecrets.djangoSecretKey.key -}}
{{- else -}}
django-secret-key
{{- end -}}
{{- end }}

{{/*
Secret name that holds the API_KEY.
Returns the external secret name when configured, otherwise the chart-managed secret.
*/}}
{{- define "classic-models-api.apiKeySecretName" -}}
{{- if .Values.externalSecrets.apiKey.name -}}
{{- .Values.externalSecrets.apiKey.name -}}
{{- else -}}
{{- include "classic-models-api.fullname" . -}}
{{- end -}}
{{- end }}

{{/*
Key inside the secret that holds the API_KEY.
*/}}
{{- define "classic-models-api.apiKeySecretKey" -}}
{{- if .Values.externalSecrets.apiKey.key -}}
{{- .Values.externalSecrets.apiKey.key -}}
{{- else -}}
api-key
{{- end -}}
{{- end }}

{{/*
Secret name that holds the MySQL password.
Returns the external secret name when configured, otherwise the chart-managed secret.
*/}}
{{- define "classic-models-api.mysqlPasswordSecretName" -}}
{{- if .Values.externalSecrets.mysqlPassword.name -}}
{{- .Values.externalSecrets.mysqlPassword.name -}}
{{- else -}}
{{- include "classic-models-api.fullname" . -}}
{{- end -}}
{{- end }}

{{/*
Key inside the secret that holds the MySQL password.
*/}}
{{- define "classic-models-api.mysqlPasswordSecretKey" -}}
{{- if .Values.externalSecrets.mysqlPassword.key -}}
{{- .Values.externalSecrets.mysqlPassword.key -}}
{{- else -}}
mysql-password
{{- end -}}
{{- end }}