import CategoryGallery from "./CategoryGallery";

export function generateStaticParams() {
  return [
    { slug: "animal" },
    { slug: "food" },
    { slug: "vintage" },
    { slug: "technology" },
    { slug: "transport" },
    { slug: "sport" },
  ];
}

export default async function CategoryPage({ params }) {
  const { slug } = await params;
  return <CategoryGallery slug={slug} />;
}
