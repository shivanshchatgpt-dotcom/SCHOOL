import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

interface PathItem {
  id: number;
  name: string;
  description: string;
  libraries: string;
  slug: string;
  difficulty: number;
  category_id: number;
  category_name: string;
  category_icon: string;
  assessment_count: number;
  duration_days: number;
}

interface Category {
  id: number;
  name: string;
  icon: string;
  depth_label: string;
  sort_order: number;
}

const difficultyDots = (level: number) => "●".repeat(level) + "○".repeat(Math.max(0, 5 - level));

export default function Paths() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [paths, setPaths] = useState<PathItem[]>([]);
  const [activeCategory, setActiveCategory] = useState<number | "all">("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params: { category_id?: number; q?: string } = {};
    if (activeCategory !== "all") params.category_id = activeCategory;
    if (query.trim()) params.q = query.trim();
    api.paths(params)
      .then((data) => setPaths(data))
      .catch(() => setPaths([]))
      .finally(() => setLoading(false));
  }, [activeCategory, query]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black tracking-tight">Career Paths</h1>
          <p className="text-gray-500 mt-1">
            Start with one of the three fully authored foundation tracks.
          </p>
        </div>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search paths, libraries…"
          className="w-full md:w-72 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
        />
      </div>

      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setActiveCategory("all")}
          className={`px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-colors ${
            activeCategory === "all"
              ? "bg-black text-white border-black"
              : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
          }`}
        >
          All ({paths.length})
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-colors ${
              activeCategory === cat.id
                ? "bg-black text-white border-black"
                : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
            }`}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Loading paths…</div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {paths.map((path) => (
            <Link
              key={path.id}
              to={`/paths/${path.slug}/assessment`}
              className="group border border-gray-200 rounded-2xl p-5 hover:border-gray-900 hover:shadow-sm transition-all"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-2xl">{path.category_icon}</span>
                <span className="text-xs text-gray-400">{path.duration_days}-day foundation</span>
              </div>
              <h3 className="font-bold text-lg mt-3 group-hover:underline">{path.name}</h3>
              <p className="text-sm text-gray-500 mt-1 line-clamp-2">{path.description}</p>
              <div className="flex items-center justify-between mt-4">
                <span className="text-xs text-gray-400">{path.libraries}</span>
                <span className="text-xs tracking-tighter text-gray-400" title={`Difficulty ${path.difficulty}/5`}>
                  {difficultyDots(path.difficulty)}
                </span>
              </div>
              <div className="mt-3 text-sm font-semibold text-gray-900 inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                Take the {path.assessment_count}-question placement check →
              </div>
            </Link>
          ))}
        </div>
      )}

      {!loading && paths.length === 0 && (
        <div className="text-center py-16 text-gray-400">No paths found for "{query}".</div>
      )}
      <p className="text-center text-sm text-gray-400">
        A wider future catalog is planned; paths appear here only when their curriculum is published.
      </p>
    </div>
  );
}
