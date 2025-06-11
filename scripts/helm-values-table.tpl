{{- define "valuesTable" -}}
| Key | Type | Description | Default |
|-----|------|-------------|---------|
{{- range .Values }}
| {{ .Name }} | {{ .Type }} | {{ .Description | markdownify | nindent 0 }} | {{ .Default | toJson }} |
{{- end }}
{{- end -}}