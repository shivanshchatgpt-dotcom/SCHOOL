import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { saveLearner, saveProfile, savedProfile } from "../lib/learner";

interface Question {
  id: number;
  path_id: number;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  difficulty: number;
}

interface ProfileQuestion {
  id: number;
  key: string;
  question: string;
  options: { value: string; label: string }[];
}

interface Result {
  enrollment_id: number;
  score: number;
  total: number;
  level: string;
  feedback: string;
  starting_milestone: { code: string; title: string };
  weak_topics: string[];
  access_token?: string;
}

const levelStyle: Record<string, string> = {
  Foundation: "bg-violet-50 text-violet-700 border-violet-200",
  Beginner: "bg-blue-50 text-blue-700 border-blue-200",
  Intermediate: "bg-amber-50 text-amber-700 border-amber-200",
  Advanced: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

type Stage = "profile" | "info" | "quiz";

export default function Assessment() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const profile = savedProfile();
  const [path, setPath] = useState<any>(null);
  const [profileQs, setProfileQs] = useState<ProfileQuestion[]>([]);
  const [profileAnswers, setProfileAnswers] = useState<Record<string, string>>(profile.profile);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [stage, setStage] = useState<Stage>("profile");
  const [step, setStep] = useState(0);
  const [name, setName] = useState(profile.name || "");
  const [email, setEmail] = useState(profile.email || "");
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Result | null>(null);

  useEffect(() => {
    if (!slug) return;
    Promise.all([api.pathBySlug(slug), api.profileQuestions().catch(() => [])])
      .then(([p, pq]: [any, ProfileQuestion[]]) => {
        setPath(p);
        setProfileQs(pq);
        // No profiling questions configured -> go straight to the details step.
        if (pq.length === 0) setStage("info");
      })
      .catch((err) => setError(String(err)));
  }, [slug]);

  const loadQuestions = (experience?: string) => {
    if (!path) return;
    api
      .questions(path.id, experience)
      .then(setQuestions)
      .catch((err) => setError(String(err)));
  };

  if (error) return <div className="text-red-600 py-20 text-center">{error}</div>;
  if (!path) return <div className="text-center py-20 text-gray-400">Loading…</div>;

  const current = questions[step];
  const profileComplete = profileQs.every((q) => profileAnswers[q.key]);

  const submit = async () => {
    setSubmitting(true);
    try {
      const res = await api.submitAssessment({
        path_id: path.id,
        student_name: name,
        student_email: email,
        answers: Object.entries(answers).map(([qid, selected]) => ({
          question_id: Number(qid),
          selected,
        })),
        profile: profileAnswers,
      });
      saveProfile(name.trim(), email.trim().toLowerCase(), profileAnswers);
      saveLearner({
        enrollmentId: res.enrollment_id,
        pathName: path.name,
        studentName: name.trim(),
        studentEmail: email.trim().toLowerCase(),
        token: res.access_token,
      });
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmitting(false);
    }
  };

  /* --- Result view --- */
  if (result) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gray-100 border border-gray-200 grid place-items-center text-3xl mx-auto">
            🎓
          </div>
          <h1 className="text-3xl font-black mt-6">Assessment complete!</h1>
          <div className={`inline-flex items-center px-4 py-1.5 rounded-full border mt-4 font-bold ${levelStyle[result.level] ?? ""}`}>
            {result.level} level
          </div>
          <p className="text-gray-500 mt-3">
            You scored <span className="font-bold text-gray-900">{result.score}</span> / {result.total}
          </p>
          <p className="text-gray-600 mt-4 leading-relaxed">{result.feedback}</p>
          <div className="mt-5 rounded-xl bg-gray-50 border border-gray-200 p-4 text-left text-sm">
            <p className="font-semibold">Your starting milestone</p>
            <p className="text-gray-600 mt-1">{result.starting_milestone.code} · {result.starting_milestone.title}</p>
            {result.weak_topics.length > 0 && <p className="text-gray-500 mt-2">Review focus: {result.weak_topics.join(", ").replace(/-/g, " ")}</p>}
          </div>
          <button
            onClick={() => navigate(`/dashboard/${result.enrollment_id}`)}
            className="mt-8 bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800"
          >
            Go to my school →
          </button>
        </div>
      </div>
    );
  }

  /* --- Profiling step --- */
  if (stage === "profile") {
    return (
      <div className="max-w-xl mx-auto py-12">
        <h1 className="text-2xl font-black">Let's set you up</h1>
        <p className="text-gray-500 mt-1 mb-8">
          A few quick questions so we can tune the {path.name} level test to you.
        </p>
        <div className="space-y-6">
          {profileQs.map((q) => (
            <div key={q.key}>
              <p className="font-semibold mb-2">{q.question}</p>
              <div className="space-y-2">
                {q.options.map((opt, i) => (
                  <button
                    key={`${q.key}-${i}`}
                    onClick={() => setProfileAnswers((prev) => ({ ...prev, [q.key]: opt.value }))}
                    className={`w-full text-left border rounded-xl px-4 py-2.5 transition-colors ${
                      profileAnswers[q.key] === opt.value
                        ? "border-gray-900 bg-gray-50"
                        : "border-gray-200 hover:border-gray-400"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        <button
          disabled={!profileComplete}
          onClick={() => setStage("info")}
          className="w-full mt-8 bg-black text-white py-3 rounded-xl font-semibold hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continue →
        </button>
      </div>
    );
  }

  /* --- Student info step --- */
  if (stage === "info") {
    return (
      <div className="max-w-md mx-auto py-12">
        <h1 className="text-2xl font-black">Before you start</h1>
        <p className="text-gray-500 mt-1 mb-8">Tell us who you are — this joins you to {path.name}.</p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-1">Your name</label>
            <input
              value={name}
              onChange={(e) => { setName(e.target.value); saveProfile(e.target.value, email, profileAnswers); }}
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-gray-900"
              placeholder="e.g. Aarav Kumar"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Email</label>
            <input
              value={email}
              onChange={(e) => { setEmail(e.target.value); saveProfile(name, e.target.value, profileAnswers); }}
              type="email"
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-gray-900"
              placeholder="you@example.com"
            />
          </div>
          <button
            disabled={!name.trim() || !email.trim() || submitting}
            onClick={() => { loadQuestions(profileAnswers.experience); setStage("quiz"); }}
            className="w-full bg-black text-white py-3 rounded-xl font-semibold hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Start the level test →
          </button>
        </div>
      </div>
    );
  }

  /* --- Question steps --- */
  if (!current) return <div className="text-center py-20 text-gray-400">Loading questions…</div>;

  const select = (option: string) => {
    setAnswers((prev) => ({ ...prev, [current.id]: option }));
    if (step < questions.length - 1) {
      setStep((s) => s + 1);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-gray-400">{path.name}</p>
          <h1 className="text-2xl font-black">Level test</h1>
        </div>
        <span className="text-sm font-semibold text-gray-500">
          {step + 1} / {questions.length}
        </span>
      </div>

      <div className="h-1.5 bg-gray-100 rounded-full mb-8 overflow-hidden">
        <div
          className="h-full bg-gray-900 transition-all"
          style={{ width: `${((step + 1) / questions.length) * 100}%` }}
        />
      </div>

      <div className="border border-gray-200 rounded-2xl p-6">
        <h2 className="text-lg font-bold mb-6">{current.question}</h2>
        <div className="space-y-3">
          {[
            { key: "A", text: current.option_a },
            { key: "B", text: current.option_b },
            { key: "C", text: current.option_c },
            { key: "D", text: current.option_d },
          ].map((opt) => (
            <button
              key={opt.key}
              onClick={() => select(opt.key)}
              className={`w-full text-left border rounded-xl px-4 py-3 hover:border-gray-900 hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                answers[current.id] === opt.key ? "border-gray-900 bg-gray-50" : "border-gray-200"
              }`}
            >
              <span className="w-7 h-7 rounded-full bg-gray-100 border border-gray-200 grid place-items-center text-xs font-bold shrink-0">
                {opt.key}
              </span>
              <span>{opt.text}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex justify-between mt-6">
        <button
          onClick={() => (step === 0 ? setStage("info") : setStep((s) => s - 1))}
          className="px-4 py-2 text-sm font-semibold text-gray-500 hover:text-gray-900"
        >
          ← Back
        </button>
        {step === questions.length - 1 && (
          <button
            onClick={submit}
            disabled={submitting}
            className="bg-black text-white px-6 py-2.5 rounded-xl font-semibold hover:bg-gray-800 disabled:opacity-40"
          >
            {submitting ? "Checking…" : "Submit answers →"}
          </button>
        )}
        <span />
      </div>
    </div>
  );
}
