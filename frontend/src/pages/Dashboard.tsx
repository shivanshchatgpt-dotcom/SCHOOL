import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

export default function Dashboard() {
  const { id } = useParams();
  const enrollmentId = Number(id);
  const [data, setData] = useState<any>(null);
  const [lesson, setLesson] = useState<any>(null);
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => Promise.all([api.dashboard(enrollmentId), api.lesson(enrollmentId)])
    .then(([d, l]) => { setData(d); setLesson(l); setCode(l.code_example || ""); })
    .catch((e) => setMessage(String(e)));
  useEffect(() => { if (enrollmentId) load(); }, [enrollmentId]);

  const complete = async () => { setBusy(true); try { const r = await api.completeLesson(enrollmentId); setMessage(r.message); await load(); } catch (e) { setMessage(String(e)); } finally { setBusy(false); } };
  const submit = async () => {
    if (!lesson?.id) { setMessage("Is lesson ka homework abhi auto-generated hai; pehle class complete karke next lesson unlock karein."); return; }
    setBusy(true); try { const r = await api.submitHomework({ enrollment_id: enrollmentId, lesson_id: lesson.id, code }); setMessage(r.feedback); await load(); } catch (e) { setMessage(String(e)); } finally { setBusy(false); }
  };

  if (!data || !lesson) return <div className="text-center py-20 text-gray-400">Your school is loading…</div>;
  return <div className="space-y-7">
    <section className="bg-gray-950 text-white rounded-3xl p-7 md:p-9">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div><p className="text-gray-400 text-sm">Welcome back, {data.student_name}</p><h1 className="text-3xl font-black mt-1">{data.path_name}</h1><p className="text-gray-400 mt-2">{data.level} track · Day {data.current_day}</p></div>
        <div className="flex gap-6 text-sm"><div><b className="text-2xl">{data.xp}</b><br/><span className="text-gray-400">XP</span></div><div><b className="text-2xl">{data.streak}</b><br/><span className="text-gray-400">day streak</span></div><div><b className="text-2xl">{data.penalty_points}</b><br/><span className="text-gray-400">penalties</span></div></div>
      </div>
      <div className="mt-7"><div className="flex justify-between text-xs text-gray-400 mb-2"><span>Progress</span><span>{data.progress_pct}%</span></div><div className="h-2 rounded-full bg-gray-800"><div className="h-full rounded-full bg-white" style={{width: `${data.progress_pct}%`}} /></div></div>
    </section>
    {message && <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm">{message}</div>}
    <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-6">
      <article className="border border-gray-200 rounded-2xl p-6"><p className="text-xs font-bold uppercase tracking-wider text-gray-400">Today’s 1-hour class</p><h2 className="text-2xl font-black mt-2">{lesson.title}</h2><div className="prose-pyschool mt-5 whitespace-pre-wrap text-gray-600">{lesson.theory}</div><pre className="mt-5"><code>{lesson.code_example}</code></pre><button onClick={complete} disabled={busy} className="mt-2 bg-black text-white px-5 py-3 rounded-xl font-semibold disabled:opacity-50">{busy ? "Saving…" : "Mark class complete →"}</button></article>
      <aside className="border border-gray-200 rounded-2xl p-6 h-fit"><p className="text-xs font-bold uppercase tracking-wider text-gray-400">Homework</p><h2 className="text-xl font-black mt-2">Build something small</h2><p className="text-gray-600 text-sm mt-3 whitespace-pre-wrap">{lesson.homework}</p><textarea value={code} onChange={e => setCode(e.target.value)} className="w-full h-44 mt-5 bg-gray-950 text-gray-100 rounded-xl p-4 font-mono text-sm" placeholder="Paste your Python code here…" /><button onClick={submit} disabled={busy || !code.trim()} className="w-full mt-3 bg-gray-100 border border-gray-300 px-5 py-3 rounded-xl font-semibold disabled:opacity-50">Submit homework</button></aside>
    </div>
  </div>;
}
