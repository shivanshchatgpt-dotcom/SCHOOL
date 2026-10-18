import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import { forgetLearner, saveLearner, savedLearner } from "../lib/learner";

interface HomeworkChecks {
  syntax_ok: boolean;
  lines_written: number;
  min_lines: number;
  lines_ok: boolean;
  patterns: { pattern: string; found: boolean }[];
}

interface HomeworkResult {
  passed: boolean;
  feedback: string;
  checks?: HomeworkChecks;
}

export default function Dashboard() {
  const { id } = useParams();
  const enrollmentId = Number(id);
  const learner = savedLearner();
  // The token only counts when it belongs to the enrollment in the URL.
  const token = learner && learner.enrollmentId === enrollmentId ? learner.token : undefined;

  const [data, setData] = useState<any>(null);
  const [lesson, setLesson] = useState<any>(null);
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [lessonRead, setLessonRead] = useState(false);
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [lastResult, setLastResult] = useState<HomeworkResult | null>(null);

  const load = async () => {
    try {
      const dashboard = await api.dashboard(enrollmentId, token);
      setData(dashboard);
      saveLearner({
        enrollmentId,
        pathName: dashboard.path_name,
        studentName: dashboard.student_name,
        studentEmail: dashboard.student_email,
        token,
      });
      try {
        const currentLesson = await api.lesson(enrollmentId, undefined, token);
        setLesson(currentLesson);
        setCode("");
        setLessonRead(localStorage.getItem(`pyschool:lesson-read:${enrollmentId}:${currentLesson.id}`) === "true");
      } catch (error) {
        setLesson(null);
        setMessage(error instanceof Error ? error.message : "The next module is being prepared.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load your school.");
    }
  };

  useEffect(() => { if (enrollmentId) void load(); }, [enrollmentId]);

  const submit = async () => {
    if (!lesson?.id) return;
    setBusy(true);
    try {
      const result: HomeworkResult = await api.submitHomework(
        { enrollment_id: enrollmentId, lesson_id: lesson.id, code },
        token
      );
      setLastResult(result);
      setMessage(result.feedback);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Submission failed.");
    } finally { setBusy(false); }
  };

  const complete = async () => {
    setBusy(true);
    try {
      const result = await api.completeLesson(enrollmentId, token);
      setMessage(result.message);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not complete this milestone.");
    } finally { setBusy(false); }
  };

  const toggleLessonRead = (checked: boolean) => {
    setLessonRead(checked);
    if (lesson) localStorage.setItem(`pyschool:lesson-read:${enrollmentId}:${lesson.id}`, String(checked));
  };

  if (!data) return (
    <div className="max-w-xl mx-auto py-20 text-center">
      {message ? (
        <>
          <h1 className="text-2xl font-black">We could not load your school</h1>
          <p className="text-gray-500 mt-3">{message}</p>
          <p className="text-gray-400 mt-2 text-sm">
            If this says the server is unreachable, the backend is not running on port 8000.
          </p>
        </>
      ) : (
        <p className="text-gray-400">Your school is loading…</p>
      )}
    </div>
  );
  if (!lesson) return <div className="max-w-xl mx-auto py-20 text-center"><h1 className="text-2xl font-black">Foundation complete</h1><p className="text-gray-500 mt-3">{message || "The next module is being prepared."}</p></div>;

  const practicePassed = Boolean(lesson.submission?.passed) || Boolean(lastResult?.passed);

  /* --- Requirements panel: what today's rubric expects, before submitting --- */
  const minLines: number = lesson.assignment.min_lines ?? 3;
  const requiredPatterns: string[] = lesson.assignment.required_patterns ?? [];
  const checks: HomeworkChecks | null =
    lastResult?.checks ??
    (lesson.submission
      ? { syntax_ok: true, lines_written: minLines, min_lines: minLines, lines_ok: true, patterns: requiredPatterns.map((p: string) => ({ pattern: p, found: true })) }
      : null);

  return <div className="space-y-7">
    <section className="bg-gray-950 text-white rounded-3xl p-7 md:p-9">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <p className="text-gray-400 text-sm">Welcome back, {data.student_name}</p>
          <h1 className="text-3xl font-black mt-1">{data.path_name}</h1>
          <p className="text-gray-400 mt-2">
            {data.level} placement · Day {data.current_day} of {data.available_lessons} available
            {data.coming_soon_days > 0 && (
              <span className="ml-2 text-amber-300/80">
                ({data.coming_soon_days} more days coming soon)
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-6 text-sm">
          <div><b className="text-2xl">{data.xp}</b><br /><span className="text-gray-400">XP</span></div>
          <div><b className="text-2xl">{data.streak}</b><br /><span className="text-gray-400">day streak</span></div>
          <div><b className="text-2xl">{data.review_ready}</b><br /><span className="text-gray-400">to review</span></div>
        </div>
      </div>
      <div className="mt-5 flex items-center justify-between gap-4 text-sm">
        <span className="text-gray-400">
          Week {Math.ceil(data.current_day / 7)} of {Math.max(1, Math.ceil(data.available_lessons / 7))} · {data.done_lessons} days completed
        </span>
        <button onClick={() => setShowRoadmap((value) => !value)} className="rounded-lg border border-gray-700 px-3 py-1.5 font-semibold text-white hover:bg-gray-800">
          {showRoadmap ? "Hide roadmap" : `View ${data.catalog_days}-day roadmap`}
        </button>
      </div>
      {showRoadmap && <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: data.catalog_days }, (_, index) => index + 1).map((day) => {
            const released = day <= data.available_lessons;
            const done = day < data.current_day;
            const current = day === data.current_day && released;
            return (
              <span
                key={day}
                title={released
                  ? undefined
                  : "This module is still being written. It is not part of your path yet."}
                className={
                  done ? "rounded-full bg-emerald-500 px-2.5 py-1 text-xs font-bold text-emerald-950"
                  : current ? "rounded-full bg-white px-2.5 py-1 text-xs font-bold text-gray-950"
                  : released ? "rounded-full bg-gray-800 px-2.5 py-1 text-xs font-bold text-gray-300"
                  : "rounded-full border border-dashed border-gray-700 px-2.5 py-1 text-xs font-bold text-gray-600"
                }
              >
                {released ? `Day ${day}` : `Day ${day} ·`}
                {done ? " ✓" : ""}
                {!released && <span className="ml-1 text-[9px] uppercase tracking-wider">soon</span>}
              </span>
            );
          })}
        </div>
        <p className="mt-3 text-xs text-gray-500">
          {data.available_lessons} of {data.catalog_days} days are written and available. Dashed days are
          still in development and do not count toward your progress.
        </p>
      </div>}
      <div className="mt-7"><div className="flex justify-between text-xs text-gray-400 mb-2"><span>Phase {data.phase} · {data.available_lessons} days available</span><span>{data.progress_pct}%</span></div><div className="h-2 rounded-full bg-gray-800"><div className="h-full rounded-full bg-white" style={{ width: data.progress_pct + "%" }} /></div></div>
    </section>

    {message && <div className={`rounded-xl border px-4 py-3 text-sm ${practicePassed ? "border-emerald-200 bg-emerald-50" : "border-gray-200 bg-gray-50"}`}>{message}</div>}

    <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-6">
      <article className="border border-gray-200 rounded-2xl p-6">
        <p className="text-xs font-bold uppercase tracking-wider text-gray-400">{lesson.milestone.code} · {lesson.milestone.domain}</p>
        <h2 className="text-2xl font-black mt-2">{lesson.title}</h2>
        <p className="mt-3 rounded-lg bg-violet-50 px-3 py-2 text-sm text-violet-900"><span className="font-bold">Objective:</span> {lesson.milestone.objective}</p>
        <LessonContent content={lesson.theory} />
        <pre className="mt-5"><code>{lesson.code_example}</code></pre>
        {Array.isArray(lesson.questions) && lesson.questions.length > 0 &&
          <ThinkCheck questions={lesson.questions} answers={lesson.answers} />}
        <div className="mt-5 rounded-xl border border-gray-200 p-4 text-sm">
          <p className="font-semibold">Mastery evidence</p>
          <p className="text-gray-600 mt-1">{lesson.milestone.mastery_criteria}</p>
          <p className="text-gray-500 mt-2">After the coding check, explain the idea in your own words and revisit it during review.</p>
        </div>
      </article>

      <aside className="border border-gray-200 rounded-2xl p-6 h-fit">
        <p className="text-xs font-bold uppercase tracking-wider text-gray-400">Day {data.current_day} checklist</p>
        <h2 className="text-xl font-black mt-2">Finish today’s lesson</h2>
        <label className="mt-5 flex gap-3 rounded-xl border border-gray-200 p-3 text-sm cursor-pointer">
          <input type="checkbox" checked={lessonRead} onChange={(event) => toggleLessonRead(event.target.checked)} className="mt-0.5 h-4 w-4" />
          <span><b>I read the lesson and understood the worked example.</b><br /><span className="text-gray-500">This saves in this browser.</span></span>
        </label>

        {/* Practice requirements — visible BEFORE any submission */}
        <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mt-6">Practice requirements</p>
        <ul className="mt-3 space-y-1.5 text-sm">
          <li className="flex items-start gap-2">
            <RequirementMark ok={checks ? checks.syntax_ok : null} pending={!checks} />
            <span>Valid Python syntax (your code is parsed, never executed)</span>
          </li>
          <li className="flex items-start gap-2">
            <RequirementMark ok={checks ? checks.lines_ok : null} pending={!checks} />
            <span>At least <b>{minLines} non-empty lines</b>{checks ? ` — you wrote ${checks.lines_written}` : ""}</span>
          </li>
          {requiredPatterns.map((pattern) => {
            const found = checks?.patterns.find((entry) => entry.pattern === pattern);
            return (
              <li key={pattern} className="flex items-start gap-2">
                <RequirementMark ok={found ? found.found : null} pending={!checks} />
                <span>Must include <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono">{pattern.trim()}</code> (spacing like <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono">print (…)</code> is accepted)</span>
              </li>
            );
          })}
        </ul>

        <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mt-6">Today’s practice</p>
        <p className="text-gray-600 text-sm mt-3 whitespace-pre-wrap">{lesson.assignment.prompt}</p>
        <div className="rounded-lg bg-gray-50 text-xs text-gray-600 px-3 py-2 mt-4">
          <span className="font-semibold">Rubric:</span> {lesson.assignment.rubric}
        </div>
        <textarea value={code} onChange={(event) => setCode(event.target.value)} className="w-full h-44 mt-5 bg-gray-950 text-gray-100 rounded-xl p-4 font-mono text-sm" placeholder="Write your Python code here…" />
        <button onClick={submit} disabled={busy || !code.trim() || practicePassed} className="w-full mt-3 bg-gray-100 border border-gray-300 px-5 py-3 rounded-xl font-semibold disabled:opacity-50">
          {practicePassed ? "Practice passed ✓" : "Check my practice"}
        </button>
        <button onClick={complete} disabled={busy || !practicePassed || !lessonRead} className="w-full mt-3 bg-black text-white px-5 py-3 rounded-xl font-semibold disabled:opacity-50">
          Complete Day {data.current_day} →
        </button>
        {practicePassed && lessonRead && <p className="mt-3 text-xs text-emerald-700 font-semibold">Everything is checked. Click “Complete Day {data.current_day}” to unlock Day {data.current_day + 1}.</p>}
        {(!practicePassed || !lessonRead) && <p className="mt-3 text-xs text-gray-500">Complete both checklist items to unlock the button. The checker only parses submitted source; it never executes it on the server.</p>}
      </aside>
    </div>
    <div className="text-right"><button onClick={forgetLearner} className="text-xs text-gray-400 hover:text-gray-800">This is not my account</button></div>
  </div>;
}

