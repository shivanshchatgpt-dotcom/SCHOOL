import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api";

export default function Home() {
  const [pathCount, setPathCount] = useState<number | null>(null);
  const [categoryCount, setCategoryCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Leave the counts unknown on failure rather than reporting zero. Zero is a
    // claim about the catalogue, and an unreachable API is not that.
    api.paths()
      .then((paths) => { setPathCount(paths.length); setError(null); })
      .catch((err) => setError(`Could not reach the server: ${(err as Error).message}`));
    api.categories()
      .then((cats) => setCategoryCount(cats.length))
      .catch(() => setCategoryCount(null));
  }, []);

  return (
    <div className="space-y-12">
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}. The backend appears to be down — start it on port 8000 and reload.
        </div>
      )}
      {/* Hero */}
      <section className="py-16 text-center">
        <h1 className="text-5xl md:text-6xl font-black tracking-tight text-gray-900">
          Stop wandering.
          <br />
          <span className="text-gray-400">Start belonging to a school.</span>
        </h1>
        <p className="mx-auto max-w-2xl mt-6 text-lg text-gray-600 leading-relaxed">
          There are thousands of free Python resources — and that's the problem.
          PySchool asks you{" "}
          <span className="font-semibold text-gray-900">what you want to become</span>,
          tests your level, then gives you a daily 1-hour class, homework and
          progress — exactly like a real school.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            to="/paths"
            className="bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 transition-colors"
          >
            Choose your path →
          </Link>
        </div>
        <div className="mt-10 flex items-center justify-center gap-8 text-sm text-gray-500">
          <div><span className="font-bold text-gray-900 text-2xl">{pathCount ?? "—"}</span><br />Launch tracks</div>
          <div className="w-px h-10 bg-gray-200" />
          <div><span className="font-bold text-gray-900 text-2xl">{categoryCount ?? "—"}</span><br />Learning domains</div>
          <div className="w-px h-10 bg-gray-200" />
          <div><span className="font-bold text-gray-900 text-2xl">1hr</span><br />Daily class</div>
        </div>
      </section>

      {/* How it works */}
      <section>
        <h2 className="text-2xl font-bold text-center mb-8">How PySchool works</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { step: "1", title: "Pick a purpose", desc: "Choose an authored launch track for web development, data science, or AI research." },
            { step: "2", title: "Get placed", desc: "A placement check finds a transparent starting milestone and weak topics." },
            { step: "3", title: "Attend class", desc: "Work through a daily 1-hour lesson with a clear objective, code and practice." },
            { step: "4", title: "Prove progress", desc: "Pass the safe coding rubric, then complete the milestone and return for review." },
          ].map((card) => (
            <div key={card.step} className="border border-gray-200 rounded-2xl p-6 hover:border-gray-400 transition-colors">
              <div className="w-10 h-10 rounded-full bg-gray-100 border border-gray-200 grid place-items-center font-bold mb-4">
                {card.step}
              </div>
              <h3 className="font-semibold text-lg mb-1">{card.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{card.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
