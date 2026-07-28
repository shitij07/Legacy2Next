export const queryKeys = {
  projects: {
    all: ['projects'] as const,
    list: (page: number, size: number) => ['projects', 'list', { page, size }] as const,
    detail: (id: number) => ['projects', id] as const,
  },
  uploads: {
    byProject: (projectId: number, page: number, size: number) =>
      ['projects', projectId, 'uploads', { page, size }] as const,
    detail: (id: number) => ['uploads', id] as const,
  },
  analysis: {
    detail: (id: number) => ['analysis', id] as const,
    byUpload: (uploadId: number) => ['analysis', 'upload', uploadId] as const,
    dashboard: (id: number) => ['analysis', id, 'dashboard'] as const,
    files: (id: number, filters: object) =>
      ['analysis', id, 'files', filters] as const,
    technologies: (id: number) => ['analysis', id, 'technologies'] as const,
    dependencies: (id: number, filters: object) =>
      ['analysis', id, 'dependencies', filters] as const,
    metrics: (id: number) => ['analysis', id, 'metrics'] as const,
    warnings: (id: number, filters: object) =>
      ['analysis', id, 'warnings', filters] as const,
  },
  ai: {
    summary: (id: number) => ['ai', id, 'summary'] as const,
    architecture: (id: number) => ['ai', id, 'architecture'] as const,
    techDebt: (id: number) => ['ai', id, 'techDebt'] as const,
    modernization: (id: number) => ['ai', id, 'modernization'] as const,
    explanation: (analysisId: number, fileId: number) =>
      ['ai', analysisId, 'file', fileId, 'explain'] as const,
  },
}
