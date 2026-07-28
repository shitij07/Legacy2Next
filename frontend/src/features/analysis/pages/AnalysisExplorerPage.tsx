import { useCallback, useMemo } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useProject } from '@/hooks/useProjects'
import { useAnalysisSummary } from '@/hooks/useAnalysis'
import { FilesTab } from '../components/files/FilesTab'
import { TechnologiesTab } from '../components/technologies/TechnologiesTab'
import { DependenciesTab } from '../components/dependencies/DependenciesTab'
import { WarningsTab } from '../components/warnings/WarningsTab'
import { MetricsTab } from '../components/metrics/MetricsTab'

const TABS = ['files', 'technologies', 'dependencies', 'warnings', 'metrics'] as const

export function AnalysisExplorerPage() {
  const { projectId, analysisId } = useParams<{ projectId: string; analysisId: string }>()
  const [searchParams, setSearchParams] = useSearchParams()

  const pid = Number(projectId)
  const aid = Number(analysisId)

  const activeTab = useMemo(() => {
    const tab = searchParams.get('tab')
    if (tab && TABS.includes(tab as typeof TABS[number])) return tab as typeof TABS[number]
    return 'files'
  }, [searchParams])

  const setActiveTab = useCallback(
    (tab: string) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev)
        next.set('tab', tab)
        return next
      })
    },
    [setSearchParams],
  )

  const {
    data: project,
    isLoading: projectLoading,
    isError: projectError,
  } = useProject(pid)

  const {
    data: summary,
    isLoading: summaryLoading,
    isError: summaryError,
    isFetching: summaryFetching,
    refetch: refetchSummary,
  } = useAnalysisSummary(aid)

  const isLoading = projectLoading || summaryLoading

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Analysis Explorer" />
        <LoadingState variant="page" />
      </div>
    )
  }

  if (projectError || !project) {
    return (
      <div>
        <PageHeader title="Project not found" />
        <ErrorState
          title="Failed to load project"
          message="The project could not be found or you do not have access."
        />
      </div>
    )
  }

  if (summaryError) {
    return (
      <div>
        <PageHeader title="Analysis Explorer" />
        <ErrorState
          title="Failed to load analysis"
          message="An unexpected error occurred."
        />
      </div>
    )
  }

  if (!summary) {
    return (
      <div>
        <PageHeader title="Analysis Explorer" />
        <ErrorState
          title="Analysis not found"
          message="The analysis could not be found or has not been completed yet."
        />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={`Analysis Data — ${project.name}`}
        description="Browse and explore analysis results."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => refetchSummary()}
              disabled={summaryFetching}
              aria-label="Refresh analysis data"
            >
              <RefreshCw className={`h-4 w-4 ${summaryFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
            </Button>
            <Button variant="ghost" asChild>
              <Link to={`/projects/${pid}/analyses/${aid}`}>
                <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                Dashboard
              </Link>
            </Button>
          </div>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-x-6 gap-y-1 text-sm text-neutral-600">
        <span>
          Status:{' '}
          <span className="font-medium text-neutral-800">{summary.status}</span>
        </span>
        {summary.completed_at && (
          <span>
            Completed:{' '}
            <span className="font-medium text-neutral-800">
              {new Date(summary.completed_at).toLocaleString()}
            </span>
          </span>
        )}
        <span>
          Files:{' '}
          <span className="font-medium text-neutral-800">{summary.file_count}</span>
        </span>
        <span>
          Technologies:{' '}
          <span className="font-medium text-neutral-800">{summary.technology_count}</span>
        </span>
        <span>
          Dependencies:{' '}
          <span className="font-medium text-neutral-800">{summary.dependency_count}</span>
        </span>
        <span>
          Warnings:{' '}
          <span className="font-medium text-neutral-800">{summary.warning_count}</span>
        </span>
      </div>

      <Separator className="mb-6" />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full overflow-x-auto" role="tablist" aria-label="Analysis data sections">
          <TabsTrigger value="files" role="tab">Files</TabsTrigger>
          <TabsTrigger value="technologies" role="tab">Technologies</TabsTrigger>
          <TabsTrigger value="dependencies" role="tab">Dependencies</TabsTrigger>
          <TabsTrigger value="warnings" role="tab">Warnings</TabsTrigger>
          <TabsTrigger value="metrics" role="tab">Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="files" role="tabpanel" tabIndex={0}>
          <FilesTab analysisId={aid} />
        </TabsContent>

        <TabsContent value="technologies" role="tabpanel" tabIndex={0}>
          <TechnologiesTab analysisId={aid} />
        </TabsContent>

        <TabsContent value="dependencies" role="tabpanel" tabIndex={0}>
          <DependenciesTab analysisId={aid} />
        </TabsContent>

        <TabsContent value="warnings" role="tabpanel" tabIndex={0}>
          <WarningsTab analysisId={aid} />
        </TabsContent>

        <TabsContent value="metrics" role="tabpanel" tabIndex={0}>
          <MetricsTab analysisId={aid} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