function RequirementMark({ ok, pending }: { ok: boolean | null; pending?: boolean }) {
  if (pending || ok === null) return <span className="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full border border-gray-300 text-[10px] text-gray-300">•</span>;
  return ok
    ? <span className="mt-0.5 shrink-0 font-bold text-emerald-600">✓</span>
    : <span className="mt-0.5 shrink-0 font-bold text-red-500">✗</span>;
}

function LessonContent({ content }: { content: string }) {
  return <div className="mt-5 text-gray-600">
    {content.split("\n\n").filter(Boolean).map((section, index) => {
      const [heading, ...body] = section.split("\n");
      return <section key={`${heading}-${index}`} className="mb-5">
        <h3 className="font-bold text-gray-900">{heading.replace(/^#{1,3}\s*/, "")}</h3>
        {body.map((line, lineIndex) => <p key={lineIndex} className="mt-1 leading-7">{line}</p>)}
      </section>;
    })}
  </div>;
}

function ThinkCheck({ questions, answers }: { questions: string[]; answers: string[] }) {
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  return <div className="mt-5 rounded-xl border border-violet-200 bg-violet-50/60 p-4">
    <p className="text-xs font-bold uppercase tracking-wider text-violet-700">Think check — answer first, then reveal</p>
    <ol className="mt-3 space-y-3 text-sm">
      {questions.map((question, index) => (
        <li key={index}>
          <p className="font-semibold text-gray-900">{index + 1}. {question}</p>
          {revealed[index]
            ? <p className="mt-1 rounded-lg bg-white px-3 py-2 text-gray-700 border border-violet-100">{answers?.[index] ?? "Discuss with a peer or revisit the example."}</p>
            : <button
                onClick={() => setRevealed((state) => ({ ...state, [index]: true }))}
                className="mt-1 rounded-lg border border-violet-300 bg-white px-3 py-1 text-xs font-semibold text-violet-700 hover:bg-violet-100">
                Reveal answer
              </button>}
        </li>
      ))}
    </ol>
  </div>;
}
