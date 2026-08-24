const BASE = "/api";

interface RequestOptions extends RequestInit {
  enrollmentToken?: string;
  adminToken?: string;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { enrollmentToken, adminToken, ...rest } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (enrollmentToken) headers["X-Enrollment-Token"] = enrollmentToken;
  if (adminToken) headers["X-Admin-Token"] = adminToken;

  const res = await fetch(BASE + path, { ...rest, headers });
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.detail ?? "";
    } catch {
      /* non-JSON error body */
    }
    if (res.status === 401) {
      throw new Error(detail || "Session expired — please re-enroll from the path page.");
    }
    throw new Error(detail || `Request failed: ${res.status}`);
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
  lesson: (enrollmentId: number, day?: number, enrollmentToken?: string) =>
    request<any>(`/enrollments/${enrollmentId}/lesson${day ? `?day=${day}` : ""}`, { enrollmentToken }),
  completeLesson: (enrollmentId: number, enrollmentToken?: string) =>
    request<any>(`/enrollments/${enrollmentId}/complete`, { method: "POST", enrollmentToken }),
  homework: (enrollmentId: number, enrollmentToken?: string) =>
    request<any>(`/enrollments/${enrollmentId}/homework`, { enrollmentToken }),
  submitHomework: (body: any, enrollmentToken?: string) =>
    request<any>("/homework/submit", { method: "POST", body: JSON.stringify(body), enrollmentToken }),
  dashboard: (enrollmentId: number, enrollmentToken?: string) =>
    request<any>(`/enrollments/${enrollmentId}/dashboard`, { enrollmentToken }),
  adminStudents: (adminToken: string) =>
    request<any[]>("/admin/students", { adminToken }),
  adminEnrollments: (adminToken: string) =>
    request<any[]>("/admin/enrollments", { adminToken }),
};
