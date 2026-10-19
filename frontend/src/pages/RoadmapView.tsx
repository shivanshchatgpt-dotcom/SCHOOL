import { Link, useParams } from "react-router-dom";
import { ROADMAP_CATS } from "../lib/roadmaps";

function titleFor(slug: string) {
  for (const cat of ROADMAP_CATS) {
    const hit = cat.items.find((i) => i.slug === slug);
    if (hit) return hit.title;
  }
  return slug;
}

export default function RoadmapView() {
  const { slug = "" } = useParams();
  const title = titleFor(slug);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-700 hover:border-gray-900 hover:text-black transition-colors"
        >
          <span aria-hidden="true">←</span> Back
        </Link>
        <h1 className="truncate text-lg font-black tracking-tight">{title}</h1>
      </div>

      <iframe
        title={`${title} roadmap`}
        src={`/roadmaps/${slug}-roadmap.html`}
        className="h-[calc(100vh-11rem)] w-full rounded-2xl border border-gray-200 bg-white"
      />
    </div>
  );
}
