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
MySQL fullname
*/}}
{{- define "classic-models-api.mysql.fullname" -}}
{{- if .Values.mysql.fullnameOverride }}
{{- .Values.mysql.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default "mysql" .Values.mysql.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
MySQL service name
*/}}
{{- define "classic-models-api.mysql.servicename" -}}
{{- if .Values.mysql.enabled }}
{{- include "classic-models-api.mysql.fullname" . }}
{{- else }}
{{- required "mysql.externalHost is required when mysql.enabled is false" .Values.mysql.externalHost }}
{{- end }}
{{- end }}

{{/*
MySQL port
*/}}
{{- define "classic-models-api.mysql.port" -}}
{{- if .Values.mysql.enabled }}
{{- default 3306 .Values.mysql.primary.service.port }}
{{- else }}
{{- default 3306 .Values.mysql.externalPort }}
{{- end }}
{{- end }}

{{/*
MySQL database name
*/}}
{{- define "classic-models-api.mysql.database" -}}
{{- default "classicmodels" .Values.mysql.auth.database }}
{{- end }}

{{/*
MySQL username
*/}}
{{- define "classic-models-api.mysql.username" -}}
{{- default "classicuser" .Values.mysql.auth.username }}
{{- end }}

{{/*
Image name
*/}}
{{- define "classic-models-api.image" -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" .Values.image.repository $tag }}
{{- end }}