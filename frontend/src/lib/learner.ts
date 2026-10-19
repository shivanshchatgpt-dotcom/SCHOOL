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

export interface SavedProfile {
  name: string;
  email: string;
  /** Self-report answers (key -> chosen value) from the profiling step. */
  profile: Record<string, string>;
}

export function savedProfile(): SavedProfile {
  try {
    const profile = JSON.parse(localStorage.getItem(PROFILE_KEY) || "{}") || {};
    return {
      name: profile.name || "",
      email: profile.email || "",
      profile: profile.profile && typeof profile.profile === "object" ? profile.profile : {},
    };
  } catch {
    return { name: "", email: "", profile: {} };
  }
}

export function saveProfile(name: string, email: string, answers?: Record<string, string>) {
  const previous = savedProfile();
  localStorage.setItem(
    PROFILE_KEY,
    JSON.stringify({ name, email, profile: answers ?? previous.profile }),
  );
}

export function forgetLearner() {
  localStorage.removeItem(LEARNER_KEY);
  window.dispatchEvent(new Event("pyschool:learner-changed"));
}
