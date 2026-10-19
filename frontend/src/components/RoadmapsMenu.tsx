import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ROADMAP_CATS, ROADMAP_COUNT } from "../lib/roadmaps";

const roadmapHref = (slug: string) => `/roadmaps/${slug}`;

export default function RoadmapsMenu() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    return ROADMAP_CATS.map((cat) => ({
      ...cat,
      items: q
        ? cat.items.filter(
            (i) =>
              i.title.toLowerCase().includes(q) ||
              i.slug.includes(q) ||
              cat.label.toLowerCase().includes(q),
          )
        : cat.items,
    })).filter((cat) => cat.items.length > 0);
  }, [query]);

  const shown = useMemo(
    () => groups.reduce((n, cat) => n + cat.items.length, 0),
    [groups],
  );

  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Open all roadmaps"
        className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 hover:border-gray-900 hover:text-black transition-colors"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z" />
          <path d="M9 4v14M15 6v14" />
        </svg>
        <span>Roadmaps</span>
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <aside className="relative z-10 flex h-full w-full max-w-md flex-col bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
              <div>
                <h2 className="text-lg font-black tracking-tight">All Roadmaps</h2>
                <p className="text-xs text-gray-500">
                  {ROADMAP_COUNT} learning roadmaps inside PySchool
                </p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close roadmaps"
                className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-black"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="border-b border-gray-100 px-5 py-3">
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search roadmaps…"
                className="w-full rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
              />
            </div>

            <div className="flex-1 overflow-y-auto px-3 py-3">
              {groups.map((cat) => (
                <section key={cat.label} className="mb-4">
                  <div className="sticky top-0 z-10 bg-white px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-gray-400">
                    {cat.icon} {cat.label}
                  </div>
                  <ul className="mt-1 space-y-0.5">
                    {cat.items.map((item) => (
                      <li key={item.slug}>
                        <Link
                          to={roadmapHref(item.slug)}
                          onClick={() => setOpen(false)}
                          className="group flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-sm hover:bg-gray-100"
                        >
                          <span className="font-medium text-gray-800 group-hover:text-black">
                            {item.title}
                          </span>
                          <span className="shrink-0 text-gray-300 group-hover:text-gray-600 transition-transform group-hover:translate-x-0.5">
                            →
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}

              {shown === 0 && (
                <p className="px-2 py-10 text-center text-sm text-gray-400">
                  No roadmap matches “{query}”.
                </p>
              )}
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
