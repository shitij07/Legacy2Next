import { useState, useMemo } from 'react'
import { Search, FolderIcon, FileIcon } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { Badge } from '@/components/ui/badge'
import { useAnalysisFiles } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'
import { formatFileSize } from '@/services/upload'
import { DataTable } from '../explorer/DataTable'
import { PaginationBar } from '../explorer/PaginationBar'
import type { AnalysisFile, AnalysisFilesParams } from '@/lib/types'
import type { Column } from '../explorer/DataTable'

interface FilesTabProps {
  analysisId: number
}

export function FilesTab({ analysisId }: FilesTabProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [language, setLanguage] = useState('all')
  const [extension, setExtension] = useState('all')
  const [directoryOnly, setDirectoryOnly] = useState(false)
  const [sortBy, setSortBy] = useState('relative_path')
  const [sortDir, setSortDir] = useState('asc')

  const debouncedSearch = useDebounce(search, 300)

  const params: AnalysisFilesParams = useMemo(
    () => ({
      page,
      size: 50,
      search: debouncedSearch || undefined,
      language: language && language !== 'all' ? language : undefined,
      extension: extension && extension !== 'all' ? extension : undefined,
      is_directory: directoryOnly || undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
    }),
    [page, debouncedSearch, language, extension, directoryOnly, sortBy, sortDir],
  )

  const { data, isLoading, isError, error, refetch } = useAnalysisFiles(analysisId, params)

  const columns: Column<AnalysisFile>[] = useMemo(
    () => [
      {
        key: 'file_name',
        header: 'File Name',
        render: (item) => (
          <div className="flex items-center gap-2">
            {item.is_directory ? (
              <FolderIcon className="h-4 w-4 shrink-0 text-info" aria-hidden="true" />
            ) : (
              <FileIcon className="h-4 w-4 shrink-0 text-neutral-500" aria-hidden="true" />
            )}
            <span className="font-medium text-neutral-900">{item.file_name}</span>
          </div>
        ),
      },
      {
        key: 'relative_path',
        header: 'Relative Path',
        render: (item) => (
          <span className="text-neutral-600">{item.relative_path}</span>
        ),
        className: 'hidden md:table-cell',
      },
      {
        key: 'language',
        header: 'Language',
        render: (item) =>
          item.language ? (
            <Badge variant="info" size="sm">{item.language}</Badge>
          ) : (
            <span className="text-neutral-500">—</span>
          ),
        className: 'hidden sm:table-cell',
      },
      {
        key: 'extension',
        header: 'Extension',
        render: (item) =>
          item.extension ? (
            <code className="rounded bg-neutral-200 px-1.5 py-0.5 text-xs text-neutral-700">{item.extension}</code>
          ) : (
            <span className="text-neutral-500">—</span>
          ),
        className: 'hidden sm:table-cell',
      },
      {
        key: 'file_size',
        header: 'Size',
        render: (item) => <span className="text-neutral-700">{formatFileSize(item.file_size)}</span>,
        className: 'text-right',
      },
      {
        key: 'is_directory',
        header: 'Directory',
        render: (item) =>
          item.is_directory ? (
            <Badge variant="default" size="sm">Yes</Badge>
          ) : (
            <span className="text-neutral-500">No</span>
          ),
        className: 'hidden lg:table-cell text-center',
      },
    ],
    [],
  )

  if (isLoading) {
    return <LoadingState variant="table" count={5} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load files"
        message={error?.message ?? 'An unexpected error occurred.'}
        onRetry={() => refetch()}
      />
    )
  }

  const files = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 1

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
          <Input
            placeholder="Search files..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
            aria-label="Search files"
          />
        </div>
        <Select value={language} onValueChange={(v) => { setLanguage(v); setPage(1) }}>
          <SelectTrigger className="w-36" aria-label="Filter by language">
            <SelectValue placeholder="Language" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Languages</SelectItem>
            <SelectItem value="TypeScript">TypeScript</SelectItem>
            <SelectItem value="JavaScript">JavaScript</SelectItem>
            <SelectItem value="Python">Python</SelectItem>
            <SelectItem value="Java">Java</SelectItem>
            <SelectItem value="C#">C#</SelectItem>
            <SelectItem value="Go">Go</SelectItem>
            <SelectItem value="Rust">Rust</SelectItem>
            <SelectItem value="Ruby">Ruby</SelectItem>
            <SelectItem value="PHP">PHP</SelectItem>
            <SelectItem value="HTML">HTML</SelectItem>
            <SelectItem value="CSS">CSS</SelectItem>
          </SelectContent>
        </Select>
        <Select value={extension} onValueChange={(v) => { setExtension(v); setPage(1) }}>
          <SelectTrigger className="w-32" aria-label="Filter by extension">
            <SelectValue placeholder="Extension" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Extensions</SelectItem>
            <SelectItem value=".ts">.ts</SelectItem>
            <SelectItem value=".tsx">.tsx</SelectItem>
            <SelectItem value=".js">.js</SelectItem>
            <SelectItem value=".jsx">.jsx</SelectItem>
            <SelectItem value=".py">.py</SelectItem>
            <SelectItem value=".java">.java</SelectItem>
            <SelectItem value=".cs">.cs</SelectItem>
            <SelectItem value=".go">.go</SelectItem>
            <SelectItem value=".rs">.rs</SelectItem>
            <SelectItem value=".rb">.rb</SelectItem>
            <SelectItem value=".php">.php</SelectItem>
            <SelectItem value=".html">.html</SelectItem>
            <SelectItem value=".css">.css</SelectItem>
            <SelectItem value=".json">.json</SelectItem>
            <SelectItem value=".xml">.xml</SelectItem>
            <SelectItem value=".yaml">.yaml</SelectItem>
            <SelectItem value=".md">.md</SelectItem>
            <SelectItem value=".sql">.sql</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1) }}>
          <SelectTrigger className="w-36" aria-label="Sort files">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="relative_path">Path</SelectItem>
            <SelectItem value="file_size">Size</SelectItem>
            <SelectItem value="extension">Extension</SelectItem>
            <SelectItem value="language">Language</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortDir} onValueChange={(v) => { setSortDir(v); setPage(1) }}>
          <SelectTrigger className="w-28" aria-label="Sort direction">
            <SelectValue placeholder="Direction" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="asc">Ascending</SelectItem>
            <SelectItem value="desc">Descending</SelectItem>
          </SelectContent>
        </Select>
        <label className="flex items-center gap-2 text-sm text-neutral-700">
          <input
            type="checkbox"
            checked={directoryOnly}
            onChange={(e) => { setDirectoryOnly(e.target.checked); setPage(1) }}
            className="h-4 w-4 rounded border-border accent-primary-500"
          />
          Directories only
        </label>
      </div>

      {files.length === 0 ? (
        <EmptyState
          title="No files found"
          description={debouncedSearch ? 'Try a different search term.' : 'This analysis has no files.'}
        />
      ) : (
        <>
          <DataTable columns={columns} data={files} />
          <PaginationBar
            page={page}
            size={50}
            total={total}
            pages={pages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}
