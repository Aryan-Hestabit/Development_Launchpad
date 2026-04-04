export default function FeatureCard({ title, description }) {
  return (
    <div className="bg-gray-100 p-6 rounded-lg transition hover:shadow-md">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-gray-600">{description}</p>
    </div>
  );
}
