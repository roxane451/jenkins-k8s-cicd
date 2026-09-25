{{/* Labels communs */}}
{{- define "movie-app.labels" -}}
app.kubernetes.io/part-of: {{ .Chart.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/* Référence complète d'une image applicative : <registry>/<nom>:<tag> */}}
{{- define "movie-app.image" -}}
{{- $root := index . 0 -}}
{{- $name := index . 1 -}}
{{- $registry := required "image.registry est obligatoire (ex: c8n.io/mon-compte)" $root.Values.image.registry -}}
{{- $tag := required "image.tag est obligatoire (fourni par le pipeline)" $root.Values.image.tag -}}
{{- printf "%s/%s:%s" $registry $name $tag -}}
{{- end }}

{{/* securityContext conteneur durci, commun à tous les pods */}}
{{- define "movie-app.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: ["ALL"]
{{- end }}
