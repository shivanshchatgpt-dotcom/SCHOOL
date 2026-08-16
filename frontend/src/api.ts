const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  categories: () => request<any[]>("/categories"),
  paths: (params?: { category_id?: number; q?: string }) => {
    const query = new URLSearchParams();
    if (params?.category_id) query.set("category_id", String(params.category_id));
    if (params?.q) query.set("q", params.q);
    const qs = query.toString();
    return request<any[]>(`/paths${qs ? `?${qs}` : ""}`);
  },
  pathBySlug: (slug: string) => request<any>(`/paths/${slug}`),
  questions: (pathId: number) => request<any[]>(`/assessment/${pathId}/questions`),
  submitAssessment: (body: any) =>
    request<any>("/assessment/submit", { method: "POST", body: JSON.stringify(body) }),
  lesson: (enrollmentId: number, day?: number) =>
    request<any>(`/enrollments/${enrollmentId}/lesson${day ? `?day=${day}` : ""}`),
  completeLesson: (enrollmentId: number) =>
    request<any>(`/enrollments/${enrollmentId}/complete`, { method: "POST" }),
  homework: (enrollmentId: number) => request<any>(`/enrollments/${enrollmentId}/homework`),
  submitHomework: (body: any) =>
    request<any>("/homework/submit", { method: "POST", body: JSON.stringify(body) }),
  dashboard: (enrollmentId: number) => request<any>(`/enrollments/${enrollmentId}/dashboard`),
  adminStudents: () => request<any[]>("/admin/students"),
  adminEnrollments: () => request<any[]>("/admin/enrollments"),
};
