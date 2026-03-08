const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
  runtime_ms: number | null;
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
};
