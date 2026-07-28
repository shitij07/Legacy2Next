import { useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useProject } from '@/hooks/useProjects'
import { useAnalysisSummary } from '@/hooks/useAnalysis'
import {
  useGenerateSummary,
  useGenerateArchitecture,
  useGenerateTechnicalDebt,
  useGenerateModernization,
  useGenerateFileExplanation,
  useGenerateModuleExplanation,
} from '@/hooks/useAI'
import { SummarySection } from '../components/summary/SummarySection'
import { ArchitectureSection } from '../components/architecture/ArchitectureSection'
import { TechnicalDebtSection } from '../components/technicalDebt/TechnicalDebtSection'
import { ModernizationSection } from '../components/modernization/ModernizationSection'
import { FileExplanationSection } from '../components/fileExplanation/FileExplanationSection'
import { ModuleExplanationSection } from '../components/moduleExplanation/ModuleExplanationSection'

export function AIWorkspacePage() {
  const { projectId, analysisId } = useParams<{ projectId: string; analysisId: string }>()
  const pid = Number(projectId)
  const aid = Number(analysisId)

  const { data: project, isLoading: projectLoading, isError: projectError } = useProject(pid)
  const { data: summary, isLoading: summaryLoading, isFetching: summaryFetching, refetch: refetchSummary } =
    useAnalysisSummary(aid)

  const summaryMutation = useGenerateSummary()
  const architectureMutation = useGenerateArchitecture()
  const techDebtMutation = useGenerateTechnicalDebt()
  const modernizationMutation = useGenerateModernization()
  const fileExplanationMutation = useGenerateFileExplanation()
  const moduleExplanationMutation = useGenerateModuleExplanation()

  const handleGenerateSummary = useCallback(() => {
    summaryMutation.mutate(aid)
  }, [summaryMutation, aid])

  const handleGenerateArchitecture = useCallback(() => {
    architectureMutation.mutate(aid)
  }, [architectureMutation, aid])

  const handleGenerateTechDebt = useCallback(() => {
    techDebtMutation.mutate(aid)
  }, [techDebtMutation, aid])

  const handleGenerateModernization = useCallback(() => {
    modernizationMutation.mutate(aid)
  }, [modernizationMutation, aid])

  const handleGenerateFileExplanation = useCallback(
    (fileId: number) => {
      fileExplanationMutation.mutate({ analysisId: aid, fileId })
    },
    [fileExplanationMutation, aid],
  )

  const handleGenerateModuleExplanation = useCallback(
    (modulePath: string) => {
      moduleExplanationMutation.mutate({ analysisId: aid, modulePath })
    },
    [moduleExplanationMutation, aid],
  )

  const isLoading = projectLoading || summaryLoading

  if (isLoading) {
    return (
      <div>
        <PageHeader title="AI Workspace" />
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

  if (!summary) {
    return (
      <div>
        <PageHeader title="AI Workspace" />
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
        title={`AI Workspace — ${project.name}`}
        description="Generate AI-powered insights and recommendations for your codebase."
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
            <Button variant="outline" size="sm" asChild>
              <Link to={`/projects/${pid}/analyses/${aid}/explorer`}>
                Data Explorer
              </Link>
            </Button>
          </div>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-x-6 gap-y-1 text-sm text-neutral-600">
        <span>
          Status: <span className="font-medium text-neutral-800">{summary.status}</span>
        </span>
        {summary.completed_at && (
          <span>
            Completed:{' '}
            <span className="font-medium text-neutral-800">
              {new Date(summary.completed_at).toLocaleString()}
            </span>
          </span>
        )}
      </div>

      <Separator className="mb-6" />

      <div className="grid gap-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <SummarySection
            onGenerate={handleGenerateSummary}
            isGenerating={summaryMutation.isPending}
            response={summaryMutation.data ?? null}
            error={summaryMutation.error}
            onRegenerate={handleGenerateSummary}
          />
          <ArchitectureSection
            onGenerate={handleGenerateArchitecture}
            isGenerating={architectureMutation.isPending}
            response={architectureMutation.data ?? null}
            error={architectureMutation.error}
            onRegenerate={handleGenerateArchitecture}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <TechnicalDebtSection
            onGenerate={handleGenerateTechDebt}
            isGenerating={techDebtMutation.isPending}
            response={techDebtMutation.data ?? null}
            error={techDebtMutation.error}
            onRegenerate={handleGenerateTechDebt}
          />
          <ModernizationSection
            onGenerate={handleGenerateModernization}
            isGenerating={modernizationMutation.isPending}
            response={modernizationMutation.data ?? null}
            error={modernizationMutation.error}
            onRegenerate={handleGenerateModernization}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <FileExplanationSection
            analysisId={aid}
            onGenerate={handleGenerateFileExplanation}
            isGenerating={fileExplanationMutation.isPending}
            response={fileExplanationMutation.data ?? null}
            error={fileExplanationMutation.error}
            onRegenerate={handleGenerateFileExplanation}
          />
          <ModuleExplanationSection
            onGenerate={handleGenerateModuleExplanation}
            isGenerating={moduleExplanationMutation.isPending}
            response={moduleExplanationMutation.data ?? null}
            error={moduleExplanationMutation.error}
            onRegenerate={handleGenerateModuleExplanation}
          />
        </div>
      </div>
    </div>
  )
}
