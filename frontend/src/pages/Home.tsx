import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api";

export default function Home() {
  const [pathCount, setPathCount] = useState<number | null>(null);
  const [categoryCount, setCategoryCount] = useState<number | null>(null);

  useEffect(() => {
    api.paths().then((paths) => setPathCount(paths.length)).catch(() => setPathCount(0));
    api.categories().then((cats) => setCategoryCount(cats.length)).catch(() => setCategoryCount(0));
  }, []);

  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="py-16 text-center">
        <h1 className="text-5xl md:text-6xl font-black tracking-tight text-gray-900">
          Stop wandering.
          <br />
          <span className="text-gray-400">Start belonging to a school.</span>
        </h1>
        <p className="mx-auto max-w-2xl mt-6 text-lg text-gray-600 leading-relaxed">
          There are thousands of free Python resources — and that's the problem.
          PySchool is the only school that asks you{" "}
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
          <div><span className="font-bold text-gray-900 text-2xl">{pathCount ?? "—"}</span><br />Career paths</div>
          <div className="w-px h-10 bg-gray-200" />
          <div><span className="font-bold text-gray-900 text-2xl">{categoryCount ?? "—"}</span><br />Depth categories</div>
          <div className="w-px h-10 bg-gray-200" />
          <div><span className="font-bold text-gray-900 text-2xl">1hr</span><br />Daily class</div>
        </div>
      </section>

      {/* How it works */}
      <section>
        <h2 className="text-2xl font-bold text-center mb-8">How PySchool works</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { step: "1", title: "Pick a purpose", desc: "100+ paths — from web dev to AI research. You tell us why you're learning Python." },
            { step: "2", title: "Get tested", desc: "A short adaptive assessment judges whether you're Beginner, Intermediate or Advanced." },
            { step: "3", title: "Attend class", desc: "A daily 1-hour lesson built for your exact path and level — theory, code, practice." },
            { step: "4", title: "Submit homework", desc: "Homework every day. Skip it and the school gives you more. Just like real school." },
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
