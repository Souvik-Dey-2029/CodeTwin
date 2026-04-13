const API_BASE_URL = "/api/v1";

export interface Repository {
  id: number;
  name: string;
  github_url: string;
  health_score: number;
  default_branch: string;
  created_at: string;
}

export interface AnalysisStatus {
  id: number;
  repo_id: number;
  status: "Queue" | "Active" | "Done" | "Error";
  runtime_ms?: number;
}

export interface DashboardSummary {
  health_score: number;
  status: string;
  analysis_id: number | null;
  god_object_count: number;
  total_files: number;
  total_dependencies: number;
  risk_level: string;
}

export interface RefactorProposal {
  file_path: string;
  complexity: number;
  centrality: number;
  reason: string;
  suggested_action: string;
}

export interface ImpactSimulation {
  target: string;
  impact_score: number;
  affected_nodes: {
    id: string;
    distance: number;
    centrality: number;
  }[];
}

export interface DeadFunctionFinding {
  name: string;
  file: string;
  line: number;
  type: string;
  confidence: number;
}

export interface DeadCodeAnalysis {
  dead_functions: DeadFunctionFinding[];
  unused_imports: any[];
  total_functions_analyzed: number;
  total_files_analyzed: number;
  total_issues: number;
}

export interface UnusedDependency {
  name: string;
  version: string;
  type: string;
  confidence: number;
  suggestion: string;
}

export interface DependencyAnalysis {
  unused_dependencies: UnusedDependency[];
  missing_dependencies: any[];
  total_declared: number;
  total_used: number;
  issue_count: number;
  summary?: string;
}

export const api = {
  async submitRepository(githubUrl: string): Promise<Repository> {
    const response = await fetch(`${API_BASE_URL}/repositories/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ github_url: githubUrl }),
    });
    if (!response.ok) throw new Error("Failed to submit repository");
    return response.json();
  },

  async listRepositories(): Promise<Repository[]> {
    const response = await fetch(`${API_BASE_URL}/repositories/`);
    if (!response.ok) throw new Error("Failed to fetch repositories");
    return response.json();
  },

  async getDashboardSummary(repoId: number): Promise<DashboardSummary> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/summary`);
    if (!response.ok) throw new Error("Failed to fetch dashboard summary");
    return response.json();
  },

  async getAnalysisStatus(repoId: number): Promise<AnalysisStatus> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/status`);
    if (!response.ok) throw new Error("Failed to fetch status");
    return response.json();
  },

  async getRepository(repoId: number): Promise<Repository> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}`);
    if (!response.ok) throw new Error("Failed to fetch repository details");
    return response.json();
  },

  async getRepositoryGraph(repoId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/graph`);
    if (!response.ok) throw new Error("Failed to fetch graph data");
    return response.json();
  },

  async getRepositoryHeatmap(repoId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/heatmap`);
    if (!response.ok) throw new Error("Failed to fetch heatmap data");
    return response.json();
  },

  async getRefactorProposals(repoId: number): Promise<RefactorProposal[]> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/refactor-proposals`);
    if (!response.ok) throw new Error("Failed to fetch proposals");
    return response.json();
  },

  async getFileContent(repoId: number, path: string): Promise<{ content: string }> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/file-content?path=${encodeURIComponent(path)}`);
    if (!response.ok) throw new Error("Failed to fetch file content");
    return response.json();
  },

  async simulateImpact(repoId: number, filePath: string): Promise<ImpactSimulation> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/simulate-impact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: filePath }),
    });
    if (!response.ok) throw new Error("Failed to simulate impact");
    return response.json();
  },

  async getAiRefactorAdvice(repoId: number, filePath: string): Promise<{ advice: string }> {
    // Base64 encode the path to safely pass it in URL
    const b64Path = typeof window !== 'undefined' ? btoa(filePath) : Buffer.from(filePath).toString('base64');
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/ai-advice?file_path_b64=${encodeURIComponent(b64Path)}`);
    if (!response.ok) throw new Error("Failed to fetch AI advice");
    return response.json();
  },

  async reanalyzeRepository(repoId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/reanalyze`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to trigger reanalysis");
    return response.json();
  },

  async getDeadCodeAnalysis(repoId: number): Promise<DeadCodeAnalysis> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/dead-code`);
    if (!response.ok) throw new Error("Failed to fetch dead code analysis");
    return response.json();
  },

  async getDependencyAnalysis(repoId: number): Promise<DependencyAnalysis> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/dependencies`);
    if (!response.ok) throw new Error("Failed to fetch dependency analysis");
    return response.json();
  },

  async explainDeadFunction(repoId: number, funcIndex: number): Promise<{ explanation: string; confidence: number }> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/dead-code/${funcIndex}/explanation`);
    if (!response.ok) throw new Error("Failed to fetch explanation");
    return response.json();
  },

  async explainUnusedDependency(repoId: number, depIndex: number): Promise<{ explanation: string; confidence: number }> {
    const response = await fetch(`${API_BASE_URL}/repositories/${repoId}/dependencies/${depIndex}/explanation`);
    if (!response.ok) throw new Error("Failed to fetch explanation");
    return response.json();
  },
};
