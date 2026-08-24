export interface SavedLearner {
  enrollmentId: number;
  pathName: string;
  studentName: string;
  studentEmail: string;
  /** MVP access control: presented as X-Enrollment-Token on every
   *  enrollment-scoped request. Issued by POST /api/assessment/submit. */
  token?: string;
}

const LEARNER_KEY = "pyschool:learner";
const PROFILE_KEY = "pyschool:profile";

export function savedLearner(): SavedLearner | null {
  try {
    const value = JSON.parse(localStorage.getItem(LEARNER_KEY) || "null");
    return value && Number.isFinite(value.enrollmentId) ? value : null;
  } catch {
    return null;
  }
}

export function saveLearner(learner: SavedLearner) {
  localStorage.setItem(LEARNER_KEY, JSON.stringify(learner));
  window.dispatchEvent(new Event("pyschool:learner-changed"));
}

export function savedProfile(): { name: string; email: string } {
  try {
    const profile = JSON.parse(localStorage.getItem(PROFILE_KEY) || "{}") || {};
    return { name: profile.name || "", email: profile.email || "" };
  } catch {
    return { name: "", email: "" };
  }
}

export function saveProfile(name: string, email: string) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify({ name, email }));
}

export function forgetLearner() {
  localStorage.removeItem(LEARNER_KEY);
  window.dispatchEvent(new Event("pyschool:learner-changed"));
}
