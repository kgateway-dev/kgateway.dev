{{- define "valuesTable" -}}
| Key | Type | Description | Default |
|-----|------|-------------|---------|
{{- range .Values }}
| {{ .Name }} | {{ .Type }} | {{ .Description }} | {{ .Default | toJson }} |
{{- end }}
{{- end -}}